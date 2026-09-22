# ForgeMatch

**ScienceGuru + Guru Turbo 1.2 · 24.8998 seconds on 8× H100, verified across five seeds.**

![NanoGPT training-time comparison: ForgeMatch 24.8998 seconds, ANVIL2 39.914, Exact-match 47.2056, community reference approximately 67.56, Recursive approximately 75.36, PACEvolve 140.2, NorMuon approximately 140.70, and Enigma approximately 179.40 seconds.](assets/benchmark-comparison.svg)

[Chart data and sources](docs/BASELINES.md) · [Download PNG](assets/benchmark-comparison.png)

[Chinese](README.zh-CN.md) · [Reproduce](docs/REPRODUCE.md) · [Strategy](docs/STRATEGY.md) · [Evidence](docs/EVIDENCE.md) · [Research baselines](docs/BASELINES.md) · [Rules and limitations](docs/COMPLIANCE.md)

ForgeMatch trains a language model with causal prefix retrieval, sparse n-gram embeddings, FP8 execution, and a compact training schedule. CPU affinity, asynchronous prefetching, and coordinated memory management keep the GPUs supplied with data and reduce timing variation.

## Verified result

**ScienceGuru + Guru Turbo 1.2** produced this 652-step result across five fixed seeds, with every run included. All five final validation losses are below **3.28**, measured on the complete **10,485,760-token** validation target with full-vocabulary probabilities.

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

The evidence-verified result is a local experimental result, **not an officially accepted world record**. Fixed seeds were used during adaptive development; the nominal t-test does not remove that statistical limitation. See [machine-readable results](results/cohorts.json) and the [evidence guide](docs/EVIDENCE.md).

## Comparison with public strategies

| Strategy | Reported mean time | Reported mean loss | Runs | ForgeMatch time reduction |
|---|---:|---:|---:|---:|
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 39.914 s | 3.277311 | 18 | **37.62% / 1.603×** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 s | 3.26556 | 5 | **47.25% / 1.896×** |
| **ForgeMatch, 652 steps** | **24.8998 s** | **3.27498** | **5** | — |

The public results use different machines and sample counts. These are comparisons at the same **loss ≤3.28 threshold**, not matched-loss or controlled same-machine speedups: Exact-match retains a larger quality margin. ANVIL2's published 18-run summary includes one run whose raw log was lost, as its authors disclose. The sources and our single-seed same-machine reproductions are explained in [Strategy](docs/STRATEGY.md#comparisons).

## Research-group baselines

Verified on **2026-09-23**. These are historical public results associated with identifiable research groups, on the 8×H100 / FineWeb loss ≤3.28 task. They are not a ranking of the groups' current capabilities. Approximate seconds marked below are conversions from rounded official leaderboard minutes.

| Research affiliation | Method | Public time | Evidence status |
|---|---|---:|---|
| Google + Google DeepMind, UW–Madison, UC San Diego | [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | **140.2 s** | Paper experiment from version 40; 142.8 → 140.2 s; no accepted record located |
| Georgia Tech + Microsoft | [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | **≈140.70 s** | Official historical record #41, 2.345 min |
| Stanford-associated Enigma project | [Faster gradient all-reduce](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | **≈179.40 s** | Official historical record #22, 2.990 min |
| Recursive | [ReLU² kernel contribution](https://github.com/KellerJordan/modded-nanogpt/pull/322) | **≈75.36 s** | Official historical record #87, 1.256 min; only part of the original submission was integrated |
| Hyperstition, formerly Social Physics Lab | [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | **39.914 s** | Public 18-run mean; PR still open |

Affiliation evidence, dates, original submission versus accepted-record distinctions, and separate optimizer-track results for OpenAI/Anthropic models are in [Research baselines](docs/BASELINES.md).

## What this benchmark establishes

NanoGPT Speedrun measures **time to a fixed language-modeling quality target**. It exercises training algorithms, model architecture, GPU kernels, distributed communication, data movement, and reproducible experimentation. Its research value includes exposing useful optimization ideas and providing an open task for evaluating autonomous research systems; Google/DeepMind, METR, and Prime Intellect have used it for this purpose. See [benchmark significance and scope](docs/BASELINES.md#benchmark-significance-and-scope).

The result applies to this workload and protocol. It does not establish frontier-model capability, inference speed, total research cost, or general superiority over another laboratory. ForgeMatch builds on newer community work than several historical baselines above and still needs official acceptance.

## What is included

- [`model/`](model/): the 33 archived source files, preserved byte for byte, including the Python trainer and Rust exact-match extension.
- [`provenance/source-files.json`](provenance/source-files.json): source hashes and original experiment commit identity.
- [`results/cohorts.json`](results/cohorts.json): measured cohorts and their status.
- [`docs/REPRODUCE.md`](docs/REPRODUCE.md): environment, data, and launch instructions.
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md): what the packaged evidence establishes and how to verify it.

The reference hardware is **8× H100 80GB HBM3**, two Xeon Platinum 8481C CPUs, and about **1.8 TiB host RAM**. The full retrieval corpus requires all **103 training shards**, plus the validation shard. The CPU affinity mapping is specific to that host topology. Follow [Reproduce](docs/REPRODUCE.md), rather than the inherited historical instructions inside `model/README.md`.

## Credits and license

[Source attribution and acknowledgments](CREDITS.md) · [MIT license](LICENSE)
