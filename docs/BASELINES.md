# Research baselines and benchmark context

Training results, research affiliations, and source references. Updated **2026-09-24 UTC**.

## Official SOTA comparison

The latest accepted Track 1 entry is **Canonical Token Masking by @jvarho**, record **#91**, at **1.126 min (≈67.56 s)** in the [official record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history). [PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350) was merged on **2026-09-18**; the record table dates the contribution **2026-08-06**. This is the final official-history point in the [opening chart](SPEEDRUN_CHART.md).

Against that published time, ScienceGuru's **24.8998 s** five-seed mean uses **≈63.14% less time**, a **≈2.713× speedup**, saving **≈42.66 s**. Both target FineWeb validation loss ≤3.28 on 8×H100. The ratios use the leaderboard's rounded-minute value for the reference and the measured cohort mean for ScienceGuru.

## Training-time baselines

These results concern the **8×H100 / FineWeb validation loss ≤3.28** task. Times marked **≈** are converted from the published leaderboard's rounded minutes.

| Research affiliation | Work | Time | Source |
|---|---|---:|---|
| Google, Google DeepMind, UW–Madison, UC San Diego | PACEvolve | **140.2 s** | [Paper, §4.2](https://arxiv.org/pdf/2601.10657v3) |
| Georgia Tech and Microsoft | NorMuon | **≈140.70 s** | [PR144](https://github.com/KellerJordan/modded-nanogpt/pull/144) / [record #41](https://github.com/KellerJordan/modded-nanogpt#world-record-history) |
| Stanford-associated Enigma project | Faster gradient all-reduce | **≈179.40 s** | [Record #22](https://github.com/KellerJordan/modded-nanogpt#world-record-history) |
| Recursive | Faster ReLU² MLP kernel | **≈75.36 s** | [PR322](https://github.com/KellerJordan/modded-nanogpt/pull/322) / [record #87](https://github.com/KellerJordan/modded-nanogpt#world-record-history) |
| Hyperstition, formerly Social Physics Lab | ANVIL2 | **39.914 s** | [PR360](https://github.com/KellerJordan/modded-nanogpt/pull/360) |
| hermabr | Exact-match | **47.2056 s** | [PR367](https://github.com/KellerJordan/modded-nanogpt/pull/367) |
| modded-nanogpt community / @jvarho | Canonical Token Masking | **≈67.56 s** | [Record #91](https://github.com/KellerJordan/modded-nanogpt#world-record-history) / [PR350](https://github.com/KellerJordan/modded-nanogpt/pull/350) |
| **AutoTrust · Guru Turbo 1.2** | **ScienceGuru** | **24.8998 s** | [Five-seed results](../results/cohorts.json), 652 steps |

The [record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history) supplies record identifiers and rounded times. ScienceGuru's run records, source hashes, and measurement protocol are in [Evidence](EVIDENCE.md).

Contributor biographies and primary sources for the leading results are collected in [Teams and contributors](TEAMS.md).

### Affiliations and experiment details

- **PACEvolve:** [paper v3](https://arxiv.org/pdf/2601.10657v3), dated 2026-09-10, lists the four institutions on page 1. Section 4.2, page 8, specifies Gemini 3 Pro, 8 H100 GPUs, and the 3.28 FineWeb target. Its version-40 baseline improves from 142.8 s through 141.9, 141.5, and 140.8 to 140.2 s. [Code](https://github.com/google/pacevolve).
- **NorMuon:** the [paper](https://arxiv.org/pdf/2510.05491), page 1, identifies Georgia Tech and Microsoft. First author Zichong Li's [PR144](https://github.com/KellerJordan/modded-nanogpt/pull/144) reports two 20-run groups on 8 H100s and reduces the step count from 2330 to 2315. The listed result is 2.345 min, dated 2025-10-24.
- **Enigma:** the [OmniMouse paper](https://borowiecki.dev/pdf/2604.18827) identifies Stanford-affiliated contributors on page 1. Appendix A.5, page 22, connects the group's distributed-training strategy to NanoGPT record #22, dated 2025-05-24.
- **Recursive:** [PR322](https://github.com/KellerJordan/modded-nanogpt/pull/322) reports **77.34 s**, mean loss **3.27893**, across **13** Modal runs, against **80.61 s** for its 10-run same-machine baseline. Applying the ReLU² kernel change to the later baseline produces the table's **1.256 min** result, dated 2026-06-11.
- **ANVIL2:** [PR360](https://github.com/KellerJordan/modded-nanogpt/pull/360) names Deven Pietrzak and Hyperstition, formerly Social Physics Lab. Its 18-run mean is 39.914 s, with mean loss about 3.27731. The reported cohort contains 17 raw logs and one ledger-recorded result. [Credits](../CREDITS.md).
- **Exact-match:** the author's [statistics](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) report a five-run mean of 47.2056 s and mean loss 3.26556, using seeds 0–4.

## OpenAI and Anthropic models: optimizer-step baselines

**Prime Intellect** evaluates research agents on the optimizer track, which measures the steps needed to reach the target loss with a fixed model and batch configuration. Its [Frontier page](https://www.primeintellect.ai/research/nanogpt-speedrun) reports these results and search budgets:

| Model provider / model | Best validated steps | Steps after 24 agent-hours | Search duration for listed trajectory |
|---|---:|---:|---:|
| Anthropic / Fable 5 | **2726** | 3010 | 8.7 days |
| Anthropic / Opus 5 | **2920** | 3045 | 2.9 days |
| OpenAI / GPT-5.6 Sol | **3042** | 3160 | 6.1 days |

The [methodology](https://www.primeintellect.ai/blog/measuring-autonomous-research) uses 8×H200 nodes, a verified 3290-step starting baseline, and a human reference at 2600 steps. Validation uses eight fixed-seed runs under a protected verifier. The table gives each trajectory's search duration and its result after 24 agent-hours.

## Benchmark significance and scope

NanoGPT Speedrun evaluates training efficiency and provides an open testbed for automated research.

1. **It couples speed with quality.** A fast training loop only succeeds when it reaches the specified validation target. Optimizer, architecture, numerical precision, communication, and data-system choices interact, making it a useful integrated engineering task. The [official rules](https://github.com/KellerJordan/modded-nanogpt#rules) fix the token streams, require statistical evidence for ML-changing submissions, restrict extra compiler flags, and require improvement against a same-machine baseline.
2. **It has traceable, cumulative progress.** Public code, PR discussions, logs, and records allow ideas to be inspected and reproduced. Google/DeepMind's [PACEvolve experiment](https://arxiv.org/pdf/2601.10657v3) and [METR's research](https://metr.org/blog/2026-07-21-expenditure-horizon/) use it as an AI R&D task, with repeated validation of candidate improvements.
3. **Optimization ideas inform larger training systems.** Muon is part of the speedrun's optimization lineage. Moonshot's [Kimi K2 report](https://arxiv.org/abs/2507.20534) describes extending Muon with QK-Clip for large-scale pretraining.

| Capability exercised | Examples |
|---|---|
| Optimization and convergence | Learning rates, optimizer updates, initialization, schedule and step count |
| Modeling | Attention, residual paths, embeddings, auxiliary objectives |
| GPU and distributed systems | BF16/FP8, fused kernels, memory traffic, collective communication overlap |
| Host/data systems | Loading, prefetch, CPU placement, allocations and host-to-device transfers |
| Experimental reasoning | Profiling, hypotheses, ablations, multiple runs, statistical checks and reproducibility |

The main track measures training time to a fixed FineWeb language-modeling loss. It permits changes to architecture and training methods, including sparse lookup tables, numerical precision, and hardware-specific kernels. The optimizer track fixes the model and batch configuration and measures training steps. ScienceGuru's training configuration and execution environment are documented in [Strategy](STRATEGY.md) and [Reproduce](REPRODUCE.md).

## Regenerating the charts

The README opens with the full [speedrun history chart](../assets/speedrun-history.svg): all **91 numbered official records**, including the two additional re-timings of record #21, followed by two selected public results and ScienceGuru's final five-seed mean. A [recent-history version](../assets/speedrun-history-recent.svg) focuses on October 2025 onward. Both use a logarithmic training-time axis and plot ScienceGuru after the public results. Historical rows and source links are in [speedrun-history-data.json](../assets/speedrun-history-data.json); ScienceGuru's measured mean is read directly from [cohorts.json](../results/cohorts.json). See [chart data notes](SPEEDRUN_CHART.md) for dates, source precision, and interpretation.

With Python and Matplotlib installed, run from the repository root:

```sh
python3 scripts/plot_speedrun_history.py
```

This recreates the full and recent-history SVG and PNG files in `assets/`.

The additional [horizontal comparison chart](../assets/benchmark-comparison.svg) shows selected training-time baselines on a linear axis starting at zero. It reads the same ScienceGuru cohort mean, with public values and sources from [comparison-data.json](../assets/comparison-data.json). Approximate public values retain their precision markers. Recreate its [SVG](../assets/benchmark-comparison.svg) and [PNG](../assets/benchmark-comparison.png) with:

```sh
python3 scripts/plot_comparison.py
```

The renderers use Matplotlib; the original comparison renderer was verified with Matplotlib 3.11.1.
