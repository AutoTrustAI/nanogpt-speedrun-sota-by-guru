# Rules, timing, and acceptance status

The reviewed systems changes did not reveal an explicit rule violation within the inspected scope. **ForgeMatch has not been accepted as an official NanoGPT speedrun record.** Local evidence review and a passing five-seed target do not constitute an upstream ruling.

This document summarizes the archived rules review performed on **2026-09-22 UTC / 2026-09-23 Asia/Shanghai**, against upstream master `bc3a0c2d640d0d73dedaef87eae26148d2e32afb`. It is a dated review, not a claim about the current state of upstream review. The [official rules](https://github.com/KellerJordan/modded-nanogpt#rules) remain authoritative.

## Benchmark requirements

The main track uses 8×H100 and the fixed underlying FineWeb train/validation token streams. The target is mean validation cross-entropy ≤3.28 on the complete **10,485,760-token** validation target. Learning-method changes require log-backed statistical evidence with **p<0.01**; the rules prohibit additional Inductor/compile tuning flags and require a speed comparison with the preceding record on the same hardware. Readability and the treatment of loss margin remain subject to maintainer judgment. See the [rules](https://github.com/KellerJordan/modded-nanogpt#rules) and [target-metric discussion](https://github.com/KellerJordan/modded-nanogpt#comment-on-the-target-metric).

Our additional local requirement is stricter than a mean-loss gate: **each** of the five chosen seeds must have final loss ≤3.28, mean time ≤25 s, and time range ≤5 s. The complete 652-step cohort satisfies those numerical conditions. Its mean loss is **3.27498**, worst loss **3.2777**, and nominal one-sided t-test p-value **0.001867596**. A fixed five-seed cohort after adaptive development does not establish independent random sampling or guarantee future-run behavior.

## Data and causal validation

- The data files retain the official token streams; all 104 files were hash-checked during data preparation.
- Validation uses the full target token count and full vocabulary. Sampled softmax is used during ANVIL2 training, not to narrow the validation vocabulary.
- Online retrieval queries every microbatch of a training step before inserting that step's tokens.
- Offline retrieval is built from **all 103 training shards**. Validation queries use causal prefixes; validation targets are not inserted into the retrieval index, and validation performs no backward updates.
- The neural training loop consumes only part of the corpus. The broader retrieval corpus is therefore an explicit part of the learning method, not a pure systems optimization.

Static inspection and targeted tests support these statements; they are not a formal proof of every execution. The full-corpus retrieval method and its timing conventions still require upstream acceptance.

## Timing boundary

The score is the final validation line's `train_time`. The last ordinary training-progress line can be smaller because required final work still follows it.

| Outside the measured interval | Inside the measured interval |
|---|---|
| Compilation and warmup; model and optimizer state are restored after warmup | Formal training data reads and neural training |
| Empty retrieval-storage allocation and prefault | Training-content index construction |
| Thread preparation and validation-file header read | Online queries/inserts and offline validation-prefix queries |
| Final model validation computation | Required index release, cross-rank merge, thread joins, final weight processing, and CUDA synchronization before stopping the clock |

No training-content index is built before the clock starts. The excluded preparation is inherited and disclosed; we do **not** claim every preparation operation is timed. A zero final cache-wait measurement means background work already completed during the timed interval, not that construction was free.

The CPU affinity, deferred wait, coordinated release, and raw-pageable changes preserve this boundary. The shorter training schedule changes learning and is evaluated as a separate cohort.

## Evidence and limits

The final review checks source manifests, fixed strategies, registration before the first run, full terminal results, console/native-log agreement, and the five-run cohort record. All five slots remain in the final result; earlier cohorts and failures are separate. See [Evidence](EVIDENCE.md).

Targeted checks included Rust retrieval causality fixtures, real CUDA batch-lifetime checks, coordinated-release checks, and a **173-case loader comparison**. The loader check used one CUDA device and eight simulated ranks; it does not prove full distributed model equivalence or production performance. Statistical summaries use the precision emitted by the trainer. Hashes establish file consistency, not independently signed provenance.

The archived review found no added compile tuning flags or unreset warmup learning. Machine-specific CPU affinity and the change of compilation-cache SSD are recorded configuration differences. They do not establish that all unrecorded host conditions were identical.

## Upstream status at the review snapshot

- [ANVIL2 PR #360](https://github.com/KellerJordan/modded-nanogpt/pull/360) was open. The [maintainer's comment](https://github.com/KellerJordan/modded-nanogpt/pull/360#issuecomment-5565930470) supported the described methods' legitimacy while requiring their own reproduction before acceptance. It does not approve the ForgeMatch hybrid.
- [Exact-match PR #367](https://github.com/KellerJordan/modded-nanogpt/pull/367) was open, with no reviews displayed in the archived check.
- No ForgeMatch submission or official acceptance is established by this repository.

Public speed comparisons use different machines and actual losses. Our single-seed same-machine reproductions do not replace the official multi-run comparison and review process.
