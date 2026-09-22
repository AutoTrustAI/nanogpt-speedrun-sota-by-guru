# ForgeMatch

**ScienceGuru + Guru Turbo 1.2 · 24.8998 seconds on 8× H100, verified across five seeds.**

![NanoGPT training-time comparison: ForgeMatch 24.8998 seconds, ANVIL2 39.914, Exact-match 47.2056, community reference approximately 67.56, Recursive approximately 75.36, PACEvolve 140.2, NorMuon approximately 140.70, and Enigma approximately 179.40 seconds.](assets/benchmark-comparison.svg)

[Chart data and sources](docs/BASELINES.md) · [Download PNG](assets/benchmark-comparison.png)

[Chinese](README.zh-CN.md) · [Reproduce](docs/REPRODUCE.md) · [Strategy](docs/STRATEGY.md) · [Evidence](docs/EVIDENCE.md) · [Research baselines](docs/BASELINES.md) · [Benchmark protocol](docs/COMPLIANCE.md)

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
- Fixed execution order: **43 → 42 → 44 → 45 → 46**, with all five runs included.
- The target of mean time ≤25 s, time range ≤5 s, and all five losses ≤3.28 is met.

The metric is the final `train_time`: training, content-dependent retrieval construction, and required completion work are timed. Compilation, warmup, and final model validation occur outside this interval. See the [timing protocol](docs/COMPLIANCE.md#timing-boundary).

See [machine-readable results](results/cohorts.json) and the [evidence guide](docs/EVIDENCE.md).

## Comparison with the official SOTA

As of **2026-09-23**, the latest result in the [official Track 1 record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history) is **Canonical Token Masking by @jvarho**, at **1.126 minutes (≈67.56 seconds)**. Its [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350) is merged.

| Strategy | Training time | Hardware | Target loss |
|---|---:|---|---:|
| **Official SOTA — Canonical Token Masking** | **≈67.56 s** | 8× H100 | ≤3.28 |
| **ForgeMatch — ScienceGuru + Guru Turbo 1.2** | **24.8998 s** | 8× H100 | ≤3.28 |

ForgeMatch uses **approximately 63.14% less training time**, a **2.713× speedup** against the published official SOTA time, saving **about 42.66 seconds**. The reference seconds are converted from the leaderboard's rounded minutes; ForgeMatch is the measured five-seed mean.

## Comparison with public strategies

| Strategy | Reported mean time | Reported mean loss | Runs | ForgeMatch time reduction |
|---|---:|---:|---:|---:|
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 39.914 s | 3.277311 | 18 | **37.62% / 1.603×** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 s | 3.26556 | 5 | **47.25% / 1.896×** |
| **ForgeMatch, 652 steps** | **24.8998 s** | **3.27498** | **5** | — |

The comparison uses the **loss ≤3.28 threshold** and each source's reported mean on its respective machine. Sample counts and achieved losses appear above; sources and same-machine seed-42 reproductions are in [Strategy](docs/STRATEGY.md#comparisons).

## Research-group baselines

Results checked on **2026-09-23**, for **8×H100 / FineWeb loss ≤3.28**. Approximate seconds are converted from rounded leaderboard minutes.

| Research affiliation | Method | Public time |
|---|---|---:|
| Google + Google DeepMind, UW–Madison, UC San Diego | [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | **140.2 s** |
| Georgia Tech + Microsoft | [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | **≈140.70 s** |
| Stanford-associated Enigma project | [Faster gradient all-reduce](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | **≈179.40 s** |
| Recursive | [ReLU² kernel contribution](https://github.com/KellerJordan/modded-nanogpt/pull/322) | **≈75.36 s** |
| Hyperstition, formerly Social Physics Lab | [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | **39.914 s** |

Affiliations, dates, source details, and optimizer-track results for OpenAI/Anthropic models are in [Research baselines](docs/BASELINES.md).

## What this benchmark establishes

NanoGPT Speedrun measures **time to a fixed language-modeling quality target**. It exercises training algorithms, model architecture, GPU kernels, distributed communication, data movement, and reproducible experimentation. Its research value includes exposing useful optimization ideas and providing an open task for evaluating autonomous research systems; Google/DeepMind, METR, and Prime Intellect have used it for this purpose. See [benchmark significance and scope](docs/BASELINES.md#benchmark-significance-and-scope).

## What is included

- [`model/`](model/): the 33 archived source files, preserved byte for byte, including the Python trainer and Rust exact-match extension.
- [`provenance/source-files.json`](provenance/source-files.json): source hashes and original experiment commit identity.
- [`results/cohorts.json`](results/cohorts.json): measured cohorts and their status.
- [`docs/REPRODUCE.md`](docs/REPRODUCE.md): environment, data, and launch instructions.
- [`docs/EVIDENCE.md`](docs/EVIDENCE.md): what the packaged evidence establishes and how to verify it.

The reference hardware is **8× H100 80GB HBM3**, two Xeon Platinum 8481C CPUs, and about **1.8 TiB host RAM**. The full retrieval corpus requires all **103 training shards**, plus the validation shard. The CPU affinity mapping is specific to that host topology. Follow [Reproduce](docs/REPRODUCE.md), rather than the inherited historical instructions inside `model/README.md`.

## Credits and license

[Source attribution and acknowledgments](CREDITS.md) · [MIT license](LICENSE)
