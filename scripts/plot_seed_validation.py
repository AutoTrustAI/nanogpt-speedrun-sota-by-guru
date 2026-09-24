#!/usr/bin/env python3
"""Render the ScienceGuru five-seed NanoGPT results from the archived cohort.

Run from any directory: python3 scripts/plot_seed_validation.py
Requires matplotlib. Source values and statistics remain in results/cohorts.json.
"""

import json
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MultipleLocator


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
RESULTS = json.loads((ROOT / "results" / "cohorts.json").read_text())
COHORT = next(c for c in RESULTS["cohorts"] if c["id"] == "coordinated-pageable652-five-v1")
STATS = COHORT["statistics"]
ROWS = sorted(COHORT["rows"], key=lambda row: row["seed"])
TIMES = [Decimal(row["train_seconds"]) for row in ROWS]
LOSSES = [Decimal(row["val_loss"]) for row in ROWS]
LOSS_LIMIT = Decimal(RESULTS["local_target"]["max_loss_each"])
TIME_GUIDE = Decimal(RESULTS["local_target"]["max_mean_train_seconds"])
COMPLETION_DATE = max(row["completed_utc"] for row in ROWS)[:10]

assert [row["seed"] for row in ROWS] == RESULTS["fixed_seeds"]
assert len(ROWS) == STATS["n"] == 5
assert all(row["status"] == "completed" and row["exit_code"] == 0 for row in ROWS)
assert all(row["steps"] == COHORT["steps"] == 652 for row in ROWS)
assert sum(TIMES) / len(TIMES) == Decimal(STATS["mean_seconds"]) == Decimal("24.8998")
assert sum(LOSSES) / len(LOSSES) == Decimal(STATS["mean_loss"]) == Decimal("3.27498")
assert max(TIMES) - min(TIMES) == Decimal(STATS["range_seconds"]) == Decimal("0.071")
assert all(value < TIME_GUIDE for value in TIMES)
assert all(value <= LOSS_LIMIT for value in LOSSES)

# AutoTrust's public website palette; text branding only, no reproduced logo.
ACCENT = "#1F4B41"
SECONDARY = "#2C5E52"
BACKGROUND = "#FAF6EC"
CARD = "#FFFDF7"
INK = "#1C2A25"
MUTED = "#66776D"
GRID = "#DDE4D9"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 13,
    "svg.fonttype": "none",
    "svg.hashsalt": "scienceguru-five-seeds-v1",
    "axes.unicode_minus": False,
})
fig = plt.figure(figsize=(20, 8), facecolor=BACKGROUND)
time_ax = fig.add_axes((0.084, 0.285, 0.380, 0.396), facecolor=CARD)
loss_ax = fig.add_axes((0.584, 0.285, 0.375, 0.396), facecolor=CARD)
positions = list(range(len(ROWS)))

fig.text(0.045, 0.945, "AutoTrust · ScienceGuru · Guru Turbo 1.2",
         color=ACCENT, fontsize=16, weight="bold")
fig.text(0.045, 0.863, "Five seeds. Five passes.",
         color=INK, fontsize=37, weight="bold")
fig.text(0.045, 0.807,
         "NanoGPT training  ·  8× H100  ·  FineWeb  ·  652 steps  ·  Seeds 42–46",
         color=MUTED, fontsize=16)
fig.text(0.084, 0.735, "Training time", color=INK, fontsize=20, weight="bold")
fig.text(0.584, 0.735, "Validation loss", color=INK, fontsize=20, weight="bold")

for ax in (time_ax, loss_ax):
    ax.set_ylim(len(ROWS) - 0.45, -0.55)
    ax.set_yticks(positions, [f"Seed {row['seed']}" for row in ROWS])
    ax.tick_params(axis="y", colors=INK, length=0, pad=14, labelsize=14)
    ax.tick_params(axis="x", colors=MUTED, length=0, pad=12, labelsize=13)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=GRID, linewidth=0.9)
    for spine in ax.spines.values():
        spine.set_visible(False)

time_ax.set_xlim(0, 27)
time_ax.xaxis.set_major_locator(MultipleLocator(5))
time_ax.set_xlabel("Training time (seconds)", color=MUTED, labelpad=15, fontsize=14)
time_ax.barh(positions, [float(value) for value in TIMES],
             height=0.53, color=ACCENT, edgecolor="none", zorder=3)
time_ax.axvline(float(TIME_GUIDE), color=SECONDARY, linewidth=1.4,
               linestyle=(0, (4, 3)), zorder=4)
time_ax.text(float(TIME_GUIDE), 1.045, "25 s guide", transform=time_ax.get_xaxis_transform(),
             color=SECONDARY, fontsize=12, ha="right", va="bottom")
for i, row in enumerate(ROWS):
    time_ax.text(float(row["train_seconds"]) - 0.50, i, row["train_seconds"] + " s",
                 ha="right", va="center", color=CARD, fontsize=15, weight="bold", zorder=5)

loss_ax.set_xlim(3.270, 3.282)
loss_ax.set_xticks([3.270, 3.274, 3.278, 3.282])
loss_ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
loss_ax.set_xlabel("Final validation loss", color=MUTED, labelpad=15, fontsize=14)
loss_ax.axvline(float(LOSS_LIMIT), color=SECONDARY, linewidth=1.4,
               linestyle=(0, (4, 3)), zorder=2)
loss_ax.text(float(LOSS_LIMIT), 1.045, "3.28 pass threshold",
             transform=loss_ax.get_xaxis_transform(), color=SECONDARY,
             fontsize=12, ha="center", va="bottom")
for i, row in enumerate(ROWS):
    value = float(row["val_loss"])
    loss_ax.hlines(i, 3.270, value, color=GRID, linewidth=1.8, zorder=1)
    loss_ax.scatter(value, i, s=112, facecolor=ACCENT, edgecolor=CARD, linewidth=1.5, zorder=3)
    loss_ax.text(value + 0.00035, i, row["val_loss"], color=ACCENT,
                 fontsize=15, weight="bold", va="center", ha="left", zorder=4)

fig.add_artist(Line2D([0.045, 0.959], [0.169, 0.169], transform=fig.transFigure,
                      color=GRID, linewidth=1))
summary = [
    (0.045, STATS["mean_seconds"] + " s", "Mean training time  ·  " + STATS["range_seconds"] + " s run-to-run range"),
    (0.398, STATS["mean_loss"], "Mean final validation loss"),
    (0.706, "5 of 5 pass", "Every run: loss ≤ 3.28 and training time < 25 s"),
]
for x, value, label in summary:
    fig.text(x, 0.107, value, color=ACCENT, fontsize=28, weight="bold")
    fig.text(x, 0.065, label, color=MUTED, fontsize=12)
fig.text(0.045, 0.022,
         f"Source: results/cohorts.json  ·  Measured {COMPLETION_DATE}  ·  "
         "Training interval excludes compilation, warmup and validation.",
         color=MUTED, fontsize=10.5)

ASSETS.mkdir(exist_ok=True)
svg_path = ASSETS / "seed-validation.svg"
png_path = ASSETS / "seed-validation.png"
fig.savefig(svg_path, facecolor=BACKGROUND, metadata={"Date": None})
fig.savefig(png_path, dpi=240, facecolor=BACKGROUND)
plt.close(fig)

ET.register_namespace("", "http://www.w3.org/2000/svg")
tree = ET.parse(svg_path)
svg = tree.getroot()
svg.set("role", "img")
svg.set("aria-labelledby", "chart-title chart-description")
title = ET.Element("{http://www.w3.org/2000/svg}title", {"id": "chart-title"})
title.text = "AutoTrust · ScienceGuru · Guru Turbo 1.2: Five seeds. Five passes."
description = ET.Element("{http://www.w3.org/2000/svg}desc", {"id": "chart-description"})
description.text = (
    "Measured NanoGPT training on 8 H100 GPUs, FineWeb, 652 steps. "
    + "; ".join(
        f"Seed {row['seed']}: training time {row['train_seconds']} seconds, final validation loss {row['val_loss']}"
        for row in ROWS
    )
    + f". Mean training time {STATS['mean_seconds']} seconds, range {STATS['range_seconds']} seconds. "
    + f"Mean final validation loss {STATS['mean_loss']}. All five runs have loss at most 3.28 "
    + f"and training time below 25 seconds. Measured {COMPLETION_DATE}. "
    + "Source: results/cohorts.json. Compilation, warmup and validation are outside the measured training interval."
)
svg.insert(0, description)
svg.insert(0, title)
tree.write(svg_path, encoding="utf-8", xml_declaration=True)
print(f"Rendered {len(ROWS)} verified seeds to {svg_path.name} and {png_path.name}")
print(f"Mean time: {STATS['mean_seconds']} s; mean loss: {STATS['mean_loss']}; range: {STATS['range_seconds']} s")
