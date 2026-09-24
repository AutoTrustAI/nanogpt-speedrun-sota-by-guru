# AutoTrust: fastest among the checked NanoGPT speedrun references

**AutoTrust's ScienceGuru platform, using Guru Turbo 1.2, reports a 24.8998-second five-seed mean: the fastest result among the references checked here.** At the shared 8 × H100 / FineWeb validation loss ≤3.28 target, this is **≈2.713× as fast, or ≈63.14% less training time**, than Canonical Token Masking's leaderboard time of **≈67.56 s**. Against ANVIL2's reported **39.914 s**, it is **1.603× as fast, or 37.62% less training time**. Sources: [our five-seed results](../results/cohorts.json), [official history](https://github.com/KellerJordan/modded-nanogpt#world-record-history), [ANVIL2 submission](https://github.com/KellerJordan/modded-nanogpt/pull/360).

The teams and methods below are ordered by their displayed training times. The comparison covers the references checked on **2026-09-24 UTC / 2026-09-25 Asia/Shanghai**.

## Teams, contributors, and methods

| Team / contributor | Publicly supported background | Method and reported time |
|---|---|---|
| **AutoTrust · ScienceGuru · Guru Turbo 1.2** | **AutoTrust** is the team and brand, **ScienceGuru** is its research platform, and **Guru Turbo 1.2** is the model used for this project. The [official organization](https://github.com/AutoTrustAI) links to [AutoTrust's website](https://autotrust.ai/), which describes ScienceGuru as a workspace for research, reasoning, and writing. The project-specific attribution is recorded [here](../provenance/project-attribution.json). | **24.8998 s**, mean of five fixed seeds. All five runs have validation loss ≤3.28; mean loss **3.27498**. [Result records](../results/cohorts.json) and [evidence](EVIDENCE.md). |
| **Hyperstition · Deven Pietrzak** | The [ANVIL2 PR](https://github.com/KellerJordan/modded-nanogpt/pull/360) identifies its creator as Deven Pietrzak, describes his background as “MIT Math,” and names the lab **Hyperstition**, formerly **Social Physics Lab**. These details are stated by the creator in the PR. | **ANVIL2: 39.914 s**, reported mean of 18 runs. The method combines sampled-softmax training, sparse hashed n-gram embeddings, the ANVIL optimizer, FP8 execution, mixed-width attention, and systems changes. [PR #360](https://github.com/KellerJordan/modded-nanogpt/pull/360). |
| **Herman Brunborg · `@hermabr`** | The author's [GitHub profile](https://github.com/hermabr) names **Herman Brunborg** and describes him as a **PhD student at Stanford**; it links to his [personal website](https://brunborg.com/). The method is credited to the individual contributor. | **Exact-match: 47.2056 s**, reported five-run mean. It uses a CPU cache of previously seen sequences to retrieve the token following the longest matching prefix. [PR #367](https://github.com/KellerJordan/modded-nanogpt/pull/367); [exact statistics](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md). |
| **Jan Varho · `@jvarho`** | The contributor's [personal website](https://jan.varho.org/) identifies him as a **software developer at Fluentia**; his [GitHub profile](https://github.com/jvarho) confirms the name. The leaderboard credits the individual contributor. | **Canonical Token Masking: 1.126 min ≈67.56 s**, official record **#91**. It masks infeasible token continuations during validation. [Official history](https://github.com/KellerJordan/modded-nanogpt#world-record-history); [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350). |
| **Recursive · Cong Lu** | The [Recursive website](https://www.recursive.com/) describes its focus on self-improving AI and automated scientific discovery. [Cong Lu's personal website](https://www.conglu.co.uk/) identifies him as a founding-team member and a former Google DeepMind research scientist. The upstream history credits `@cong_ml` and Recursive; [PR #322](https://github.com/KellerJordan/modded-nanogpt/pull/322) was submitted by his GitHub account `@conglu1997`. | **1.256 min ≈75.36 s**, official record **#87**, listed as a faster ReLU² kernel implementation. The PR also reports an earlier **77.34 s** mean on Modal hardware, which is a different result from the leaderboard time. [Official history](https://github.com/KellerJordan/modded-nanogpt#world-record-history); [PR #322](https://github.com/KellerJordan/modded-nanogpt/pull/322). |

Source-code lineage and acknowledgments are in [CREDITS.md](../CREDITS.md).

## What the comparisons mean

For a reference time `T` and our mean `24.8998 s`, the reported speedup is `T / 24.8998`, and the training-time reduction is `(T - 24.8998) / T × 100%`.

| Checked reference | Reference training time | Time saved | Speedup | Training-time reduction |
|---|---:|---:|---:|---:|
| Canonical Token Masking · #91 | ≈67.56 s | ≈42.6602 s | ≈2.713× | ≈63.14% |
| ANVIL2 | 39.914 s | 15.0142 s | 1.603× | 37.62% |
| Exact-match | 47.2056 s | 22.3058 s | 1.896× | 47.25% |
| Recursive · #87 | ≈75.36 s | ≈50.4602 s | ≈3.027× | ≈66.96% |

The historical values come from rounded leaderboard minutes, so their seconds and derived comparisons are approximate. The comparisons share a hardware class and loss target but use different machines, sample counts, software versions, and achieved losses; they are not controlled reruns on one machine. ANVIL2's reported cohort includes 17 raw logs and one recorded result whose raw log was lost. Our five fixed seeds were also used during development. See [Baselines](BASELINES.md), [Evidence](EVIDENCE.md), and the [history-chart source notes](SPEEDRUN_CHART.md).

## Short introduction for the README

**English:** AutoTrust's ScienceGuru platform, using Guru Turbo 1.2, reports **24.8998 s** across five seeds on 8 × H100, with every validation loss ≤3.28. It is the fastest among the checked comparison results: **≈2.713× as fast as Canonical Token Masking (≈63.14% less training time)** and **1.603× as fast as ANVIL2 (37.62% less training time)**. The comparison includes Hyperstition's ANVIL2, Herman Brunborg's Exact-match, Jan Varho's Canonical Token Masking, and Recursive. [Team backgrounds and sources](#teams-contributors-and-methods).

**中文：** AutoTrust 团队使用 **ScienceGuru 科研平台与 Guru Turbo 1.2 模型**，在 8 × H100 上取得五个种子平均 **24.8998 秒**的结果，五次验证损失均 ≤3.28。在已核查的对比项中，我们的训练时间最短：相对 Canonical Token Masking，**加速约 2.713 倍、用时减少约 63.14%**；相对 ANVIL2，**加速 1.603 倍、用时减少 37.62%**。对比团队与作者包括 Hyperstition、Herman Brunborg、Jan Varho 和 Recursive。[团队背景与来源](#teams-contributors-and-methods)。

<details>
<summary>Sources and check notes</summary>

The official history and PR metadata were checked on 2026-09-24 UTC / 2026-09-25 Asia/Shanghai. The selected comparisons do not form an exhaustive global ranking. The latest accepted upstream result remains Canonical Token Masking, record #91: its table date is 2026-08-06 and [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350) merged on 2026-09-18 UTC. Recursive's record #87 has table date 2026-06-11 and [PR #322](https://github.com/KellerJordan/modded-nanogpt/pull/322) merged on 2026-08-02 UTC. [ANVIL2 PR #360](https://github.com/KellerJordan/modded-nanogpt/pull/360), created 2026-08-31 UTC, and [Exact-match PR #367](https://github.com/KellerJordan/modded-nanogpt/pull/367), created 2026-09-17 UTC, were both open and unmerged. AutoTrust's 24.8998-second result is reported by this repository and is not an accepted upstream record.

Public professional affiliations describe the contributors' backgrounds; they do not establish that an employer or university sponsored or endorsed a submission. No parameter count, architecture specification, or claim of fully autonomous development for Guru Turbo 1.2 is inferred from these sources.

</details>
