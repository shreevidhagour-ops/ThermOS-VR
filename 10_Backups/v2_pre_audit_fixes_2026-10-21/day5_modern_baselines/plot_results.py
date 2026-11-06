"""
Generate v2 comparison figures from 05_Results/v2_modern_baselines/*.csv.

Writes only to 06_Figures/v2_modern_baselines/. Each bar's height is read
back from the drawn figure and written to figure_manifest.csv so that
verify_outputs.py can check the figures against the CSV.
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
RESULTS_DIR = os.path.join(PROJECT, "05_Results", "v2_modern_baselines")
FIGURES_DIR = os.path.join(PROJECT, "06_Figures", "v2_modern_baselines")

POLICY_ORDER = [
    "FCFS", "Priority", "Round Robin", "ThermOS-VR",
    "EDF-NP", "EDF", "TA-EDF", "EEVDF-inspired",
]

# Reference categorical palette, fixed slot order (dataviz references/palette.md).
POLICY_COLORS = dict(zip(POLICY_ORDER, [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#6250d6", "#e34948",
]))

WORKLOAD_ORDER = [
    "Normal VR Workload", "Burst VR Workload",
    "Sustained Thermal Workload", "HOT Thermal Workload",
]

DVFS_TITLES = {
    "off": "DVFS off (fixed 2.5 GHz)",
    "hysteresis": "DVFS on (same hysteresis governor for every policy)",
}

# metric column -> (file slug, axis label, value format)
METRICS = {
    "Average Waiting Time": ("waiting_time", "Average waiting time (ticks)", "{:.1f}"),
    "Average Turnaround Time": ("turnaround_time", "Average turnaround time (ticks)", "{:.1f}"),
    "Average Completion Time": ("completion_time", "Average completion time (ticks)", "{:.1f}"),
    "Deadline Misses": ("deadline_misses", "Deadline misses (of 6 tasks)", "{:.0f}"),
    "Total Tardiness": ("total_tardiness", "Total tardiness (ticks)", "{:.0f}"),
    "Average Temperature": ("average_temperature", "Average simulated temperature (°C)", "{:.2f}"),
    "Peak Temperature": ("peak_temperature", "Peak simulated temperature (°C)", "{:.2f}"),
    "Thermal Exposure (HOT core-ticks)": ("thermal_exposure", "Core-ticks in HOT/CRITICAL (≥70 °C)", "{:.0f}"),
    "Core-ticks >= 60C": ("core_ticks_above_60c", "Core-ticks at or above 60 °C", "{:.0f}"),
    "Throttled Busy Core-ticks": ("throttled_core_ticks", "Busy core-ticks below 2.5 GHz", "{:.0f}"),
    "Heat Generated (model units)": ("heat_generated", "Heat generated (model units)", "{:.1f}"),
    "Core-time Utilization (%)": ("utilization", "Simulated core-time utilization (%)", "{:.1f}"),
}

INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
GRID = "#e4e3df"
SURFACE = "#fcfcfb"


def style_axes(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_SECONDARY, labelsize=8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def metric_figure(df, dvfs, metric, manifest):
    slug, ylabel, fmt = METRICS[metric]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), facecolor=SURFACE)

    for ax, workload in zip(axes.flat, WORKLOAD_ORDER):
        data = (
            df[(df["DVFS"] == dvfs) & (df["Workload"] == workload)]
            .set_index("Policy")
            .reindex(POLICY_ORDER)
        )
        values = data[metric].tolist()
        x = list(range(len(POLICY_ORDER)))
        colors = [POLICY_COLORS[p] for p in POLICY_ORDER]
        style_axes(ax)

        top = max(values) if max(values) > 0 else 1

        if "Temperature" in metric:
            # Dot plot: differences are < 2 °C on a ~60 °C scale, and a
            # bar with a truncated baseline would misstate them.
            marks = ax.scatter(x, values, s=70, c=colors, zorder=3,
                               edgecolors=SURFACE, linewidths=2)
            plotted = [float(y) for _, y in marks.get_offsets()]
            span = max(top - min(values), 0.5)
            ax.set_ylim(min(values) - 0.25 * span, top + 0.25 * span)
            label_y = plotted
            offset = 7
        else:
            bars = ax.bar(x, values, color=colors, edgecolor=SURFACE,
                          linewidth=2, width=0.8)
            plotted = [bar.get_height() for bar in bars]
            ax.set_ylim(0, top * 1.15)
            label_y = plotted
            offset = 2

        ax.set_title(workload, color=INK, fontsize=10, loc="left")
        ax.set_xticks(x)
        ax.set_xticklabels(POLICY_ORDER, rotation=35, ha="right")
        ax.set_ylabel(ylabel, color=INK_SECONDARY, fontsize=8)

        for xi, policy, y, value in zip(x, POLICY_ORDER, label_y, plotted):
            ax.annotate(
                fmt.format(value), (xi, y),
                xytext=(0, offset), textcoords="offset points",
                ha="center", va="bottom", fontsize=7, color=INK,
            )
            manifest.append({
                "Figure": f"{dvfs}_{slug}.png",
                "DVFS": dvfs,
                "Workload": workload,
                "Policy": policy,
                "Metric": metric,
                "Plotted Value": value,
            })

    fig.suptitle(f"{metric} — {DVFS_TITLES[dvfs]}", color=INK, fontsize=12,
                 x=0.01, ha="left")
    fig.text(0.01, 0.005,
             "ThermOS-VR v2 simulation. Simulated values only; 2 identical cores; "
             "1 run per configuration (deterministic workloads).",
             fontsize=7, color=INK_SECONDARY)
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(os.path.join(FIGURES_DIR, f"{dvfs}_{slug}.png"), dpi=200,
                facecolor=SURFACE)
    plt.close(fig)


def trace_figure(summary, trace):
    """Per-core temperature over time, HOT workload, DVFS on."""
    policies = ["FCFS", "ThermOS-VR", "EDF", "TA-EDF"]
    core_colors = {1: "#2a78d6", 2: "#eb6834"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=True, facecolor=SURFACE)

    for ax, policy in zip(axes.flat, policies):
        run_id = summary[
            (summary["DVFS"] == "hysteresis")
            & (summary["Workload"] == "HOT Thermal Workload")
            & (summary["Policy"] == policy)
        ]["Run ID"].item()
        rows = trace[trace["Run ID"] == run_id]
        style_axes(ax)
        for core_id, color in core_colors.items():
            r = rows[rows["core"] == core_id]
            ax.plot(r["time"], r["temperature"], color=color, linewidth=2,
                    label=f"Core {core_id} ({r['core_type'].iloc[0]} label)")
        ax.axhline(60, color=INK_SECONDARY, linewidth=1, linestyle="--")
        ax.text(1, 60.3, "60 °C: DVFS 2.5→2.2 GHz", fontsize=7, color=INK_SECONDARY)
        ax.set_title(policy, color=INK, fontsize=10, loc="left")
        ax.set_xlabel("Simulation time (ticks)", color=INK_SECONDARY, fontsize=8)
        ax.set_ylabel("Simulated temperature (°C)", color=INK_SECONDARY, fontsize=8)
        ax.legend(fontsize=7, frameon=False, loc="lower right")

    fig.suptitle("Per-core simulated temperature — HOT Thermal Workload, DVFS on",
                 color=INK, fontsize=12, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(os.path.join(FIGURES_DIR, "hysteresis_hot_temperature_trace.png"),
                dpi=200, facecolor=SURFACE)
    plt.close(fig)


def main():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    summary = pd.read_csv(os.path.join(RESULTS_DIR, "benchmark_results.csv"))
    trace = pd.read_csv(os.path.join(RESULTS_DIR, "tick_trace.csv"))

    manifest = []
    for dvfs in DVFS_TITLES:
        for metric in METRICS:
            metric_figure(summary, dvfs, metric, manifest)
    trace_figure(summary, trace)

    with open(os.path.join(FIGURES_DIR, "figure_manifest.csv"), "w",
              newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(manifest[0]))
        writer.writeheader()
        writer.writerows(manifest)

    print(f"{len(DVFS_TITLES) * len(METRICS) + 1} figures, "
          f"{len(manifest)} bars written to {FIGURES_DIR}")


if __name__ == "__main__":
    main()
