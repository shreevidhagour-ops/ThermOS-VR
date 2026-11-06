"""
New figures for the paper (existing v2 figures are reused unchanged):

  fig_architecture.png        simulator architecture / tick order (diagram, no data)
  fig_sensitivity_tardiness.png
      TA-EDF minus EDF total tardiness vs migration cost
      (context-switch cost fixed at 0), one line per workload, DVFS on/off.

Reads 05_Results/v2_sensitivity/sensitivity_results.csv (read-only).
Writes only into this folder, plus figure_manifest_paper.csv with every
plotted value, then re-reads the drawn line data and checks it against a
fresh recomputation from the CSV. Run:  python -B make_paper_figures.py
"""

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
S_PATH = os.path.join(ROOT, "05_Results", "v2_sensitivity", "sensitivity_results.csv")

INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
WORKLOADS = ["Normal VR Workload", "Burst VR Workload",
             "Sustained Thermal Workload", "HOT Thermal Workload"]
SHORT = {"Normal VR Workload": "Normal VR", "Burst VR Workload": "Burst VR",
         "Sustained Thermal Workload": "Sustained", "HOT Thermal Workload": "HOT"}
MARKERS = ["o", "s", "^", "D"]

plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 7.5})


# ------------------------------------------------------------- architecture
def box(ax, x, y, w, h, text, fill="#eef3fb", edge="#2a78d6", bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                                facecolor=fill, edgecolor=edge, linewidth=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7,
            color=INK, fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, text=None, style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=INK2, lw=0.9))
    if text:
        ax.text((x1 + x2) / 2 + 0.05, (y1 + y2) / 2, text, fontsize=6, color=INK2, va="center")


def architecture():
    fig, ax = plt.subplots(figsize=(3.5, 4.6), facecolor=SURFACE)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13.2)
    ax.axis("off")
    W, H, X = 6.0, 1.05, 0.9
    rows = [
        ("Workload definition\n4 workloads × 6 one-shot tasks\n(arrival, burst, deadline, priority, intensity)", 11.7),
        ("Ready set at tick t\n(arrived, unfinished, not running)", 10.2),
        ("Scheduling policy (1 of 8)\nmaps each core to a task or idle", 8.7),
        ("Execution on 2 identical cores\nwork per tick = f / 2.5 GHz", 7.2),
        ("Thermal update per core\nT ← T + (w/100)(f/2.5)² − 0.02(T − 25)", 5.7),
        ("DVFS governor (off or hysteresis)\nsets f for tick t + 1", 4.2),
        ("Completion check, t ← t + 1\nper-tick trace and task records", 2.7),
        ("Metrics, CSV files, figures\nverification scripts", 1.2),
    ]
    for i, (text, y) in enumerate(rows):
        box(ax, X, y, W, H, text, fill="#eef3fb" if i not in (4, 5) else "#fdf1ea",
            edge="#2a78d6" if i not in (4, 5) else "#eb6834")
        if i < len(rows) - 1:
            arrow(ax, X + W / 2, y, X + W / 2, rows[i + 1][1] + H)
    # feedback loop (left margin): completion -> ready set of the next tick
    lx = 0.35
    ax.plot([X, lx, lx], [2.7 + H / 2, 2.7 + H / 2, 10.2 + H / 2], color=INK2, lw=0.9)
    ax.annotate("", xy=(X, 10.2 + H / 2), xytext=(lx, 10.2 + H / 2),
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=0.9))
    ax.text(lx - 0.1, 6.4, "next tick", fontsize=6.5, color=INK2, ha="center",
            va="center", rotation=90)
    # overhead extension annotation
    box(ax, 7.3, 8.75, 2.55, 0.95, "Overhead model\n(sensitivity only)",
        fill="#f4f4f2", edge="#8a8984")
    arrow(ax, 7.3, 9.2, X + W, 9.2)
    fig.tight_layout(pad=0.2)
    out = os.path.join(HERE, "fig_architecture.png")
    fig.savefig(out, dpi=300, facecolor=SURFACE)
    plt.close(fig)
    return out


# --------------------------------------------------------------- sensitivity
def sensitivity_differences():
    S = pd.read_csv(S_PATH)
    key = ["DVFS", "Workload", "Migration Cost", "Context Switch Cost"]
    a = S[S.Policy == "TA-EDF"].set_index(key)["Total Tardiness"]
    e = S[S.Policy == "EDF"].set_index(key)["Total Tardiness"]
    d = (a - e).reset_index()
    return d[d["Context Switch Cost"] == 0]


def sensitivity(manifest):
    d = sensitivity_differences()
    costs = sorted(d["Migration Cost"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(3.5, 2.2), sharey=True, facecolor=SURFACE)
    for ax, dvfs, title in zip(axes, ["hysteresis", "off"], ["DVFS on", "DVFS off"]):
        for color, marker, w in zip(SERIES, MARKERS, WORKLOADS):
            r = d[(d.DVFS == dvfs) & (d.Workload == w)].sort_values("Migration Cost")
            ax.plot(r["Migration Cost"], r["Total Tardiness"], color=color, marker=marker,
                    markersize=4, linewidth=1.6, label=SHORT[w])
            for x, y in zip(r["Migration Cost"], r["Total Tardiness"]):
                manifest.append({"Figure": "fig_sensitivity_tardiness.png", "Panel": dvfs,
                                 "Workload": w, "Migration Cost": x,
                                 "Context Switch Cost": 0.0,
                                 "TA-EDF minus EDF Total Tardiness": y})
        ax.axhline(0, color=INK2, linewidth=0.8, linestyle="--")
        ax.set_title(title, fontsize=7.5, loc="left", color=INK)
        ax.set_xticks(costs)
        ax.set_xticklabels([f"{c:g}" for c in costs])
        ax.grid(True, axis="y", color=GRID, linewidth=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(labelsize=6.5, colors=INK2)
    axes[0].set_ylabel("TA-EDF − EDF total tardiness (ticks)", fontsize=6.5, color=INK2)
    axes[0].legend(fontsize=6, frameon=False, loc="upper left")
    fig.supxlabel("Migration cost per migration (simulated work units; context-switch cost 0)",
                  fontsize=6.5, color=INK2)
    fig.tight_layout(pad=0.3)
    out = os.path.join(HERE, "fig_sensitivity_tardiness.png")
    fig.savefig(out, dpi=300, facecolor=SURFACE)
    # read back drawn data for validation
    drawn = {}
    for ax, dvfs in zip(axes, ["hysteresis", "off"]):
        for line in ax.get_lines():
            if line.get_label() in SHORT.values():
                drawn[(dvfs, line.get_label())] = (list(line.get_xdata()), list(line.get_ydata()))
    plt.close(fig)
    return out, drawn


def validate(drawn):
    d = sensitivity_differences()
    ok = True
    for (dvfs, label), (xs, ys) in drawn.items():
        w = next(k for k, v in SHORT.items() if v == label)
        r = d[(d.DVFS == dvfs) & (d.Workload == w)].sort_values("Migration Cost")
        ok &= list(r["Migration Cost"]) == xs and list(r["Total Tardiness"]) == ys
    return ok and len(drawn) == 8


if __name__ == "__main__":
    manifest = []
    a = architecture()
    s, drawn = sensitivity(manifest)
    with open(os.path.join(HERE, "figure_manifest_paper.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)
    ok = validate(drawn)
    print(f"wrote {os.path.basename(a)}, {os.path.basename(s)}; {len(manifest)} plotted values")
    print(f"VALIDATION: drawn sensitivity lines equal CSV recomputation: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
