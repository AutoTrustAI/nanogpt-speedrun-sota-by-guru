#!/usr/bin/env python3
"""Verify portable result evidence; optionally compare retained private originals."""

import argparse
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re


FIXED_SEEDS = [42, 43, 44, 45, 46]
EXECUTION_ORDER = [43, 42, 44, 45, 46]
FINAL = re.compile(
    rb"step:(\d+)/(\d+) val_loss:([0-9.]+) train_time:(\d+)ms step_avg:[0-9.]+ms"
)
PROGRESS = re.compile(
    rb"step:\d+/\d+ (?:val_loss:[0-9.]+ )?train_time:\d+ms step_avg:[0-9.]+ms\r?\n?"
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def verify(root, raw_root=None):
    manifest = read_json(root / "provenance/benchmark-evidence.json")
    document = read_json(root / "results/cohorts.json")
    listed = manifest["portable_files_sha256"]
    actual = {str(p.relative_to(root)) for p in (root / "results").rglob("*") if p.is_file()}
    require(set(listed) == actual, "Portable results file inventory differs")
    for name, expected in listed.items():
        require(digest(root / name) == expected, f"Portable file hash mismatch: {name}")
    require(len(manifest["source_file_sha256"]) == 33, "Expected 33 original model sources")
    for name, expected in manifest["source_file_sha256"].items():
        require(digest(root / "model" / name) == expected, f"Model source mismatch: {name}")
    require(document["fixed_seeds"] == FIXED_SEEDS, "Wrong fixed seed set")
    require(document["execution_seed_order"] == EXECUTION_ORDER, "Wrong execution order")
    cohorts = document["cohorts"]
    expected_ids = {f"coordinated-pageable{steps}-five-v1" for steps in (652, 656)}
    require(len(cohorts) == 2 and {c["id"] for c in cohorts} == expected_ids, "Wrong cohorts")
    provenance = {r["label"]: r for r in manifest["runs"]}
    require(len(provenance) == len(manifest["runs"]) == 10, "Duplicate or missing run provenance")
    cohort_provenance = {c["id"]: c for c in manifest["cohorts"]}
    require(len(cohort_provenance) == 2 and set(cohort_provenance) == expected_ids, "Wrong cohort provenance")
    seen = set()
    for cohort in cohorts:
        cid = cohort["id"]
        steps = cohort["steps"]
        require(cid == f"coordinated-pageable{steps}-five-v1", "Cohort/step mismatch")
        require(cohort["status"] == "completed", f"Incomplete cohort: {cid}")
        require(cohort["fixed_seeds"] == FIXED_SEEDS, f"Seed declaration mismatch: {cid}")
        require(cohort["execution_seed_order"] == EXECUTION_ORDER, f"Execution declaration mismatch: {cid}")
        require([r["seed"] for r in cohort["rows"]] == FIXED_SEEDS, f"Missing/duplicate/reordered seed row: {cid}")
        times, losses = [], []
        for row in cohort["rows"]:
            label = row["label"]
            require(label == f"coordinated-pageable{steps}-s{row['seed']}-v1", "Run label mismatch")
            require(label not in seen, f"Duplicate run: {label}")
            seen.add(label)
            require(row["status"] == "completed" and row["exit_code"] == 0, f"Run not completed: {label}")
            require(row["steps"] == steps, f"Run steps mismatch: {label}")
            record = provenance[label]
            require(row["source_commit"] == record["source_commit"] == cohort["source_commit"] == manifest["source_commit"], f"Source commit mismatch: {label}")
            require(record["excerpt"]["path"] == row["performance_excerpt"], f"Excerpt path mismatch: {label}")
            path = root / row["performance_excerpt"]
            require(digest(path) == record["excerpt"]["sha256"], f"Excerpt hash mismatch: {label}")
            lines = path.read_bytes().splitlines(keepends=True)
            require(lines and all(PROGRESS.fullmatch(line) for line in lines), f"Unexpected excerpt line: {label}")
            finals = [FINAL.fullmatch(line.rstrip(b"\r\n")) for line in lines]
            finals = [match for match in finals if match]
            require(len(finals) == 1 and FINAL.fullmatch(lines[-1].rstrip(b"\r\n")), f"Expected exactly one final validation: {label}")
            done, total, loss, milliseconds = finals[0].groups()
            require(int(done) == int(total) == steps, f"Final validation step mismatch: {label}")
            elapsed = Decimal(int(milliseconds)) / 1000
            loss = Decimal(loss.decode())
            require(elapsed == Decimal(row["train_seconds"]) and loss == Decimal(row["val_loss"]), f"Final validation score mismatch: {label}")
            times.append(elapsed)
            losses.append(loss)
            require(len(record["original_performance_sources"]) == 2, f"Expected console and native provenance: {label}")
            for original in record["original_performance_sources"]:
                numbers = original["one_based_selected_lines"]
                require(len(numbers) == len(lines) and numbers == sorted(set(numbers)) and min(numbers) > 0, f"Invalid original line map: {label}")
                require(original["selected_lines_sha256"] == digest(path), f"Original excerpt digest mismatch: {label}")
                if raw_root is not None:
                    raw = raw_root / "evidence/runs" / label / original["artifact"]
                    require(digest(raw) == original["sha256"], f"Raw log hash mismatch: {label}")
                    raw_lines = raw.read_bytes().splitlines(keepends=True)
                    require(b"".join(raw_lines[n - 1] for n in numbers) == path.read_bytes(), f"Original lines mismatch: {label}")
                    require(b"".join(line for line in raw_lines if PROGRESS.fullmatch(line)) == path.read_bytes(), f"Progress lines were omitted: {label}")
            if raw_root is not None:
                result = raw_root / "evidence/runs" / label / "result.json"
                require(digest(result) == record["original_result_sha256"], f"Raw result hash mismatch: {label}")
                archive = record["raw_evidence_archive"]
                require(digest(raw_root / archive["filename"]) == archive["sha256"], f"Raw run archive mismatch: {label}")
        stats = {"n": 5, "mean_seconds": sum(times) / 5, "range_seconds": max(times) - min(times), "min_seconds": min(times), "max_seconds": max(times), "mean_loss": sum(losses) / 5, "max_loss": max(losses)}
        require(set(cohort["statistics"]) == set(stats), f"Statistics schema mismatch: {cid}")
        for key, value in stats.items():
            require(Decimal(str(cohort["statistics"][key])) == value, f"Statistics mismatch: {cid}/{key}")
        conditions = {"all_losses_le_3_28": max(losses) <= Decimal("3.28"), "mean_seconds_le_25": sum(times) / 5 <= 25, "range_seconds_le_5": max(times) - min(times) <= 5}
        require(cohort["local_goal_conditions"] == conditions and cohort["local_goal_pass"] == all(conditions.values()), f"Goal decision mismatch: {cid}")
        mean_loss = sum(losses) / 5
        sample_sd = (sum((v - mean_loss) ** 2 for v in losses) / 4).sqrt()
        t = float((Decimal("3.28") - mean_loss) / (sample_sd / Decimal(5).sqrt()))
        u = t / math.sqrt(4 + t * t)
        p = (1 - u) ** 2 * (u + 2) / 4
        require(abs(t - cohort["loss_test"]["t_statistic"]) < 1e-9 and abs(p - cohort["loss_test"]["p_value"]) < 1e-12, f"Loss test arithmetic mismatch: {cid}")
        entry = cohort_provenance[cid]
        audit = read_json(root / entry["audit_summary"])
        require(audit["status"] == "VERIFIED_COMPLETE" and audit["verified_count"] == 5 and audit["all_five_evidence_verified"] is True and audit["global_errors"] == [] and audit["unfinalized_pins"] == [], f"Audit summary incomplete: {cid}")
        require(audit["cohort_id"] == cid and audit["fixed_steps"] == steps and audit["fixed_head"] == manifest["source_commit"], f"Audit identity mismatch: {cid}")
        require(audit["original_report_sha256"] == entry["original_audit_report_sha256"] and audit["original_auditor_sha256"] == entry["original_auditor_sha256"], f"Audit provenance mismatch: {cid}")
        for key, value in stats.items():
            require(Decimal(str(audit["five_seed_metrics"][key])) == value, f"Audit arithmetic mismatch: {cid}/{key}")
        require(audit["numerical_goal_conditions"] == conditions and audit["goal_pass"] == all(conditions.values()), f"Audit goal mismatch: {cid}")
        if raw_root is not None:
            require(digest(raw_root / audit["original_report_filename"]) == audit["original_report_sha256"], f"Raw audit mismatch: {cid}")
            require(digest(raw_root / audit["original_auditor_filename"]) == audit["original_auditor_sha256"], f"Raw auditor mismatch: {cid}")
            archive = entry["raw_cohort_archive"]
            require(digest(raw_root / archive["filename"]) == archive["sha256"], f"Raw cohort archive mismatch: {cid}")
        print(f"PASS {cid}: n=5, mean={stats['mean_seconds']} s, range={stats['range_seconds']} s, max loss={stats['max_loss']}, local goal={all(conditions.values())}")
    require(seen == set(provenance), "Unused or missing run provenance")
    print("PASS portable evidence consistency.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--raw-archive-root", type=Path, help="Optional private archive directory containing evidence/, original audits and tar files")
    args = parser.parse_args()
    try:
        verify(args.root, args.raw_archive_root)
    except (ValueError, KeyError, OSError, IndexError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
