# ForgeMatch · 铸忆

**ANVIL2 training meets exact-match memory: 24.8998 seconds on 8× H100, verified across five seeds.**

[中文](README.zh-CN.md) · [Reproduce](docs/REPRODUCE.md) · [Strategy](docs/STRATEGY.md) · [Evidence](docs/EVIDENCE.md) · [Rules and limitations](docs/COMPLIANCE.md)

ForgeMatch combines ANVIL2's training system with exact-match retrieval, then tunes the training schedule and CPU/GPU coordination for the NanoGPT speedrun. **Forge** acknowledges the ANVIL lineage; **Match** describes retrieval from matching training prefixes. The Chinese name **铸忆** means forging memory. This is AutoTrust-AI's name for the integration and optimization work; the underlying contributions are credited in [CREDITS.md](CREDITS.md).

## Verified result

The 652-step cohort uses five fixed seeds, with every run included. All five final validation losses are below **3.28**, measured on the complete **10,485,760-token** validation target with full-vocabulary probabilities.

| Seed | Final `train_time` (s) | Validation loss |
|---:|---:|---:|
| 42 | 24.908 | 3.2733 |
| 43 | 24.898 | 3.2777 |
| 44 | 24.868 | 3.2752 |
| 45 | 24.939 | 3.2732 |
| 46 | 24.886 | 3.2755 |
| **Mean** | **24.8998** | **3.27498** |

- Time range: **0.071 s**; sample standard deviation: **0.026499 s**.
- Worst loss: **3.2777**; one-sided loss t-test against 3.28: **p ≈ 0.001868** (df = 4).
- Fixed execution order: **43 → 42 → 44 → 45 → 46**. No outlier removal, seed replacement, or reuse of an earlier cohort's results.
- The local target of mean time ≤25 s, time range ≤5 s, and all five losses ≤3.28 is met.

These are measured benchmark-section times, **not full process wall times**. Compilation, warmup, and final model validation are excluded by the inherited timing convention. Content-dependent retrieval construction and required completion work remain inside the clock. See the [timing disclosure](docs/COMPLIANCE.md#timing-boundary).

The independently audited result is a local experimental result, **not an officially accepted world record**. Fixed seeds were used during adaptive development; the nominal t-test does not remove that statistical limitation. See [machine-readable results](results/cohorts.json) and the [evidence guide](docs/EVIDENCE.md).

## Comparison with public strategies

| Strategy | Reported mean time | Reported mean loss | Runs | ForgeMatch time reduction |
|---|---:|---:|---:|---:|
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 39.914 s | 3.277311 | 18 | **37.62% / 1.603×** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 s | 3.26556 | 5 | **47.25% / 1.896×** |
| **ForgeMatch, 652 steps** | **24.8998 s** | **3.27498** | **5** | — |

The public results use different machines and sample counts. These are comparisons at the same **loss ≤3.28 threshold**, not matched-loss or controlled same-machine speedups: Exact-match retains a larger quality margin. ANVIL2's published 18-run summary includes one run whose raw log was lost, as its authors disclose. The sources and our single-seed same-machine reproductions are explained in [Strategy](docs/STRATEGY.md#comparisons).

## What is included

- [`model/`](model/): the 33 archived source files, preserved byte for byte, including the Python trainer and Rust exact-match extension.
- [`provenance/source-files.json`](provenance/source-files.json): source hashes and original experiment commit identity.
- [`results/cohorts.json`](results/cohorts.json): measured cohorts and their status.
- [`docs/REPRODUCE.md`](docs/REPRODUCE.md): environment, data, and launch instructions.
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md): what the packaged evidence establishes and how to verify it.

The reference hardware is **8× H100 80GB HBM3**, two Xeon Platinum 8481C CPUs, and about **1.8 TiB host RAM**. The full retrieval corpus requires all **103 training shards**, plus the validation shard. The CPU affinity mapping is specific to that host topology. Follow [Reproduce](docs/REPRODUCE.md), rather than the inherited historical instructions inside `model/README.md`.

## Credits and license

Built on [Keller Jordan's modded-nanogpt](https://github.com/KellerJordan/modded-nanogpt), [Deven Pietrzak's ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360), and [hermabr's exact-match retrieval](https://github.com/KellerJordan/modded-nanogpt/pull/367), with the many upstream contributors they build upon. See [CREDITS.md](CREDITS.md) and [LICENSE](LICENSE).
