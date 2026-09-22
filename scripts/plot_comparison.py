#!/usr/bin/env python3
"""Render the README comparison as SVG and PNG using Matplotlib.

Run from any directory: python3 scripts/plot_comparison.py
Requires matplotlib. The chart reads the measured local cohort directly and
the public reference values from assets/comparison-data.json.
"""

import json
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MultipleLocator


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DATA = json.loads((ASSETS / "comparison-data.json").read_text())
RESULTS = json.loads((ROOT / DATA["local_results"]).read_text())
COHORT = next(c for c in RESULTS["cohorts"] if c["id"] == DATA["local_cohort"])
STATS = COHORT["statistics"]
local_times = [Decimal(row["train_seconds"]) for row in COHORT["rows"]]
assert sum(local_times) / len(local_times) == Decimal(STATS["mean_seconds"])
assert max(local_times) - min(local_times) == Decimal(STATS["range_seconds"])

rows = [{
    "method": "ForgeMatch",
    "affiliation": "ScienceGuru + Guru Turbo 1.2",
    "seconds": STATS["mean_seconds"],
    "approximate": False,
    "local": True,
}, *DATA["public_results"]]
rows.sort(key=lambda row: Decimal(row["seconds"]))
for row in rows:
    if "source_minutes" in row:
        assert Decimal(row["seconds"]) == Decimal(row["source_minutes"]) * 60

INK = "#14243B"
MUTED = "#66768B"
ACCENT = "#008A80"
GRID = "#E4EAF1"
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "svg.fonttype": "none",
    "svg.hashsalt": "forgematch-comparison-v1",
    "axes.unicode_minus": False,
})
fig = plt.figure(figsize=(16, 10), facecolor="white")
ax = fig.add_axes((0.305, 0.19, 0.65, 0.60), facecolor="none")
ax.set_xlim(0, 216)
ax.set_ylim(len(rows) - 0.35, -0.65)
ax.xaxis.set_major_locator(MultipleLocator(50))
ax.tick_params(axis="x", colors=MUTED, length=0, pad=13, labelsize=13)
ax.set_yticks([])
ax.set_axisbelow(True)
ax.grid(axis="x", color=GRID, linewidth=0.9)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.axvline(0, color="#CBD5E1", linewidth=1)
ax.set_xlabel("Reported training time (seconds)", color=MUTED, labelpad=20, fontsize=13)

fig.text(0.035, 0.952, "SCIENCEGURU + GURU TURBO 1.2", color=ACCENT,
         fontsize=14, weight="bold")
fig.text(0.035, 0.895, "NanoGPT training-time comparison", color=INK,
         fontsize=29, weight="bold")
fig.text(0.035, 0.851,
         "8× H100  ·  FineWeb validation loss ≤ 3.28  ·  Lower is better",
         color=MUTED, fontsize=15)

for i, row in enumerate(rows):
    local = row.get("local", False)
    center_y = fig.transFigure.inverted().transform(ax.transData.transform((0, i)))[1]
    if local:
        fig.add_artist(FancyBboxPatch(
            (0.022, center_y - 0.034), 0.955, 0.068,
            boxstyle="round,pad=0.009,rounding_size=0.012",
            linewidth=0, facecolor="#E9F7F4", transform=fig.transFigure, zorder=-1,
        ))
    color = ACCENT if local else "#B5C6DC"
    ax.barh(i, float(row["seconds"]), height=0.42, color=color,
            edgecolor="none", zorder=3)
    fig.text(0.035, center_y + 0.006, row["method"],
             color=ACCENT if local else INK, fontsize=17, weight="bold", va="center")
    fig.text(0.035, center_y - 0.019, row["affiliation"],
             color=ACCENT if local else MUTED, fontsize=11.5, va="center")
    value = ("≈" if row["approximate"] else "") + row["seconds"] + " s"
    ax.text(float(row["seconds"]) + 3.1, i, value, va="center", ha="left",
            color=ACCENT if local else INK, fontsize=16,
            weight="bold" if local else "normal", zorder=4)

fig.text(0.035, 0.070,
         f"ForgeMatch  ·  {STATS['n']} seeds  ·  {COHORT['steps']} steps  ·  "
         f"{STATS['range_seconds']} s run-to-run range",
         fontsize=13, color=INK, weight="normal")
fig.text(0.035, 0.033,
         f"Selected reported results  ·  Sources: Research baselines  ·  {DATA['as_of']}",
         fontsize=11, color=MUTED)

ASSETS.mkdir(exist_ok=True)
svg_path = ASSETS / "benchmark-comparison.svg"
fig.savefig(svg_path, facecolor="white", metadata={"Date": None})
fig.savefig(ASSETS / "benchmark-comparison.png", dpi=150, facecolor="white")
plt.close(fig)

# Preserve selectable English text and provide accessible SVG descriptions.
ET.register_namespace("", "http://www.w3.org/2000/svg")
tree = ET.parse(svg_path)
svg = tree.getroot()
svg.set("role", "img")
svg.set("aria-labelledby", "chart-title chart-description")
title = ET.Element("{http://www.w3.org/2000/svg}title", {"id": "chart-title"})
title.text = "NanoGPT training-time comparison"
description = ET.Element("{http://www.w3.org/2000/svg}desc", {"id": "chart-description"})
description.text = "; ".join(
    row["method"] + ": " + ("approximately " if row["approximate"] else "")
    + row["seconds"] + " seconds" for row in rows
) + ". Sources and experimental context are documented in docs/BASELINES.md."
svg.insert(0, description)
svg.insert(0, title)
tree.write(svg_path, encoding="utf-8", xml_declaration=True)
print(f"Rendered {len(rows)} results to assets/benchmark-comparison.svg and .png")
