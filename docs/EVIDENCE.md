# Results and evidence

The completed 652-step cohort averaged **24.8998 seconds**, with a **0.071-second** fastest-to-slowest spread. All five fixed seeds reached validation loss ≤3.28; the mean loss was **3.27498**, and the worst was **3.2777**. This satisfies our local target of a mean ≤25 seconds and a spread ≤5 seconds. It is not an accepted official record or an independent reproduction by a third party.

| Seed | 652 steps: seconds | 652 steps: loss | 656 steps: seconds | 656 steps: loss |
|---|---:|---:|---:|---:|
| 42 | 24.908 | 3.2733 | 25.018 | 3.2718 |
| 43 | 24.898 | 3.2777 | 25.019 | 3.2769 |
| 44 | 24.868 | 3.2752 | 25.049 | 3.2742 |
| 45 | 24.939 | 3.2732 | 25.000 | 3.2730 |
| 46 | 24.886 | 3.2755 | 24.941 | 3.2735 |
| Mean | **24.8998** | **3.27498** | **25.0054** | **3.27388** |

The 656-step cohort narrowly missed the local time target by 0.0054 seconds. Its time spread was 0.108 seconds. The 652-step cohort's mean was 0.1056 seconds lower (approximately 0.4223%); the average loss increased by 0.00110. These are separate complete cohorts; their runs were never pooled to create a faster result.

Both cohorts used seeds 42–46, preregistered before their first run, in execution order 43, 42, 44, 45, 46. Every planned seed appears once. No slow run was discarded or replaced. Both used the same archived source commit, `d7b6a09512010189292974b3a9b9f19c111d9b38`, and the same 33 model source files. The 652-step run count reschedules the training schedule; it is not simply a truncated 656-step run. It also used a different fresh local SSD cache filesystem. The first 652-step run preceded the remaining four by several hours because of an SSH connectivity interruption. These facts limit causal attribution of the timing difference.

The timed metric is the **final validation line's `train_time`**, including the terminal model averaging and retrieval completion performed before the timer is stopped. It is not the earlier last-update progress time, and it is not total launcher wall time. Compilation, warmup and validation time are excluded by the archived trainer's timing convention. The original runs were unprofiled, on eight H100 GPUs; each source inventory was checked before and after execution in the private audit.

## What this repository contains

- [`results/cohorts.json`](../results/cohorts.json): ten completed runs, exact decimal summary statistics, the local target decision, and loss-test results.
- [`results/logs/`](../results/logs/): selected original progress and final-validation lines for every run. Each file contains all lines matching the trainer's `step:... train_time:...` progress/final-validation format, in their original order and with their original bytes. The console and native log excerpts were verified to match.
- [`results/audit-summaries/`](../results/audit-summaries/): allowlisted summaries derived from the completed private audits. These are not copies of the complete audit reports.
- [`results/lineage.json`](../results/lineage.json): three immediate predecessor cohorts. The failed release-v1 cohort retains both successful runs, the seed44 warmup failure caused by exhausted cache filesystem inodes, and the never-started seed45/46 slots. Its two successes are not treated as a complete five-seed result and were not reused in release-v2.
- [`provenance/benchmark-evidence.json`](../provenance/benchmark-evidence.json): hashes of portable result files, all 33 model sources, original console/native logs and result records, private raw archives, original audit reports and auditors, plus original line-number maps for the excerpts.

This is **selected, derived portable evidence**, not the complete raw audit bundle. Full raw logs, embedded source snapshots, source inventories, preregistration records, launch/controller state, strategy files, failed experiment records and archives remain in the private workspace and storage. This compact export is not the complete historical experiment ledger. Raw archive hashes identify retained originals; they are not public download links or signatures. The repository removes host addresses and private filesystem paths by selecting safe fields and log lines, not by changing the selected performance lines.

## Verify the package

From the repository root, with Python 3:

```sh
python3 scripts/verify_results.py
```

This checks every portable result hash, all 33 original model file hashes, seed coverage, unique run labels, final validation steps, final score extraction, exact decimal cohort statistics, the goal decisions, and the loss-test arithmetic. It does not require a GPU or access to the private originals. With access to the retained private archive directory, also run:

```sh
python3 scripts/verify_results.py --raw-archive-root /path/to/private/archive
```

The optional mode additionally verifies original log/result/archive/report/auditor hashes and proves that the published excerpts exactly match all selected lines in both original logs. It still does not reproduce the training or repeat every check performed by the original full audit. The files and their hashes are maintained by the same author; internal consistency is not independent authentication.

The one-sided Student t-test uses a null mean loss of 3.28 and four degrees of freedom. The 652-step result has p≈0.00187 and the 656-step result p≈0.000988. Independent sampling and an approximately normal sampling distribution are assumptions, not facts established by five fixed seeds. These cohorts followed adaptive optimization; the p-values do not correct for strategy selection, establish a holdout result, or confer official acceptance. Every individual loss must still meet the local threshold.
