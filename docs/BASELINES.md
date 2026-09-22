# Research baselines and benchmark context

Checked **2026-09-23**. This is a sourced comparison of published results, not a new reproduction study or a comprehensive ranking of institutions. Historical accepted records, paper experiments, open submissions, and optimizer-track evaluations have different evidentiary meanings.

## Training-time baselines

These results concern the 8×H100 task targeting FineWeb validation loss ≤3.28. Official leaderboard times are sometimes normalized using improvements over a same-machine reproduction. Values converted from rounded leaderboard minutes are approximate and should not be presented as raw run means.

| Research affiliation | Work | Time | Date / status |
|---|---|---:|---|
| Google, Google DeepMind, UW–Madison, UC San Diego | PACEvolve | **140.2 s** | Paper v3 dated 2026-09-10; version-40 experiment, not an identified accepted record |
| Georgia Tech and Microsoft | NorMuon | **≈140.70 s** | Official record #41: 2.345 min, dated 2025-10-24; PR144 merged 2025-10-29 |
| Stanford-associated Enigma project | Faster gradient all-reduce | **≈179.40 s** | Official record #22: 2.990 min, 2025-05-24 |
| Recursive | Faster ReLU² MLP kernel | **≈75.36 s** | Official record #87: 1.256 min; contribution dated 2026-06-11, PR322 merged 2026-08-02 |
| Hyperstition, formerly Social Physics Lab | ANVIL2 | **39.914 s** | Public mean over 18 runs; PR360 opened 2026-08-31, still open at this check |
| Community reference, not a laboratory attribution | Infeasible-token-continuation masking | **≈67.56 s** | Latest listed accepted record #91: 1.126 min, 2026-08-06 |
| **ScienceGuru + Guru Turbo 1.2** | **ForgeMatch** | **24.8998 s** | Local five-seed cohort, 652 steps; not officially accepted |

Record identities and rounded times come from the [official record history](https://github.com/KellerJordan/modded-nanogpt#world-record-history). ForgeMatch's measured runs and limitations are in [Evidence](EVIDENCE.md). Its newer starting code, hardware, evaluation details, and adaptive development differ from the historical baselines. A ratio between rows does not measure relative laboratory or agent competence.

### Affiliation and measurement evidence

- **PACEvolve:** [paper v3](https://arxiv.org/pdf/2601.10657v3), page 1, explicitly lists the four institutions. Section 4.2, page 8, specifies Gemini 3 Pro, 8 H100 GPUs, and the 3.28 FineWeb target. It reports an old version-40 baseline of 142.8 s improving through 141.9, 141.5, and 140.8 to 140.2 s. This section does not provide a complete multi-seed summary for that final time. [Code is hosted by Google](https://github.com/google/pacevolve).
- **NorMuon:** the [paper](https://arxiv.org/pdf/2510.05491), page 1, identifies Georgia Tech and Microsoft. First author Zichong Li submitted [PR144](https://github.com/KellerJordan/modded-nanogpt/pull/144), reporting two 20-run groups on 8 H100s and reducing steps from 2330 to 2315. The official historical record is 2.345 min; its converted value is not the same as an independently recomputed mean from all original logs.
- **Enigma:** the [OmniMouse paper](https://borowiecki.dev/pdf/2604.18827) identifies Stanford-affiliated contributors on page 1; Appendix A.5, page 22, explicitly connects the group's distributed-training strategy to NanoGPT record #22. The leaderboard also names the Enigma project. This supports a Stanford-associated project attribution; it does not establish a Hazy Research or CRFM submission.
- **Recursive:** [PR322](https://github.com/KellerJordan/modded-nanogpt/pull/322) identifies Recursive and reports **77.34 s**, mean loss **3.27893**, across **13** Modal runs, against **80.61 s** for its 10-run same-machine baseline. Those are the original branch's measurements. The maintainer later integrated only the ReLU² kernel into a newer baseline, yielding official record #87 at 1.256 min. The original 77.34 s and accepted ≈75.36 s describe different code versions.
- **ANVIL2:** [PR360](https://github.com/KellerJordan/modded-nanogpt/pull/360) names Deven Pietrzak and Hyperstition, formerly Social Physics Lab. Its 18-run mean is 39.914 s, with mean loss about 3.27731; one raw log is disclosed as lost. The author's MIT background does not establish an MIT laboratory submission. Source authorship is documented in [Credits](../CREDITS.md).

## OpenAI and Anthropic models: a separate optimizer evaluation

Prime Intellect evaluates models from major laboratories as research agents. **Prime Intellect is the experiment organizer**; these rows are not laboratory-authored Track 1 submissions. Its [Frontier page](https://www.primeintellect.ai/research/nanogpt-speedrun) reports best validated optimizer-track step counts, with different total search budgets:

| Model provider / model | Best validated steps | Steps after 24 agent-hours | Search duration for listed trajectory |
|---|---:|---:|---:|
| Anthropic / Fable 5 | **2726** | 3010 | 8.7 days |
| Anthropic / Opus 5 | **2920** | 3045 | 2.9 days |
| OpenAI / GPT-5.6 Sol | **3042** | 3160 | 6.1 days |

The [methodology](https://www.primeintellect.ai/blog/measuring-autonomous-research) describes 8×H200 nodes, an internally verified 3290-step starting baseline, and an open human record claim at 2600 steps. Claims require eight fixed-seed runs under a protected verifier. These step counts cannot be compared to ForgeMatch's 652 steps: the permitted edits and model/training configuration differ. The best final results also do not share an equal search-time budget.

This review did not establish comparable institution-authored Track 1 times for NVIDIA, Together AI, or Anthropic. That is a limit of the evidence located here, not evidence that those institutions have never worked on the task. Employee affiliations, GPU sponsorship, and kernel-only benchmarks are insufficient to assign a full training record to an institution.

## Benchmark significance and scope

**Assessment:** this is a valuable specialist benchmark for training efficiency and an increasingly useful testbed for automated research. Its relevance to general model capability or frontier-scale economics is indirect.

1. **It couples speed with quality.** A fast training loop only succeeds when it reaches the specified validation target. Optimizer, architecture, numerical precision, communication, and data-system choices interact, making it a useful integrated engineering task. The [official rules](https://github.com/KellerJordan/modded-nanogpt#rules) fix the token streams, require statistical evidence for ML-changing submissions, restrict extra compiler flags, and require improvement against a same-machine baseline.
2. **It has traceable, cumulative progress.** Public code, PR discussions, logs, and historical records allow ideas to be inspected and reproduced. Google/DeepMind's [PACEvolve experiment](https://arxiv.org/pdf/2601.10657v3) and [METR's research](https://metr.org/blog/2026-07-21-expenditure-horizon/) illustrate its use as an AI R&D task. METR also documents how revalidation can remove apparent gains caused by noise and how older starting points risk contamination from models' prior knowledge.
3. **Some underlying ideas transfer.** Muon is an important part of the speedrun's optimization lineage. Moonshot's [Kimi K2 report](https://arxiv.org/abs/2507.20534) describes extending Muon with QK-Clip for large-scale pretraining. This supports the relevance of some optimization ideas; it does not show that every small-model speedrun technique scales.

| Capability exercised | Examples |
|---|---|
| Optimization and convergence | Learning rates, optimizer updates, initialization, schedule and step count |
| Modeling | Attention, residual paths, embeddings, auxiliary objectives |
| GPU and distributed systems | BF16/FP8, fused kernels, memory traffic, collective communication overlap |
| Host/data systems | Loading, prefetch, CPU placement, allocations and host-to-device transfers |
| Experimental reasoning | Profiling, hypotheses, ablations, multiple runs, statistical checks and reproducibility |

The core metric is training time to a fixed FineWeb language-modeling loss, not chat quality, reasoning ability, coding accuracy, inference latency, or total project cost. The current task descends from a GPT-2-small-quality target; that label should not be read as a requirement to retain the original GPT-2 architecture. For example, large lookup tables and hardware-specific techniques can improve the speedrun while needing separate studies of memory cost, inference behavior, and scaling.

An agent-assisted result additionally depends on its starting code, internet access, tools, human steering, experiment budget, and prior exposure to the benchmark. ForgeMatch's 24.8998 s is evidence about a training recipe under its documented setup. Establishing broader research-agent superiority would require a controlled evaluation with matched starting points and budgets, independent held-out runs, and other tasks. Official record acceptance also remains separate from our local evidence checks.
