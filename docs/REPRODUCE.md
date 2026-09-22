# Reproducing ForgeMatch

The default strategy is **652 steps**, with `KX_SEED=42`. The frozen model files
also support the previous **656-step** comparison. The five recorded 652-step
runs achieved a mean training time of **24.8998 s**, a **0.071 s** time range, and
all five final losses at or below **3.28**. The result tables and evidence in
this repository cover the complete cohort.

The model under `model/` is the exact 33-file source inventory from commit
`d7b6a09512010189292974b3a9b9f19c111d9b38`. The reported GPU measurements used
the original archived orchestration with these model bytes. Validation of the
packaged portable wrapper covers CPU checks and dry-run execution.

## Get the source

Clone the repository from the **AutoTrustAI** organization:

```sh
git clone https://github.com/AutoTrustAI/forgematch-nanogpt.git
cd forgematch-nanogpt
```

Run the setup and launch commands below from this repository directory.

## Hardware and runtime

The measurements used a single Linux host with eight NVIDIA H100 80 GB GPUs,
700 W power limits, two Intel Xeon Platinum 8481C CPUs, 104 physical cores / 208
logical CPUs, approximately 1.8 TiB RAM, and no swap. GPU 0–3 are on NUMA node 0;
GPU 4–7 are on node 1. CPU IDs 0–51 are the physical cores of node 0, and 52–103
are the physical cores of node 1. The archived `runtime_affinity.py` binds each
rank to 13 consecutive physical cores before importing torch.

**This affinity mapping requires that exact CPU numbering and GPU ordering.**
On another machine, first check
`lscpu -e=CPU,CORE,SOCKET,NODE`, `nvidia-smi topo -m`, and the process CPU mask.
A different mapping needs a separately documented source variant. Use an
otherwise idle machine and the same cooperative lock file for every experiment.
The wrapper takes that lock and checks for active GPU compute jobs before launch.

Recorded software: Python 3.12.14, PyTorch 2.10.0+cu128, Triton 3.6.0,
`kernels==0.16.1`, NVIDIA driver 580.178.04, and g++ 12. Use a CUDA 13-capable
driver/runtime environment: the selected FA3 binary links to `libcudart.so.13`
even though PyTorch uses its cu128 build.

From the repository root, with Python 3.12, Rust/Cargo and g++ 12 installed:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128
.venv/bin/python -m pip install -r model/requirements.txt
.venv/bin/python -m pip install 'maturin>=1.9,<2'
.venv/bin/python -m maturin build --release --locked --manifest-path model/exact_match/Cargo.toml --interpreter .venv/bin/python --out wheels
.venv/bin/python -m pip install wheels/exact_match-*.whl
.venv/bin/python scripts/verify_source.py
```

The Rust build uses `model/exact_match/Cargo.lock`. Build artifacts and downloaded
data do not change the 33 pinned source files. Avoid `python -O`: the trainer's
assertions are part of its correctness checks. The archived header and upstream
README describe earlier launch defaults; use this document and the wrapper for
the actual ForgeMatch settings.

## Pinned FA3 kernel and CUDA runtime

The trainer loads `devenpzak/flash-attn3-12864` at immutable revision
`64c1e6d1f2780e7931839f41426ddcdb564a7cb9`. It supplies the asymmetric head
dimensions required by this model. Do not substitute another flash-attention
package. The original runs mapped the downloaded kernel build using
`LOCAL_KERNELS`; the wrapper exposes the same mapping through `--kernel-dir`.

Download the pinned revision and a CUDA 13 runtime into local directories:

```bash
.venv/bin/hf download devenpzak/flash-attn3-12864 \
  --revision 64c1e6d1f2780e7931839f41426ddcdb564a7cb9 \
  --local-dir runtime/flash-attn3-12864
.venv/bin/python -m pip install --no-deps --target runtime/cuda13 nvidia-cuda-runtime==13.1.80
```

Check that `runtime/cuda13/nvidia/cu13/lib/libcudart.so.13` exists. If the runtime
is already supplied by your system image, point `--cuda-runtime-dir` to its
directory instead and record that runtime version. Version 13.1.80 matches the
separately installed runtime from our measurements. The wrapper
records hashes of the selected local FA3 Python and shared-library files.

The build path passed below must contain `_flash_attn3_cuda_*.so`; passing the
Hugging Face snapshot root is insufficient. Omitting `--kernel-dir` lets
`kernels.get_kernel` download the same source-pinned revision, but the explicit
local mapping follows our measured setup more closely.

## Full FineWeb10B dataset

Download **all 103 training shards and the one validation shard** from
[`kjj0/fineweb10B-gpt2`](https://huggingface.co/datasets/kjj0/fineweb10B-gpt2):

```bash
.venv/bin/python model/data/cached_fineweb10B.py 103
```

The files are placed at `model/data/fineweb10B/` (about 20.7 GB). You can move the
whole directory to a data volume and pass that absolute directory to
`--data-dir`. It must directly contain `fineweb_train_000001.bin` through
`fineweb_train_000103.bin`, plus `fineweb_val_000000.bin`. The wrapper checks all
104 filenames, the FineWeb headers and file lengths. Obtain the exact GPT-2
token shards from the linked dataset.

The neural network consumes the strategy's shorter scheduled token stream;
the offline exact-match table indexes **all 103 training shards**. Supplying
only enough shards for neural-network training changes the method. Evaluation
uses the full 10,485,760-token validation slice. Validation targets are not used
to build the training retrieval index. See [Rules, data, and timing](COMPLIANCE.md)
for the benchmark protocol.

## Run one seed

Choose persistent output storage and a fresh compilation-cache directory on a
fast local filesystem. The launch gate requires at least 20 GiB and 70,000 free
cache inodes per run. Five fresh runs need the corresponding aggregate capacity. Check both
`df -h` and `df -i`: a filesystem can run out of inodes with many GB free. Verify
that intended data/cache volumes are actually mounted before launching.

First inspect a launch without importing torch, querying GPUs, or creating
files. The dataset and runtime paths may be placeholders during dry-run:

```bash
.venv/bin/python scripts/run_benchmark.py \
  --steps 652 --seed 42 \
  --data-dir model/data/fineweb10B \
  --output-dir runs/forgematch652-s42-v1 \
  --cache-dir cache/forgematch652-s42-v1 \
  --kernel-dir runtime/flash-attn3-12864/build/torch-stable-abi29-cu128-x86_64-linux \
  --cuda-runtime-dir runtime/cuda13/nvidia/cu13/lib \
  --dry-run
```

Remove `--dry-run` to launch. Run the wrapper in a durable terminal session
(for example, tmux) and leave it running until it prints a terminal result.
Compilation/warmup can take roughly seven minutes even though the scored
training section is about 25 seconds. The default total subprocess timeout is
1,800 seconds and includes compilation and evaluation; adjust
`--timeout-seconds` explicitly if needed and retain the failed attempt.

The effective training command, executed inside the run's frozen `source/`, is:

```bash
python -m torch.distributed.run --standalone --nproc_per_node=8 train_gpt.py
```

The wrapper sets:

| Setting | Value |
| --- | --- |
| `KX_SEED` | Explicit positive `--seed`, default 42 |
| `HYBRID_TOTAL_STEPS` | 652 by default; 656 for the prior strategy |
| `HYBRID_CPU_AFFINITY` | `physical` |
| `OMP_NUM_THREADS` | `1` |
| `RAYON_NUM_THREADS` | `4` |
| `TORCHINDUCTOR_CACHE_DIR` | New cache directory's `inductor/` |
| `TRITON_CACHE_DIR` | New cache directory's `triton/` |
| `LOCAL_KERNELS` | Pinned FA3 local build mapping when `--kernel-dir` is supplied |

It clears inherited strategy, seed, profiling and Inductor/Triton overrides,
then sets the settings above. It adds no Inductor tuning flags. The trainer
itself retains its original allocator and compiler configuration. Other runtime
settings, including relevant NCCL options and CUDA visibility, are inherited
and recorded via a small allowlist. Launch from the normal eight-GPU ordering;
avoid remapping `CUDA_VISIBLE_DEVICES` because the CPU mapping assumes that
ordering. The wrapper never dumps the complete environment or access tokens.

The wrapper copies the 33 verified files to `runs/<name>/source/`, adds
`source/data/fineweb10B` as a symlink to the selected dataset, and runs there with
`DATA_PATH` unset. This satisfies the trainer's literal
`DATA_PATH/data/fineweb10B/...` convention, whose default `DATA_PATH` is `.`.
An existing output or cache directory is rejected rather than overwritten.

## Evidence and five-seed comparisons

Each run retains:

- `result.json`: strategy, seed, steps, command, selected environment, hardware,
  dataset header inventory, timing, loss, process status, and hashes;
- `console.log`: combined stdout and stderr, including failures;
- `source/`: the frozen source and native `source/logs/*.txt` trainer log;
- `source-manifest.json`, plus the wrapper and source-verifier snapshots.

Completion requires a clean subprocess exit, unchanged model-source hashes, the
requested final step, exactly one native log, and agreement between its complete
validation sequence and the console. Quality (`loss <= 3.28`) is recorded separately; a completed
quality failure returns a nonzero shell status and keeps its evidence. Interrupts,
timeouts and other failures also preserve the run directory. The wrapper does
not automatically retry or delete any attempt.

For a new five-seed cohort, preregister the fixed seeds **43, 42, 44, 45, 46** and
run them sequentially with unique output/cache paths. Retain every measured
time, including slow runs, and report all quality failures. A 652-step run
changes the whole learning schedule; never pool it with 656-step results.
Report the mean, minimum, maximum, range and every final loss. Our local target
was all five losses <= 3.28, mean scored training time <= 25 s, and time range
<= 5 s.

`train_seconds` is parsed from the trainer's **final scored `train_time`**, not
the wrapper's elapsed `wall_seconds`. The scorer excludes compilation, warmup
and evaluation according to the trainer's convention. Retrieval content reads,
index building and terminal synchronization/cleanup remain in the timed
training section; data-independent allocations and some setup happen before it.
