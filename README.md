# ScienceGuru: NanoGPT in 24.8998 seconds — ≈2.71× speedup over the official SOTA

**AutoTrust's ScienceGuru research platform, using Guru Turbo 1.2, brings NanoGPT Speedrun training below 25 seconds on 8×H100.** Mean training time is **24.8998 seconds**, meeting the validation-loss target of **≤3.28**. At the same quality target, this uses **≈63.14% less time than the official SOTA of ≈67.56 seconds**, saving **≈42.66 seconds**. [Results and comparison sources](docs/BASELINES.md).

| Mean training time | Speedup over official SOTA | Training time saved | Validation-loss target |
|---:|---:|---:|---:|
| **24.8998 s** | **≈2.71×** | **≈63.14%** | **≤3.28** |

Since 2024, the benchmark has accumulated **91 official records, plus two re-timings**. Each new improvement tackles a training system already refined by years of community optimization; the history below places our result in that progression.

![NanoGPT Speedrun history: 91 official records and two selected public results, followed by AutoTrust's ScienceGuru result using Guru Turbo 1.2 at 24.8998 seconds.](assets/speedrun-history.svg)

[Chart data and sources](docs/SPEEDRUN_CHART.md) · [Full history PNG](assets/speedrun-history.png) · [Recent history, enlarged](assets/speedrun-history-recent.png)

[Chinese](README.zh-CN.md) · [Reproduce](docs/REPRODUCE.md) · [Strategy](docs/STRATEGY.md) · [Evidence](docs/EVIDENCE.md) · [Research baselines](docs/BASELINES.md) · [Teams and contributors](docs/TEAMS.md) · [Benchmark protocol](docs/COMPLIANCE.md)

## AutoTrust, ScienceGuru, and Guru Turbo 1.2

### AutoTrust

[**AutoTrust**](https://autotrust.ai/about) is an applied AI research laboratory based in Singapore, building AI systems for scientific research. Its work spans scientific agents, long-horizon tasks, self-improving coding agents, open-ended algorithms, and AI scientists. The lab studies how trajectories from real research workflows can improve model training, inference, and agent orchestration, connecting practical scientific work with the development of more capable research systems.

### ScienceGuru

[**ScienceGuru**](https://scienceguru.ai/) is AutoTrust's research workspace, available on the web and desktop. It brings the lab's models into an environment for scientific reading, reasoning, and writing. The platform connects model capabilities to the daily work of research, supporting exploration within an ongoing scientific workflow. This NanoGPT project applies that focus to the practical challenge of optimizing a language-model training system.

### Guru Turbo 1.2

**Guru Turbo 1.2** is the model used in this ScienceGuru research project. AutoTrust's [**Guru family**](https://autotrust.ai/models) offers Nano, Pro, and Turbo tiers for scientific-agent workloads and sustained research tasks, drawing on scientific trajectories and synthetic scientific data for improvement. Here, Guru Turbo 1.2 is applied to the research and coding work behind the NanoGPT training strategy. The benchmark measures the training time of the small language model archived under [`model/`](model/).

The resulting strategy combines causal prefix retrieval, sparse n-gram embeddings, FP8 execution, and a compact training schedule, with CPU affinity, asynchronous prefetching, and coordinated memory management to keep the GPUs supplied with data and reduce timing variation.

## Verified result

**AutoTrust · ScienceGuru · Guru Turbo 1.2** achieved a mean training time of **24.8998 seconds** in 652 steps and a mean validation loss of **3.27498**, below the **3.28** target. Validation covers the complete **10,485,760-token** target with full-vocabulary probabilities.

The metric is the final `train_time`: training, content-dependent retrieval construction, and required completion work are timed. Compilation, warmup, and final model validation occur outside this interval. See the [timing protocol](docs/COMPLIANCE.md#timing-boundary).

See [machine-readable results](results/cohorts.json) and the [evidence guide](docs/EVIDENCE.md).

## Performance comparison

Results checked on **2026-09-24 UTC**, for **8×H100 / FineWeb loss ≤3.28**, ordered by training time. Each reference uses its source's reported time; ScienceGuru uses its mean training time. Values marked **≈** are converted from rounded leaderboard minutes.

![NanoGPT training-time comparison: ScienceGuru 24.8998 seconds, ANVIL2 39.914, Exact-match 47.2056, official SOTA approximately 67.56, Recursive approximately 75.36, PACEvolve 140.2, NorMuon approximately 140.70, and Enigma approximately 179.40 seconds.](assets/benchmark-comparison.svg)

[Download comparison PNG](assets/benchmark-comparison.png) · [Comparison data and sources](docs/BASELINES.md)

| Strategy | Team / affiliation | Training time | ScienceGuru speedup |
|---|---|---:|---:|
| **ScienceGuru, 652 steps** | **AutoTrust · Guru Turbo 1.2** | **24.8998 s** | — |
| [ANVIL2](https://github.com/KellerJordan/modded-nanogpt/pull/360) | Hyperstition, formerly Social Physics Lab | **39.914 s** | **1.603×** |
| [Exact-match](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | Herman Brunborg / Stanford PhD student | **47.2056 s** | **1.896×** |
| [**Official SOTA — Canonical Token Masking**](https://github.com/KellerJordan/modded-nanogpt/pull/350) | Jan Varho / Fluentia | **≈67.56 s** | **≈2.713×** |
| [ReLU² kernel contribution](https://github.com/KellerJordan/modded-nanogpt/pull/322) | Recursive | **≈75.36 s** | **≈3.027×** |
| [PACEvolve](https://arxiv.org/pdf/2601.10657v3) | Google + Google DeepMind, UW–Madison, UC San Diego | **140.2 s** | **5.631×** |
| [NorMuon](https://github.com/KellerJordan/modded-nanogpt/pull/144) | Georgia Tech + Microsoft | **≈140.70 s** | **≈5.651×** |
| [Faster gradient all-reduce](https://github.com/KellerJordan/modded-nanogpt#world-record-history) | Stanford-associated Enigma project | **≈179.40 s** | **≈7.205×** |

The [official Track 1 record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history) lists Canonical Token Masking at **1.126 minutes** ([PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350)). Against that published time, ScienceGuru uses **approximately 63.14% less training time**, a **2.713× speedup**, saving **about 42.66 seconds**.

ANVIL2 reports mean loss **3.277311**; Exact-match reports mean loss **3.26556**. ScienceGuru's time reductions against their published means are **37.62%** and **47.25%**, respectively. Same-machine reproductions are in [Strategy](docs/STRATEGY.md#comparisons); affiliations, dates, source details, and optimizer-track results for OpenAI/Anthropic models are in [Research baselines](docs/BASELINES.md).

## Background of the leading contributors

| Contributor | Public background | Result in this comparison |
|---|---|---|
| **Jan Varho · Canonical Token Masking** | Software developer at [Fluentia, according to his personal website](https://jan.varho.org/). | **≈67.56 s** |
| **Hyperstition · Deven Pietrzak** | The [ANVIL2 submission](https://github.com/KellerJordan/modded-nanogpt/pull/360) describes his background as “MIT Math” and names Hyperstition, formerly Social Physics Lab. | **39.914 s** |
| **Herman Brunborg · Exact-match** | His [GitHub profile](https://github.com/hermabr) identifies him as a PhD student at Stanford. | **47.2056 s** |
| **Recursive · Cong Lu** | A founding-team member of Recursive and former Google DeepMind research scientist, according to his [personal website](https://www.conglu.co.uk/). | **≈75.36 s** |

See [Teams and contributors](docs/TEAMS.md) for the methods, primary sources, and comparison scope. Source contributions to this implementation are acknowledged in [Credits](CREDITS.md).

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
