# Results and evidence

**AutoTrust · ScienceGuru · Guru Turbo 1.2 experiment results.** See [project attribution](../provenance/project-attribution.json), source records, and benchmark evidence below.

The completed 652-step cohort averaged **24.8998 seconds**, with a **0.071-second** fastest-to-slowest spread. All five fixed seeds reached validation loss ≤3.28; the mean loss was **3.27498**, and the worst was **3.2777**. This satisfies the target of a mean ≤25 seconds and a spread ≤5 seconds.

| Seed | 652 steps: seconds | 652 steps: loss | 656 steps: seconds | 656 steps: loss |
|---|---:|---:|---:|---:|
| 42 | 24.908 | 3.2733 | 25.018 | 3.2718 |
| 43 | 24.898 | 3.2777 | 25.019 | 3.2769 |
| 44 | 24.868 | 3.2752 | 25.049 | 3.2742 |
| 45 | 24.939 | 3.2732 | 25.000 | 3.2730 |
| 46 | 24.886 | 3.2755 | 24.941 | 3.2735 |
| Mean | **24.8998** | **3.27498** | **25.0054** | **3.27388** |

The 656-step cohort averaged 25.0054 seconds, with a 0.108-second spread. The 652-step cohort's mean was 0.1056 seconds lower (approximately 0.4223%); the average loss increased by 0.00110. Each cohort is summarized separately.

Both cohorts used seeds 42–46, preregistered before their first run, in execution order 43, 42, 44, 45, 46. Every planned seed appears once. Both used the same archived source commit, `d7b6a09512010189292974b3a9b9f19c111d9b38`, and the same 33 model source files. The 652-step configuration rescales the training schedule and used a fresh local SSD cache filesystem. The first 652-step run preceded the remaining four by several hours because of an SSH connectivity interruption.

The timed metric is the **final validation line's `train_time`**, including the terminal model averaging and retrieval completion performed before the timer is stopped. Compilation, warmup and validation occur outside this interval. The original runs were unprofiled, on eight H100 GPUs; each source inventory was checked before and after execution.

## What this repository contains

- [`results/cohorts.json`](../results/cohorts.json): ten completed runs, exact decimal summary statistics, the local target decision, and loss-test results.
- [`results/logs/`](../results/logs/): selected original progress and final-validation lines for every run. Each file contains all lines matching the trainer's `step:... train_time:...` progress/final-validation format, in their original order and with their original bytes. The console and native log excerpts were verified to match.
- [`results/audit-summaries/`](../results/audit-summaries/): summaries derived from the completed audits.
- [`results/lineage.json`](../results/lineage.json): three immediate predecessor cohorts. The release-v1 record contains two successful runs, the seed44 warmup failure caused by exhausted cache filesystem inodes, and the never-started seed45/46 slots. The complete release-v2 cohort contains five fresh runs.
- [`provenance/benchmark-evidence.json`](../provenance/benchmark-evidence.json): hashes of portable result files, all 33 model sources, original console/native logs and result records, private raw archives, original audit reports and auditors, plus original line-number maps for the excerpts.

The package contains selected original log lines and derived audit summaries. Full raw logs, embedded source snapshots, source inventories, preregistration records, launch/controller state, strategy files, failed experiment records and archives are retained in the experiment workspace and storage. Raw archive hashes identify those originals. Published performance lines preserve their original bytes.

## Verify the package

From the repository root, with Python 3:

```sh
python3 scripts/verify_results.py
```

This CPU-only check verifies every portable result hash, all 33 original model file hashes, seed coverage, unique run labels, final validation steps, final score extraction, exact decimal cohort statistics, the goal decisions, and the loss-test arithmetic. To also verify the retained raw archive directory, run:

```sh
python3 scripts/verify_results.py --raw-archive-root /path/to/private/archive
```

The optional mode additionally verifies original log/result/archive/report/auditor hashes and checks that the published excerpts exactly match all selected lines in both original logs. GPU execution is described in [Reproduce](REPRODUCE.md).

The one-sided Student t-test uses a null mean loss of 3.28 and four degrees of freedom, assuming independent samples and an approximately normal sampling distribution. The 652-step result has p≈0.00187 and the 656-step result p≈0.000988. The same fixed seeds were used during adaptive development. Every individual loss also meets the threshold.
