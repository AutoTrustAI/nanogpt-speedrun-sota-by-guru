# ForgeMatch strategy

ForgeMatch uses causal prefix retrieval, sparse n-gram embeddings, FP8 execution, and a compact training schedule to reach the NanoGPT speedrun's loss target. Retrieved continuation features provide predictive information at three points in the network. Asynchronous data movement and coordinated CPU/GPU execution reduce overhead and timing variation.

## Learning method

The training path uses mixed-width attention, sparse n-gram embeddings, sampled softmax, FP8 computation, and CUDA graph execution. Its optimizer updates and learning-rate schedule are arranged around the changing batch and sequence lengths. Validation remains full vocabulary.

The retrieval index searches training prefixes with a minimum context of 8 and maximum of 512 tokens. Its candidate continuations and match lengths become learned retrieval vectors, injected at the input, middle, and output of the network. See [`retrieval.py`](../model/retrieval.py), [`train_gpt.py`](../model/train_gpt.py), and the [Rust implementation](../model/exact_match/src/lib.rs).

During training, all microbatches in one optimizer step query before that step's tokens are inserted into the online index. The loader preserves real document boundaries before attention-window splitting. During validation, each rank indexes a partition of all **103 training shards** and queries causal validation prefixes against this training-only index. Cross-rank merging selects the top two distinct continuations using match length, shard-local count, and token identity. The retrieval index covers the full training corpus, while the neural training loop consumes the token counts below.

`HYBRID_TOTAL_STEPS=652` rescales the full training schedule. The stage boundaries change from **0/167/354/601/636/656** to **0/166/352/597/632/652**. The 652-step schedule consumes **180,944,896 neural input tokens**, versus **182,124,544** at 656 steps. Each schedule has its own complete five-seed evaluation.

## Systems changes

| Change | Implementation and purpose |
|---|---|
| CPU affinity | Each rank uses 13 physical CPU cores on its GPU's NUMA node; `OMP_NUM_THREADS=1`, `RAYON_NUM_THREADS=4`. Placement is applied before Torch and worker-pool initialization. The mapping is specific to the measured two-socket host. |
| Deferred CUDA wait | A prefetched batch carries its readiness event. The consumer waits just before first GPU use instead of importing a future batch's dependency into earlier work. `record_stream` preserves the six GPU buffers' lifetimes. |
| Coordinated index release | The offline status all-reduce precedes index release, so ranks coordinate completion of queries before cleanup. The collective count and retrieval ranking rule stay the same. |
| Pageable raw shards | Large raw CPU shards use ordinary pageable allocation; actual asynchronous H2D copies still use the existing pinned batch ring. This avoids pinning whole shards that are not immediately consumed. |

The archived 33-file source is identified by original experiment commit `d7b6a09512010189292974b3a9b9f19c111d9b38`. Relative to parent `7f6f968dea96b9c5219affc4b6c0a678cf1d57c0`, the final source change only switches the raw-shard `pin_memory` flag and its comment. The 652- and 656-step cohorts use the same source bytes with different step settings and fresh compilation-cache locations. The [manifest](../provenance/source-files.json) pins those bytes independently of this repository's packaging commit.

## Measured progression

Each row summarizes a complete five-run cohort with fixed seeds 42–46.

| Configuration | Steps | Mean time (s) | Time range (s) | Mean loss | Worst loss |
|---|---:|---:|---:|---:|---:|
| CPU affinity + deferred wait | 656 | 25.2832 | 0.545 | 3.27312 | 3.2761 |
| + coordinated release, complete v2 cohort | 656 | 25.0862 | 0.104 | 3.27374 | 3.2766 |
| + pageable raw shards | 656 | 25.0054 | 0.108 | 3.27388 | 3.2769 |
| **ForgeMatch, shorter schedule** | **652** | **24.8998** | **0.071** | **3.27498** | **3.2777** |

The final schedule saves **105.6 ms** on the five-run mean versus 656 steps, while mean loss rises by **0.00110**. The cohorts used fresh compilation caches on successive local SSDs. The final cohort ran in the order **43→42→44→45→46**, with a pause after seed43; its statistics include all five completed runs.

The final one-sided t-test for mean loss <3.28 gives **t = 6.063616**, **df = 4**, **p ≈ 0.001867596**. Development and evaluation used fixed seeds 42–46. See [Evidence](EVIDENCE.md) for the complete run records and statistical calculation.

An earlier coordinated-release cohort stopped when a compilation-cache filesystem ran out of inodes. Its completed runs and failure remain in the experiment archive. The v2 cohort used five fresh runs.

## Comparisons

The latest accepted [official Track 1 result](https://github.com/KellerJordan/modded-nanogpt#world-record-history), checked **2026-09-23**, is **Canonical Token Masking by @jvarho** ([merged PR #350](https://github.com/KellerJordan/modded-nanogpt/pull/350)): **1.126 min (≈67.56 s)**. ForgeMatch's **24.8998 s** five-seed mean reduces the published training time by **≈63.14%**, a **≈2.713× speedup**, at the shared 8×H100 / loss ≤3.28 target. Reference seconds and ratios use the leaderboard's rounded-minute value.

Public reference values are from the archived upstream reports:

| Reference | Mean time | Mean loss | Samples | Reduction to 24.8998 s |
|---|---:|---:|---:|---:|
| [ANVIL2 statistics](https://github.com/devenpzak/modded-nanogpt/blob/c924f68e4d72e80307fc27a7bb3a55cfb6ad43c7/records/track_1_short/2026-08-30_ANVIL2/this_pr/statistics.md) | 39.914 s | 3.2773111111 | 18 | 15.0142 s / 37.62% / 1.603× |
| [Exact-match statistics](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md) | 47.2056 s | 3.26556 | 5 | 22.3058 s / 47.25% / 1.896× |

The comparison uses the common **loss ≤3.28** target. ANVIL2 reports 18 unseeded runs on a Vast.ai 8×H100 instance; its cohort contains 17 raw logs and one ledger-recorded result. Exact-match reports seeds 0–4 on a Nebius 8×H100 instance. Each row lists the measured mean loss and sample count.

The original-source reproductions on our 8×H100 machine each used **one seed42 run**:

| Original strategy | Steps | Time | Loss | Reduction to ForgeMatch's five-run mean |
|---|---:|---:|---:|---:|
| ANVIL2 | 1194 | 40.221 s | 3.2750 | 38.09% |
| Exact-match | 688 | 48.247 s | 3.2618 | 48.39% |

For execution details, see [Reproduce](REPRODUCE.md). For exact result rows and evidence coverage, see [Evidence](EVIDENCE.md).

[Source attribution and acknowledgments](../CREDITS.md) · [MIT license](../LICENSE)
