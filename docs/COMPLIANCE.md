# Rules, data, and timing

This document records the benchmark protocol reviewed on **2026-09-22 UTC / 2026-09-23 Asia/Shanghai**, against upstream master `bc3a0c2d640d0d73dedaef87eae26148d2e32afb`. See the [official rules](https://github.com/KellerJordan/modded-nanogpt#rules).

## Benchmark requirements

The main track uses 8×H100 and the fixed underlying FineWeb train/validation token streams. The target is mean validation cross-entropy ≤3.28 on the complete **10,485,760-token** validation target. Learning-method changes require log-backed statistical evidence with **p<0.01**; the rules prohibit additional Inductor/compile tuning flags and require a speed comparison with the preceding record on the same hardware. Readability and the treatment of loss margin remain subject to maintainer judgment. See the [rules](https://github.com/KellerJordan/modded-nanogpt#rules) and [target-metric discussion](https://github.com/KellerJordan/modded-nanogpt#comment-on-the-target-metric).

Our local target uses the fixed seeds **43, 42, 44, 45, 46**: each final loss ≤3.28, mean time ≤25 s, and time range ≤5 s. The complete 652-step cohort satisfies those conditions. Its mean loss is **3.27498**, worst loss **3.2777**, and nominal one-sided t-test p-value **0.001867596**.

## Data and causal validation

- The data files retain the official token streams; all 104 files were hash-checked during data preparation.
- Validation uses the full target token count and full vocabulary. Sampled softmax is used during training, not to narrow the validation vocabulary.
- Online retrieval queries every microbatch of a training step before inserting that step's tokens.
- Offline retrieval is built from **all 103 training shards**. Validation queries use causal prefixes; validation targets are not inserted into the retrieval index, and validation performs no backward updates.
- The neural training loop consumes part of the corpus. Full-corpus retrieval is a separate component of the learning method.

## Timing boundary

The score is the final validation line's `train_time`. The last ordinary training-progress line can be smaller because required final work still follows it.

| Outside the measured interval | Inside the measured interval |
|---|---|
| Compilation and warmup; model and optimizer state are restored after warmup | Formal training data reads and neural training |
| Empty retrieval-storage allocation and prefault | Training-content index construction |
| Thread preparation and validation-file header read | Online queries/inserts and offline validation-prefix queries |
| Final model validation computation | Required index release, cross-rank merge, thread joins, final weight processing, and CUDA synchronization before stopping the clock |

Training-content index construction starts after the clock starts. A zero final cache-wait measurement means background work already completed during the timed interval.

The CPU affinity, deferred wait, coordinated release, and raw-pageable changes preserve this boundary. The shorter training schedule changes learning and is evaluated as a separate cohort.

## Evidence

The final review checks source manifests, fixed strategies, registration before the first run, full terminal results, console/native-log agreement, and the five-run cohort record. All five slots remain in the final result; earlier cohorts and failures are separate. See [Evidence](EVIDENCE.md).

Targeted checks included Rust retrieval causality fixtures, real CUDA batch-lifetime checks, coordinated-release checks, and a **173-case loader comparison** using one CUDA device and eight simulated ranks. Statistical summaries use the precision emitted by the trainer. Source and log hashes verify file consistency.

The archived review checked compiler settings and the restoration of model and optimizer state after warmup. Machine-specific CPU affinity and the compilation-cache SSD are recorded with each strategy.
