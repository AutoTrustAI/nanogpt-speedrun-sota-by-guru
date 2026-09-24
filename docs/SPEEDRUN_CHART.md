# NanoGPT Speedrun charts

The history charts place this repository's **24.8998-second five-seed mean** after the public NanoGPT Track 1 history at the common **8 × H100 / FineWeb validation loss ≤3.28** target. They show other contributors' historical results, two selected public submissions, and the final ScienceGuru cohort; they do not plot ScienceGuru's internal tuning sequence.

## Files and reproduction

- [Full history PNG](../assets/speedrun-history.png) · [SVG](../assets/speedrun-history.svg): official records from May 2024 onward, plus the selected submissions and ScienceGuru.
- [Recent history PNG](../assets/speedrun-history-recent.png) · [SVG](../assets/speedrun-history-recent.svg): official records from October 2025 onward, plus the same selected submissions and ScienceGuru.
- [Training-time comparison PNG](../assets/benchmark-comparison.png) · [SVG](../assets/benchmark-comparison.svg): a direct comparison of ScienceGuru with the selected public baselines, making the size of the training-time differences easier to compare.
- [Five-seed validation PNG](../assets/seed-validation.png) · [SVG](../assets/seed-validation.svg): every final ScienceGuru seed's training time and validation loss, showing timing consistency and all five results relative to the loss ≤3.28 target.
- [Historical source data](../assets/speedrun-history-data.json): all 91 numbered official records, both re-timings of record #21, and the two selected submissions.
- [ScienceGuru result data](../results/cohorts.json): the final `coordinated-pageable652-five-v1` cohort, with all five seeds retained.

Regenerate the images from the repository root with Python and Matplotlib:

```sh
python3 scripts/plot_speedrun_history.py
python3 scripts/plot_comparison.py
python3 scripts/plot_seed_validation.py
```

The scripts write both SVG and PNG outputs. The first creates full-history and recent-history variants. The comparison chart reads public values from [comparison-data.json](../assets/comparison-data.json); both the comparison and validation charts read ScienceGuru's final cohort from [cohorts.json](../results/cohorts.json).

## AutoTrust visual style

The palette follows the [AutoTrust website](https://autotrust.ai/) and its [official stylesheet](https://autotrust.ai/assets/index-D1dJKNGO.css): primary green **`#1F4B41`**, warm background **`#FAF6EC`**, and card background **`#FFFDF7`**. ScienceGuru uses the primary green across the history, comparison, and validation views. The public-history values and experiment records remain the sources of the plotted measurements.

## Sources and dates

The official history is transcribed from the first **World record history** table in the [upstream README at commit `bc3a0c2`](https://github.com/KellerJordan/modded-nanogpt/blob/bc3a0c2d640d0d73dedaef87eae26148d2e32afb/README.md#world-record-history). The retrieved README's Git blob SHA is `7df95e21a027b5f6db4f3b6c20b6b7e7805a56b6`; the JSON records the retrieval time. The table contains **93 rows: records #1–#91 and two additional measurements of #21**. Each row retains the original minute string, description, contributor cell, date, and a source link. Source links prefer the listed PR, then the archived log. Records #3 and #66 have no listed PR or log, so their source links point to the exact README lines.

Dates on official points are the dates in that table, converted from `MM/DD/YY` to ISO dates. The two submission points use their GitHub PR creation dates in UTC:

| Selected public submission | PR creation date (UTC) | Reported mean | Status when checked |
|---|---|---:|---|
| [ANVIL2, PR #360](https://github.com/KellerJordan/modded-nanogpt/pull/360) | 2026-08-31 | 39.914 s | Open; not merged |
| [Exact-match, PR #367](https://github.com/KellerJordan/modded-nanogpt/pull/367) | 2026-09-17 | 47.2056 s | Open; not merged |

ANVIL2's exact time is stated in its PR body; Exact-match's exact time comes from the author's [pinned five-run statistics](https://github.com/hermabr/modded-nanogpt-public/blob/3e92b0e28293dcb184197da1a0ce1f543e84f76c/records/track_1_short/2026-09-16_ExactMatch/this_pr/statistics.md). These values agree with [comparison-data.json](../assets/comparison-data.json). Submission dates identify public posting, rather than the precise dates the experiments ran. The submission series is separate from the accepted upstream history and must not be presented as accepted records.

ScienceGuru's point uses **2026-09-22**, the UTC date on which all five runs of the final cohort had completed. Its mean is **24.8998 s**, its range is **24.868–24.939 s**, and all five validation losses are ≤3.28 (mean **3.27498**, worst **3.2777**). It is a result reported by this repository, **not an accepted upstream record**. The plot's star and connecting comparison guide do not imply acceptance into the official leaderboard.

## Reading the comparison

Official times are converted with decimal arithmetic from the leaderboard's published, rounded minutes (`seconds = minutes × 60`). Those second values and comparisons derived from them are approximate: for example, record #91 is **1.126 min ≈67.56 s**. The chart labels use **≈** for these official values rather than suggesting additional measurement precision.

The two extra rows for #21 are explicitly re-timings under updated rules and a newer PyTorch version, not new records. They remain identified as re-timings in the data and should not be counted as additional improvements. Their increases in measured time are retained; the full history must not silently replace them with a monotonically decreasing minimum.

This is the complete official history in the captured table, plus **two selected public submissions** and **one final local cohort**. It is not a catalog of every submission, failed PR, unpublished experiment, or internal optimization trial. The shared hardware class and loss threshold do not make these runs a controlled comparison on identical machines, software versions, sample counts, or validation losses. In particular, ANVIL2 reports 18 runs, Exact-match reports five runs, and ScienceGuru reports five fixed seeds. See [Baselines](BASELINES.md) and [Evidence](EVIDENCE.md) for those distinctions and the timing interval.
