#!/usr/bin/env python3
"""Render community NanoGPT record history, with our measured result at the end.

Run from anywhere: python3 scripts/plot_speedrun_history.py
Data and scope: docs/SPEEDRUN_CHART.md. Requires Matplotlib.
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
# Primary / background / card / ink values from AutoTrust's official CSS.
# https://autotrust.ai/assets/index-D1dJKNGO.css
ACCENT = "#1F4B41"
BACKGROUND = "#FAF6EC"
CARD = "#FFFDF7"
HISTORY = "#8B9F85"
HISTORY_LIGHT = "#D2DCCB"
INK = "#1C2A25"
MUTED = "#6C7C73"
GRID = "#E1E5D9"
SUBMISSION = "#6B8B7B"


def date(value):
    return datetime.fromisoformat(value[:10])


def add_callout(ax, xy, text, offset, *, color=INK, border="#D2DACF",
                align="center", fontsize=12.5, bold=False):
    return ax.annotate(
        text, xy=xy, xytext=offset, textcoords="offset points",
        ha=align, va="center", fontsize=fontsize, color=color,
        weight="bold" if bold else "normal", linespacing=1.35,
        bbox=dict(boxstyle="round,pad=0.42,rounding_size=0.2",
                  facecolor=CARD, edgecolor=border, linewidth=1.0),
        arrowprops=dict(arrowstyle="-", color=border, lw=1.0,
                        shrinkA=5, shrinkB=7, connectionstyle="arc3"),
        annotation_clip=False, zorder=8,
    )


def svg_description(path, description):
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    tree = ET.parse(path)
    svg = tree.getroot()
    svg.set("role", "img")
    svg.set("aria-labelledby", "chart-title chart-description")
    title = ET.Element(f"{{{ns}}}title", {"id": "chart-title"})
    title.text = "AutoTrust ScienceGuru with Guru Turbo 1.2: NanoGPT Speedrun results"
    desc = ET.Element(f"{{{ns}}}desc", {"id": "chart-description"})
    desc.text = description
    svg.insert(0, title)
    svg.insert(1, desc)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def render(data, cohort, recent=False):
    all_records = data["community_records"]
    selected = [r for r in all_records
                if not recent or r["date"] >= "2025-10-01"]
    records = [r for r in selected if not r["is_retiming"]]
    retimings = [r for r in selected if r["is_retiming"]]
    lookup = {r["record"]: r for r in records}
    times = [Decimal(row["train_seconds"]) for row in cohort["rows"]]
    mean = sum(times) / len(times)
    assert mean == Decimal(cohort["statistics"]["mean_seconds"])
    assert len(times) == 5
    assert all(Decimal(row["val_loss"]) <= Decimal("3.28")
               for row in cohort["rows"])
    result_date = max(date(row["completed_utc"]) for row in cohort["rows"])
    ours = float(mean)
    last = records[-1]
    latest = float(last["seconds"])
    speedup = latest / ours

    fig = plt.figure(figsize=(22, 9.4), facecolor=BACKGROUND)
    ax = fig.add_axes((0.078, 0.21, 0.862, 0.525), facecolor="none")
    fig.text(0.057, 0.947, "AutoTrust", fontsize=18, color=INK, weight="bold")
    fig.text(0.057, 0.888, "ScienceGuru · Guru Turbo 1.2",
             fontsize=31, color=INK, weight="bold")
    window = "Oct 2025 – Sep 2026" if recent else "May 2024 – Sep 2026"
    fig.text(0.057, 0.84,
             "NanoGPT Speedrun · 8× H100 · FineWeb validation loss ≤ 3.28",
             fontsize=15, color=MUTED)
    fig.text(0.958, 0.94, f"{mean} s", ha="right", fontsize=34,
             color=ACCENT, weight="bold")
    fig.text(0.958, 0.891, f"≈{speedup:.2f}× faster than official SOTA*",
             ha="right", fontsize=16, color=INK)
    fig.text(0.958, 0.852,
             f"{100 * (1 - ours / latest):.2f}% less training time · 5-seed mean",
             ha="right", fontsize=12.5, color=MUTED)
    fig.text(0.939, 0.787, f"{window} · {len(records)} community records",
             ha="right", fontsize=11.5, color=MUTED)

    xs = [date(r["date"]) for r in selected]
    ys = [float(r["seconds"]) for r in selected]
    ax.set_yscale("log")
    ax.set_ylim((19, 174) if recent else (19, 4500))
    ax.set_xlim(date("2025-09-22") if recent else date("2024-05-01"),
                date("2026-12-10") if recent else date("2027-01-10"))
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#D6DDD1", linewidth=0.95)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#D2DACF")
    ax.tick_params(axis="both", length=0, colors=MUTED, labelsize=12.5, pad=10)
    ax.yaxis.set_major_locator(FixedLocator(
        [20, 30, 40, 60, 80, 100, 120, 160] if recent
        else [20, 40, 80, 160, 300, 600, 1200, 2400]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_ylabel("Reported training time (seconds, log scale)",
                  color=INK, fontsize=14, labelpad=15)
    tick_dates = (["2025-10-01", "2025-12-01", "2026-02-01", "2026-04-01",
                   "2026-06-01", "2026-08-01", "2026-10-01"] if recent else
                  ["2024-07-01", "2024-10-01", "2025-01-01", "2025-04-01",
                   "2025-07-01", "2025-10-01", "2026-01-01", "2026-04-01",
                   "2026-07-01", "2026-10-01"])
    ax.set_xticks([date(d) for d in tick_dates])
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    # Keep the two re-timings in the historic path, including their upward moves.
    ax.step(xs, ys, where="post", color=HISTORY, lw=2.1, zorder=3)
    ax.scatter([date(r["date"]) for r in records],
               [float(r["seconds"]) for r in records],
               s=25 if recent else 20, facecolor=HISTORY_LIGHT,
               edgecolor=HISTORY, linewidth=0.85, zorder=4)
    if retimings:
        ax.scatter([date(r["date"]) for r in retimings],
                   [float(r["seconds"]) for r in retimings],
                   s=30, marker="s", facecolor=CARD, edgecolor=HISTORY,
                   linewidth=1.2, zorder=5)

    # The unmerged submissions and our result are not official leaderboard entries.
    # A curved comparison guide stays clear of the independent submission points.
    ax.annotate("", xy=(result_date, ours), xytext=(date(last["date"]), latest),
                arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=0.22",
                                color=ACCENT, linestyle=(0, (4, 3)), lw=1.5,
                                alpha=0.65, shrinkA=7, shrinkB=11), zorder=2)
    for r in data["submissions"]:
        ax.scatter(date(r["date"]), float(r["seconds"]), s=74, marker="D",
                   facecolor=CARD, edgecolor=SUBMISSION, linewidth=1.5,
                   zorder=6)

    ax.scatter(result_date, ours, marker="*", s=550, color=ACCENT,
               edgecolor=ACCENT, linewidth=1.5, zorder=10)

    if recent:
        callouts = [
            (40, "#40 · Backout + HP tuning\n≈141.5 s", (40, 23)),
            (53, "#53 · Multi-token prediction\n≈119.3 s", (-6, 48)),
            (62, "#62 · Bigram hash embedding\n≈99.3 s", (20, -53)),
            (82, "#82 · Learnable XSA\n≈81.2 s", (-30, 44)),
            (87, "#87 · Recursive ReLU² kernel\n≈75.4 s", (-20, -58)),
            (91, "#91 · Canonical token masking\n≈67.56 s · official SOTA", (20, 53)),
        ]
    else:
        callouts = [
            (1, "#1 · llm.c baseline\n≈2,700 s", (57, 11)),
            (3, "#3 · Muon optimizer\n≈1,494 s", (38, 35)),
            (12, "#12 · FlexAttention\n≈301.8 s", (-52, -47)),
            (22, "#22 · Enigma all-reduce\n≈179.4 s", (0, 44)),
            (40, "#40 · Backout + HP tuning\n≈141.5 s", (-50, -56)),
            (62, "#62 · Bigram hash embedding\n≈99.3 s", (-8, 51)),
            (87, "#87 · Recursive ReLU² kernel\n≈75.4 s", (-78, -48)),
            (91, "#91 · Canonical token masking\n≈67.56 s · official SOTA", (10, 62)),
        ]

    for record_id, text, offset in callouts:
        r = lookup[record_id]
        xy = (date(r["date"]), float(r["seconds"]))
        ax.scatter(*xy, s=92, facecolor=HISTORY_LIGHT, edgecolor=HISTORY,
                   linewidth=1.5, zorder=7)
        add_callout(ax, xy, text, offset)

    by_method = {r["method"]: r for r in data["submissions"]}
    exact = by_method["Exact-match"]
    anvil = by_method["ANVIL2"]
    add_callout(ax, (date(exact["date"]), float(exact["seconds"])),
                "Exact-match · 47.2056 s", (36, 10),
                color=SUBMISSION, border="#CDD8CC", align="left", fontsize=12)
    add_callout(ax, (date(anvil["date"]), float(anvil["seconds"])),
                "ANVIL2 · 39.914 s", (-34, -31),
                color=SUBMISSION, border="#CDD8CC", align="right", fontsize=12)

    add_callout(ax, (result_date, ours),
                f"ScienceGuru\n{mean} s · ≈{speedup:.2f}× faster*",
                (32, 4), color=ACCENT, border="#749184", align="left",
                fontsize=15, bold=True)

    handles = [
        Line2D([], [], marker="o", color=HISTORY, markerfacecolor=HISTORY_LIGHT,
               markersize=6, lw=1.6, label="Official record history"),
        Line2D([], [], marker="D", color=SUBMISSION, markerfacecolor=CARD,
               markersize=6, lw=0, label="Other reported results"),
        Line2D([], [], marker="*", color=ACCENT, markerfacecolor=ACCENT,
               markersize=12, lw=0, label="ScienceGuru"),
    ]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(0.073, 0.788),
               ncol=3, frameon=False, fontsize=12, handlelength=2.5,
               columnspacing=2.0, labelcolor=MUTED)

    fig.text(0.078, 0.12,
             "ScienceGuru + Guru Turbo 1.2: 5 seeds · 652 steps · mean loss 3.27498 · "
             "5/5 runs ≤ 3.28 · completed Sep 22, 2026",
             fontsize=13, color=INK)
    fig.text(0.078, 0.077,
             "Sources: KellerJordan/modded-nanogpt record history, PRs #360 / #367, "
             "and this repository’s five-seed logs.  *Versus official SOTA ≈67.56 s.",
             fontsize=10.7, color=MUTED)
    fig.text(0.078, 0.042,
             "Official times are rounded leaderboard minutes × 60; dates follow the source "
             "record / PR submission. "
             + ("Published results use different hosts." if recent else
                "Includes two #21 re-timings; timing rules changed after #21."),
             fontsize=10.7, color=MUTED)

    name = "speedrun-history-recent" if recent else "speedrun-history"
    svg_path = ASSETS / f"{name}.svg"
    fig.savefig(svg_path, facecolor=BACKGROUND, metadata={"Date": None})
    fig.savefig(ASSETS / f"{name}.png", dpi=240, facecolor=BACKGROUND)
    plt.close(fig)
    svg_description(
        svg_path,
        f"{len(records)} official community records on a logarithmic time axis, "
        f"plus {len(retimings)} re-timings. Official SOTA: approximately "
        f"{latest} seconds. Other reported results: ANVIL2 39.914 seconds "
        f"and Exact-match 47.2056 seconds. AutoTrust's ScienceGuru platform with "
        f"Guru Turbo 1.2: {mean} seconds, five-seed mean on 2026-09-22. "
        "Details and source dates are documented in docs/SPEEDRUN_CHART.md.",
    )
    print(f"Rendered {name}.png and .svg: {len(records)} records, "
          f"{len(retimings)} re-timings, 2 reported submissions, 1 local mean")


def main():
    data = json.loads((ASSETS / "speedrun-history-data.json").read_text())
    results = json.loads((ROOT / "results/cohorts.json").read_text())
    cohort = next(c for c in results["cohorts"]
                  if c["id"] == "coordinated-pageable652-five-v1")
    records = data["community_records"]
    assert sorted(r["record"] for r in records if not r["is_retiming"]) == list(range(1, 92))
    assert sum(bool(r["is_retiming"]) for r in records) == 2
    assert all(Decimal(r["seconds"]) == Decimal(r["minutes"]) * 60 for r in records)
    assert all(date(a["date"]) <= date(b["date"])
               for a, b in zip(records, records[1:]))
    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 12,
        "svg.fonttype": "none",
        "svg.hashsalt": "nanogpt-speedrun-history-v1",
        "axes.unicode_minus": False,
    })
    render(data, cohort, recent=False)
    render(data, cohort, recent=True)


if __name__ == "__main__":
    main()
