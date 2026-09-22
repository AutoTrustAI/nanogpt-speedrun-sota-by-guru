#!/usr/bin/env python3
"""Run one archived ForgeMatch strategy on eight H100 GPUs, preserving evidence.

The default is 652 steps. --dry-run needs only Python's standard library and
never imports torch, queries GPUs, creates directories, or starts training.
"""
import argparse
import datetime
import json
import math
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import struct
import subprocess
import sys
import time

from verify_source import ROOT, sha256, verify

VAL = re.compile(r"\bstep:\s*(\d+)/(\d+)\s+val_loss:\s*(\S+)\s+train_time:\s*(\S+)ms(?:\s|$)")
FA3_REVISION = "64c1e6d1f2780e7931839f41426ddcdb564a7cb9"
CLEAR_NAMES = {
    "TRAIN_SEED", "SEED", "RANDOM_SEED", "PYTHONHASHSEED", "DATA_PATH",
    "NUM_EXTENSION_ITERATIONS", "NUM_SCHEDULED_ITERATIONS", "NUM_ITERATIONS",
    "MAX_STEPS", "TRAIN_STEPS", "TRAINING_STEPS", "BATCH_SIZE", "SEQ_LEN",
    "QK_HEAD_DIM", "DISABLE_FP8", "LOCAL_KERNELS", "PYTHONPATH", "PYTHONHOME",
    "PYTHONSTARTUP", "PYTHONOPTIMIZE", "PROFILE", "PROFILING", "ENABLE_PROFILING",
    "CUDA_PROFILE", "CUDA_PROFILE_CONFIG", "CUDA_PROFILE_LOG", "CUDA_PROFILE_CSV",
    "CUDA_INJECTION64_PATH", "NVTX_INJECTION64_PATH", "RANK", "LOCAL_RANK",
    "WORLD_SIZE", "LOCAL_WORLD_SIZE", "GROUP_RANK", "ROLE_RANK", "ROLE_WORLD_SIZE",
    "MASTER_ADDR", "MASTER_PORT", "PYTORCH_ALLOC_CONF", "PYTORCH_CUDA_ALLOC_CONF",
    "MKL_NUM_THREADS", "TORCH_COMPILE_DEBUG", "TORCH_LOGS", "TORCHDYNAMO_VERBOSE",
}
CLEAR_PREFIXES = ("KX_", "HYBRID_", "RETRIEVAL_", "PROFILE_", "NSYS_", "NCU_",
                  "TORCH_PROFILER_", "TORCHELASTIC_", "TORCHINDUCTOR_", "TRITON_")
RECORD_NAMES = ("CXX", "LD_LIBRARY_PATH", "CUDA_HOME", "CUDA_VISIBLE_DEVICES",
                "CUDA_MODULE_LOADING", "LOCAL_KERNELS", "KX_SEED", "HYBRID_TOTAL_STEPS",
                "HYBRID_CPU_AFFINITY", "OMP_NUM_THREADS", "RAYON_NUM_THREADS",
                "PYTHONUNBUFFERED", "TORCHINDUCTOR_CACHE_DIR", "TRITON_CACHE_DIR",
                "NCCL_DEBUG", "NCCL_ALGO", "NCCL_PROTO", "NCCL_P2P_DISABLE",
                "NCCL_IB_DISABLE", "NCCL_SOCKET_IFNAME", "NCCL_LAUNCH_ORDER_IMPLICIT",
                "NCCL_NVLS_ENABLE", "NCCL_COLLNET_ENABLE")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def parse_validation(line):
    match = VAL.search(line)
    if match is None:
        return None
    step, total, loss, milliseconds = match.groups()
    loss, seconds = float(loss), float(milliseconds) / 1000
    if not math.isfinite(loss) or loss < 0 or not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Invalid validation loss/time")
    return {"step": int(step), "total_steps": int(total), "val_loss": loss,
            "train_seconds": seconds}


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, choices=(652, 656), default=652)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data-dir", type=Path, required=True,
                        help="Directory containing all 103 train shards and one validation shard")
    parser.add_argument("--output-dir", type=Path, required=True, help="New, nonexistent run directory")
    parser.add_argument("--cache-dir", type=Path, required=True, help="New, nonexistent compilation cache directory")
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="Training venv interpreter")
    parser.add_argument("--kernel-dir", type=Path,
                        help="Pinned FA3 torch-stable-abi29-cu128-x86_64-linux build directory")
    parser.add_argument("--cuda-runtime-dir", type=Path, help="Directory containing libcudart.so.13")
    parser.add_argument("--cxx", default="g++-12")
    parser.add_argument("--lock-file", type=Path, default=Path("/tmp/forgematch-gpu.lock"),
                        help="Use the same lock file for every cooperating experiment on this host")
    parser.add_argument("--timeout-seconds", type=float, default=1800)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not 0 < args.seed < 2**32:
        parser.error("--seed must be in [1, 2**32); seed zero disables native seeding")
    if not math.isfinite(args.timeout_seconds) or args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive and finite")
    # Do not resolve the venv Python symlink: it must retain its venv identity.
    args.python = args.python.expanduser().absolute()
    for name in ("data_dir", "output_dir", "cache_dir", "lock_file", "kernel_dir", "cuda_runtime_dir"):
        value = getattr(args, name)
        if value is not None:
            if name in ("output_dir", "cache_dir") and (value.expanduser().exists() or value.expanduser().is_symlink()):
                parser.error(f"Refusing to reuse an existing output/cache path: {value}")
            setattr(args, name, value.expanduser().resolve())
    for path in (args.output_dir, args.cache_dir):
        if path.exists() or path.is_symlink():
            parser.error(f"Refusing to reuse an existing output/cache path: {path}")
        if path.is_relative_to(ROOT / "model") or path.is_relative_to(args.data_dir):
            parser.error("Output/cache paths cannot be inside model source or dataset directories")
        if args.data_dir.is_relative_to(path):
            parser.error("Output/cache paths cannot contain the dataset directory")
    if args.output_dir.is_relative_to(args.cache_dir) or args.cache_dir.is_relative_to(args.output_dir):
        parser.error("Output/cache paths must be distinct and cannot contain one another")
    return args


def environment(args):
    env = os.environ.copy()
    removed = sorted(name for name in env if name in CLEAR_NAMES or name.startswith(CLEAR_PREFIXES))
    for name in removed:
        env.pop(name)
    env.update(KX_SEED=str(args.seed), HYBRID_TOTAL_STEPS=str(args.steps),
               HYBRID_CPU_AFFINITY="physical", OMP_NUM_THREADS="1", RAYON_NUM_THREADS="4",
               PYTHONUNBUFFERED="1", CXX=args.cxx,
               TORCHINDUCTOR_CACHE_DIR=str(args.cache_dir / "inductor"),
               TRITON_CACHE_DIR=str(args.cache_dir / "triton"))
    env["PATH"] = str(args.python.parent) + os.pathsep + env.get("PATH", "")
    if args.kernel_dir is not None:
        env["LOCAL_KERNELS"] = "devenpzak/flash-attn3-12864=" + str(args.kernel_dir)
    if args.cuda_runtime_dir is not None:
        env["LD_LIBRARY_PATH"] = str(args.cuda_runtime_dir) + (
            os.pathsep + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    return env, removed


def dataset_inventory(directory):
    expected = {f"fineweb_train_{index:06d}.bin" for index in range(1, 104)}
    expected.add("fineweb_val_000000.bin")
    actual = {p.name for p in directory.glob("fineweb_*.bin")}
    if actual != expected:
        raise ValueError(f"Expected exactly 103 train shards and one validation shard; "
                         f"missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    inventory = {}
    for name in sorted(expected):
        path = directory / name
        with path.open("rb") as stream:
            header = stream.read(1024)
        if len(header) != 1024:
            raise ValueError(f"Truncated shard header: {name}")
        magic, version, tokens = struct.unpack_from("<iii", header)
        if (magic, version) != (20240520, 1) or tokens <= 0 or path.stat().st_size != 1024 + 2 * tokens:
            raise ValueError(f"Invalid FineWeb shard header/size: {name}")
        if name.startswith("fineweb_val_") and tokens < 10_485_761:
            raise ValueError("Validation shard does not cover the complete 10,485,760-token evaluation")
        inventory[name] = {"tokens": tokens, "size_bytes": path.stat().st_size,
                           "mtime_ns": path.stat().st_mtime_ns}
    return inventory


def hardware_preflight():
    if sys.platform != "linux" or not hasattr(os, "sched_getaffinity"):
        raise RuntimeError("Actual training requires Linux and the documented CPU topology")
    if not set(range(104)) <= os.sched_getaffinity(0):
        raise RuntimeError("CPU affinity must allow all physical CPU IDs 0 through 103")
    for cpu in range(104):
        if not Path(f"/sys/devices/system/node/node{cpu // 52}/cpu{cpu}").exists():
            raise RuntimeError("CPU NUMA numbering differs from the archived affinity mapping")
    query = ["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version,power.limit", "--format=csv,noheader"]
    devices = subprocess.check_output(query, text=True, timeout=15).strip().splitlines()
    if len(devices) != 8 or any("H100" not in row for row in devices):
        raise RuntimeError("The measured setup requires exactly eight H100 GPUs")
    active = subprocess.check_output(["nvidia-smi", "--query-compute-apps=pid,process_name",
                                      "--format=csv,noheader"], text=True, timeout=15).strip()
    if active:
        raise RuntimeError("GPU compute processes are already active; run after they finish")
    return {"gpu_query": devices, "cpu_query": subprocess.check_output(["lscpu", "--json"], text=True)}


def collect(command, cwd, env, path, timeout, on_line):
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    started = time.monotonic()
    timeout_at = None
    buffered = b""
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)

    def stop(sig):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass

    try:
        with path.open("xb") as console:
            while selector.get_map() or process.poll() is None:
                elapsed = time.monotonic() - started
                if timeout_at is None and elapsed >= timeout:
                    timeout_at = elapsed
                    stop(signal.SIGTERM)
                if timeout_at is not None and elapsed - timeout_at >= 10:
                    stop(signal.SIGKILL)
                for key, _ in selector.select(timeout=0.2):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    console.write(chunk)
                    console.flush()
                    buffered += chunk
                    while b"\n" in buffered:
                        line, buffered = buffered.split(b"\n", 1)
                        on_line(line.decode(errors="replace").rstrip("\r"))
            if buffered:
                on_line(buffered.decode(errors="replace"))
        return process.wait(), timeout_at is not None, time.monotonic() - started
    except BaseException:
        stop(signal.SIGKILL)
        process.wait()
        raise
    finally:
        selector.close()
        process.stdout.close()


def main(argv=None):
    args = arguments(argv)
    manifest_path = ROOT / "provenance/source-files.json"
    manifest = json.loads(manifest_path.read_text())
    source_hashes = verify(manifest=manifest)
    source = args.output_dir / "source"
    command = [str(args.python), "-m", "torch.distributed.run", "--standalone", "--nproc_per_node=8", "train_gpt.py"]
    env, removed = environment(args)
    result = {"strategy": "ForgeMatch", "status": "dry_run" if args.dry_run else "preflight",
              "created_utc": utc(), "steps": args.steps, "seed": args.seed,
              "source_commit": manifest["source_commit"], "source_sha256": source_hashes,
              "command": command, "cwd": str(source), "data_dir": str(args.data_dir),
              "cache_dir": str(args.cache_dir), "fa3_revision": FA3_REVISION,
              "effective_environment": {name: env.get(name) for name in RECORD_NAMES},
              "cleared_environment_names": removed, "timeout_seconds": args.timeout_seconds,
              "validations": [], "completion_errors": []}
    if args.dry_run:
        result["skipped_checks"] = ["dataset", "runtime dependencies", "hardware", "free cache capacity"]
        print(json.dumps(result, indent=2))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=False)
    result_path = args.output_dir / "result.json"

    def save():
        write_json(result_path, result)

    def on_line(line):
        try:
            validation = parse_validation(line)
            if validation is not None:
                result["validations"].append(validation)
                print(line, flush=True)
                save()
            elif "val_loss:" in line and "step:" in line:
                result["completion_errors"].append("unrecognized_validation_line")
        except (ValueError, OverflowError):
            result["completion_errors"].append("invalid_validation_line")

    try:
        save()
        if not args.python.is_file() or not os.access(args.python, os.X_OK):
            raise RuntimeError("Training Python is not executable")
        result["dataset"] = dataset_inventory(args.data_dir)
        if args.cuda_runtime_dir is not None and not (args.cuda_runtime_dir / "libcudart.so.13").is_file():
            raise RuntimeError("--cuda-runtime-dir has no libcudart.so.13")
        if args.kernel_dir is not None:
            if not args.kernel_dir.is_dir() or not list(args.kernel_dir.glob("_flash_attn3_cuda_*.so")):
                raise RuntimeError("--kernel-dir is not the FA3 build directory")
            result["local_kernel_sha256"] = {str(path.relative_to(args.kernel_dir)): sha256(path)
                                             for path in sorted(args.kernel_dir.rglob("*"))
                                             if path.is_file() and path.suffix in (".py", ".so")}
        source.mkdir()
        for name in source_hashes:
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "model" / name, target)
        verify(source, manifest)
        (source / "data/fineweb10B").symlink_to(args.data_dir, target_is_directory=True)
        shutil.copy2(manifest_path, args.output_dir / "source-manifest.json")
        for name in ("run_benchmark.py", "verify_source.py"):
            shutil.copy2(Path(__file__).parent / name, args.output_dir / name)
        result["wrapper_sha256"] = {name: sha256(args.output_dir / name)
                                   for name in ("run_benchmark.py", "verify_source.py")}
        args.cache_dir.mkdir(parents=True, exist_ok=False)
        filesystem = os.statvfs(args.cache_dir)
        result["cache_capacity_before"] = {"available_bytes": filesystem.f_bavail * filesystem.f_frsize,
                                            "available_inodes": filesystem.f_favail}
        if filesystem.f_bavail * filesystem.f_frsize < 20 * 1024**3 or filesystem.f_favail < 70_000:
            raise RuntimeError("A fresh run needs at least 20 GiB and 70,000 available cache inodes")
        import fcntl
        args.lock_file.parent.mkdir(parents=True, exist_ok=True)
        with args.lock_file.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result["hardware"] = hardware_preflight()
            result["status"] = "running"
            save()
            code, timed_out, wall = collect(command, source, env, args.output_dir / "console.log",
                                             args.timeout_seconds, on_line)
        result.update(exit_code=code, timed_out=timed_out, wall_seconds=wall)
        final = result["validations"][-1] if result["validations"] else {}
        if final.get("step") != args.steps or final.get("total_steps") != args.steps or final.get("train_seconds", 0) <= 0:
            result["completion_errors"].append("missing_or_wrong_final_validation")
        native = []
        for path in sorted((source / "logs").glob("*.txt")):
            values = [value for line in path.read_text(errors="replace").splitlines()
                      if (value := parse_validation(line)) is not None]
            native.append({"path": str(path.relative_to(args.output_dir)), "sha256": sha256(path),
                           "validations": values, "last_validation": values[-1] if values else None})
        result["native_logs"] = native
        if len(native) != 1 or native[0]["validations"] != result["validations"]:
            result["completion_errors"].append("native_log_validation_sequence_mismatch")
        result["final_validation"] = final
        result["quality_pass"] = bool(final) and final.get("val_loss", math.inf) <= 3.28
        result["status"] = "timeout" if timed_out else (
            "completed" if code == 0 and not result["completion_errors"] else "failed")
    except KeyboardInterrupt:
        result.update(status="interrupted", error="KeyboardInterrupt or termination signal")
    except Exception as exc:
        result.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    finally:
        try:
            verify(source, manifest)
            result["source_after_matches_before"] = True
        except (OSError, ValueError) as exc:
            result["source_after_matches_before"] = False
            result["source_verification_error"] = str(exc)
            if result["status"] == "completed":
                result["status"] = "failed"
        if (args.output_dir / "console.log").is_file():
            result["console_sha256"] = sha256(args.output_dir / "console.log")
        result["completed_utc"] = utc()
        save()
    print(f"{result['status']}: {result_path}", flush=True)
    return 0 if result["status"] == "completed" and result.get("quality_pass") else 1


if __name__ == "__main__":
    def terminate(_signum, _frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, terminate)
    raise SystemExit(main())
