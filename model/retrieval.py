"""Next-token embeddings, the prefetching online cache, and the sharded validation cache."""
import os
import glob
import numpy as np
import torch
import torch.distributed as dist
from queue import Queue
from collections import deque
from contextlib import nullcontext
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
os.environ.setdefault("RAYON_NUM_THREADS", "4")
from exact_match import Cache

def merge_top2(keys, group=None):
    """Rank shard-local candidates by length/count/token, excluding duplicate tokens.

    Counts are shard-local, not exact global frequencies.
    """
    length = keys.max(1).values >> 40
    if group is not None:
        dist.all_reduce(length, op=dist.ReduceOp.MAX, group=group)
    keys = torch.where((keys >> 40) == length[:, None], keys, 0)
    ids = torch.full((len(keys), 4), -1, dtype=torch.int32)
    for i in range(2):
        best = keys.max(1).values
        if group is not None:
            dist.all_reduce(best, op=dist.ReduceOp.MAX, group=group)
        ids[:, i] = torch.where(best > 0, 0xFFFF - (best & 0xFFFF), -1)
        keys = torch.where((keys & 0xFFFF) == (best[:, None] & 0xFFFF), 0, keys)
    return length.numpy(), ids.numpy()

def retrieval_vector(model, length, candidates, device):
    to_device = lambda x: torch.as_tensor(x, device=device, dtype=torch.int64)
    length, ids = to_device(length), to_device(candidates)
    bucket = torch.bucketize(length, to_device([1, 24, 32, 48, 64, 128, 256]), right=True)
    valid = ids >= 0
    gathered = model.embed.weight[ids.clamp_min(0)].float()
    mean = (gathered * valid[..., None]).sum(1, dtype=torch.float32) / valid.sum(1, keepdim=True).clamp_min(1)
    values = mean * model.ret_next_scale[bucket, None] + model.ret_bucket_embed[bucket]
    return (values * (length > 0)[:, None]).bfloat16()

def _freeze_anvil_batch(batch):
    """Own ANVIL's host rings before its loader advances again.

    The first seven fields keep ANVIL's original ordering:
      GPU inputs, targets, cu_seqlens, ngrams; CPU ngrams, targets, inputs.
    Field eight is (query_inputs, real_document_bounds, insertion_group), where
    insertion_group is (immutable_shard_tokens, starts_by_rank, ends_by_rank).
    Query bounds are captured BEFORE ANVIL's virtual attention-cap splitting.
    """
    if len(batch) != 8 or batch[7] is None:
        raise ValueError("online retrieval needs ANVIL's seven fields plus retrieval metadata")
    owned = list(batch[:7])
    for index in (4, 5, 6):
        owned[index] = np.array(owned[index], copy=True, order="C")
    inputs, bounds, group = batch[7]
    inputs = np.array(inputs, dtype=np.int32, copy=True, order="C")
    bounds = np.array(bounds, dtype=np.int32, copy=True, order="C")
    if inputs.ndim != 1 or bounds.ndim != 1 or len(bounds) < 2:
        raise ValueError("retrieval inputs and document bounds must be one-dimensional")
    if bounds[0] != 0 or bounds[-1] != len(inputs) or np.any(bounds[1:] < bounds[:-1]):
        raise ValueError("retrieval bounds must cover the current input batch in order")
    if not np.array_equal(inputs, owned[6]):
        raise ValueError("retrieval metadata and ANVIL's current CPU inputs disagree")
    if group is None or len(group) != 3:
        raise ValueError("online insertion requires the current global training group")
    tokens, starts, ends = group
    # The shard is immutable and huge: retain its numpy view/base, never copy it.
    # The small span lists are owned so subsequent loader steps cannot mutate them.
    starts = tuple(tuple(int(x) for x in row) for row in starts)
    ends = tuple(tuple(int(x) for x in row) for row in ends)
    if len(starts) != len(ends) or not starts:
        raise ValueError("insertion group must have matching nonempty rank lists")
    for ss, ee in zip(starts, ends):
        if len(ss) != len(ee) or not ss:
            raise ValueError("insertion group must have matching nonempty document spans")
        if any(s < 0 or e <= s or e > len(tokens) for s, e in zip(ss, ee)):
            raise ValueError("insertion span lies outside its immutable training shard")
    return tuple(owned), inputs, bounds, (tokens, starts, ends)


# HYBRID_DEFERRED_INPUT_WAIT_V1
def wait_for_batch(batch):
    """Transfer a prefetched batch's CUDA ownership at its first real consumer.

    FIFO entries retain Python references to every producer tensor until use.
    After waiting, record_stream extends each allocation's lifetime through the
    consumer stream even when the FIFO later discards its last Python reference.
    CPU metadata may be read before this handoff; GPU batch fields may not.
    """
    if len(batch) != 9:
        raise ValueError("deferred retrieval batch must contain a readiness event")
    ready = batch[8]
    if ready is not None:
        consumer_stream = torch.cuda.current_stream(batch[0].device)
        consumer_stream.wait_event(ready)
        for tensor in (*batch[:4], *batch[7]):
            tensor.record_stream(consumer_stream)


class OnlineCache:
    """Exact-match's online semantics adapted to ANVIL's seven-field loader.

    A private worker drives the raw loader; all microbatches in one optimizer
    step query BEFORE any token from that step is inserted. The queue keeps the
    original depth of 16 steps. Owned CPU arrays protect ANVIL's small host rings.
    CUDA batches and matches travel on one producer stream, with an explicit
    event consumed on the caller's stream before yielding the original seven
    fields plus (match_lengths, candidate_ids). The caller copies matches into
    its own address-stable CUDA Graph buffers.
    """
    def __init__(self, min_context, capacity, depth=16):
        if depth <= 0:
            raise ValueError("retrieval prefetch depth must be positive")
        self.cache = Cache(min_context, 512)
        self.cache.reserve(capacity)
        self.depth = depth
        self.thread = None
        self.error = None

    def prefetch(self, loader, loader_args, steps, microbatches, device, *, defer_cuda_wait=False):
        if self.thread is not None:
            raise RuntimeError("online retrieval prefetch may only start once")
        if steps <= 0 or microbatches <= 0:
            raise ValueError("retrieval prefetch requires positive steps and microbatches")
        queue = Queue(self.depth * microbatches)
        is_cuda = torch.device(device).type == "cuda"

        def run():
            # Retain match-copy source buffers until DMA completes. Bound pending
            # H2D copies to eight raw batches before asking the loader for another:
            # this also protects its original >=16-slot pinned rings, independently
            # of the larger depth16 + ANVIL lookahead8 queue lifetime.
            pending = deque()
            try:
                if is_cuda:
                    torch.cuda.set_device(device)
                    producer_stream = torch.cuda.Stream(device=device)
                else:
                    producer_stream = None
                with torch.cuda.stream(producer_stream) if is_cuda else nullcontext():
                    prev = loader_args(0)
                    for step in range(steps):
                        args, groups = loader_args(step), []
                        for idx in range(microbatches):
                            while pending and pending[0][0].query():
                                pending.popleft()
                            if len(pending) >= 8:
                                pending.popleft()[0].synchronize()
                            raw = loader.send(args if idx == 0 and args != prev else None)
                            batch, inputs, bounds, group = _freeze_anvil_batch(raw)
                            result = self.cache.query(inputs, bounds)
                            host_matches = tuple(torch.from_numpy(x) for x in result)
                            if is_cuda:
                                host_matches = tuple(x.pin_memory() for x in host_matches)
                            matches = tuple(x.to(device, non_blocking=True) for x in host_matches)
                            if is_cuda:
                                ready = torch.cuda.Event()
                                ready.record(producer_stream)
                                pending.append((ready, host_matches))
                            else:
                                ready = None
                            queue.put(((*batch, matches), ready))
                            groups.append(group)
                        prev = args
                        if step == steps - 1:
                            break
                        # Upstream ordering: every microbatch was queried above;
                        # only now insert all ranks' current-step training tokens.
                        for tokens, starts, ends in groups:
                            for ss, ee in zip(starts, ends):
                                buf = np.concatenate([tokens[s:e] for s, e in zip(ss, ee)]).astype(np.int32)
                                bounds = np.minimum(np.cumsum([0] + [e-s for s, e in zip(ss, ee)]), len(buf)-1).astype(np.int32)
                                self.cache.insert(buf[:-1], buf[1:], bounds)
                    for ready, _sources in pending:
                        ready.synchronize()
                    pending.clear()
            except BaseException as exc:
                self.error = exc
                queue.put(exc)
                # Preserve async copy sources until their stream is finished even
                # on error. The first exception remains the reported failure.
                for ready, _sources in pending:
                    try:
                        ready.synchronize()
                    except BaseException:
                        pass

        self.thread = Thread(target=run, daemon=True, name="anvil-exact-prefetch")
        self.thread.start()
        for _ in range(steps * microbatches):
            item = queue.get()
            if isinstance(item, BaseException):
                raise item
            batch, ready = item
            if defer_cuda_wait:
                # CPU lookahead may inspect metadata without importing the future
                # batch's DMA dependency into the current training step's stream.
                yield (*batch, ready)
            else:
                if is_cuda:
                    consumer_stream = torch.cuda.current_stream(device)
                    consumer_stream.wait_event(ready)
                    for tensor in (*batch[:4], *batch[7]):
                        tensor.record_stream(consumer_stream)
                yield batch

    def finish(self):
        if self.thread is not None:
            self.thread.join()
        if self.error is not None:
            raise self.error

class ValidationCache:
    """Each rank indexes a slice of the training shards, queries the validation inputs against
    it, and the results are merged across ranks by (match length, mode count, smaller token)."""
    def __init__(self, train_pattern, val_pattern, min_context, local_tokens, total_tokens,
                 group=None, expected_shards=103):
        self.group = group
        self.local_tokens, self.total_tokens = local_tokens, total_tokens
        if total_tokens <= 0 or local_tokens <= 0 or total_tokens % local_tokens:
            raise ValueError("validation tokens must be a positive multiple of local_tokens")
        files = sorted(glob.glob(train_pattern))
        if len(files) != expected_shards:
            raise ValueError(f"expected {expected_shards} training shards, found {len(files)}")

        tokens_per_shard = 101_000_000
        self.training_token_capacity = len(files) * tokens_per_shard
        rank, world = (dist.get_rank(group), dist.get_world_size(group)) if group is not None else (0, 1)
        self.length = np.zeros(total_tokens, np.int32)
        self.next = np.full((total_tokens, 4), -1, np.int32)
        self.counts = np.zeros((total_tokens, 4), np.int32)
        self.status = torch.zeros(1, dtype=torch.int32)
        self.future = None
        self.ready = False
        val_files = sorted(glob.glob(val_pattern))
        if not val_files:
            raise ValueError("no validation shard")
        self.val_file = open(val_files[0], "rb")
        header = np.fromfile(self.val_file, dtype="<i4", count=256)
        if len(header) != 256 or tuple(header[:2]) != (20240520, 1) or header[2] < total_tokens + 1:
            self.val_file.close()
            raise ValueError("invalid or undersized validation shard")
        self.inputs = np.empty(total_tokens, dtype="<u2")
        try:
            local_files = files[rank::world]
            self.cache = Cache.allocate_offline(
                local_files, min_context, 512,
                token_capacity=len(local_files) * tokens_per_shard)
        except Exception:
            self.val_file.close()
            raise
        self.worker = ThreadPoolExecutor(max_workers=1)
        self.worker.submit(lambda: None).result()

    def start(self):
        if self.future is not None:
            raise RuntimeError("validation cache already started")
        self.future = self.worker.submit(self._build)

    def _build(self):
        error = None

        # Coordinate index release after every rank has finished querying.
        try:
            try:
                self.cache.build()
                if self.val_file.readinto(self.inputs) != self.inputs.nbytes:
                    raise ValueError("truncated validation shard")
                for offset in range(0, self.total_tokens, self.local_tokens):
                    end = offset + self.local_tokens
                    x = self.inputs[offset:end].astype(np.int32)
                    self.length[offset:end], candidates = self.cache.query(
                        x, np.array([0, len(x)], np.int32))
                    self.next[offset:end] = candidates[:, :4]
                    self.counts[offset:end] = candidates[:, 4:]
            except Exception as exc:
                error = exc
                self.status[0] = 1
            if self.group is not None:
                dist.all_reduce(self.status, op=dist.ReduceOp.MAX, group=self.group)
        finally:
            self.val_file.close()
            self.cache.release()
            del self.cache, self.inputs
        if self.status.item():
            raise RuntimeError("offline validation cache build failed") from error
        for offset in range(0, self.total_tokens, self.local_tokens):
            end = offset + self.local_tokens
            length = torch.from_numpy(self.length[offset:end]).long()
            ids = torch.from_numpy(self.next[offset:end]).long()
            counts = torch.from_numpy(self.counts[offset:end]).long()
            key = (length[:, None] << 40) | (counts.clamp(0, (1 << 24)-1) << 16) | (0xFFFF - ids.clamp_min(0))
            key *= (ids >= 0) & (length[:, None] > 0)
            self.length[offset:end], self.next[offset:end] = merge_top2(key, self.group)
        del self.counts
        self.ready = True

    def finish(self):
        if self.future is None:
            raise RuntimeError("validation cache has not been started")
        try:
            self.future.result()
        finally:
            self.worker.shutdown()

    def query(self, offset, batch):
        if not self.ready:
            raise RuntimeError("validation cache is not ready")
        end = offset + len(batch[0])
        if offset < 0 or end > self.total_tokens or offset % self.local_tokens or end-offset != self.local_tokens:
            raise ValueError("validation batch does not match cache layout")
        return self.length[offset:end], self.next[offset:end]
