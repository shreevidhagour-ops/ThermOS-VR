"""
Independent verification of the v2 benchmark outputs.

  1. Recompute every summary metric from tick_trace.csv + task_results.csv
     (without metrics_v2) and compare with benchmark_results.csv.
  2. Re-run every simulation from scratch and compare all metrics.
  3. Check every plotted value in figure_manifest.csv against the CSV.
  4. Check trace invariants (no task on two cores, rows = cores x makespan,
     busy ticks) and partial-tick work accounting:
        "Executed Work" = capacity of every busy tick (sum of f/2.5),
        including the unused part of the final tick. Useful work equals
        Burst, so the unused capacity is Executed Work - Burst, and it must
        satisfy 0 <= unused < capacity of the task's final tick (the task
        really needed that last tick).
  5. Re-render every figure in memory, compare its pixels with the saved
     PNG, and compare the trace figure's line data with tick_trace.csv.
  6. Check that every original v1 file still matches its backup checksum.

Writes nothing to the project (temporary renders go to the OS temp dir).
Exit code 0 only if every check passes.
"""

import hashlib
import math
import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from run_benchmark import run_one, WORKLOADS, OUTPUT_DIR, PROJECT  # noqa: E402
from policies import BENCHMARK_POLICIES  # noqa: E402
import plot_results  # noqa: E402

WORK_TOLERANCE = 1e-6  # engine snaps remaining work below 1e-6 to zero

FIGURES_DIR = os.path.join(PROJECT, "06_Figures", "v2_modern_baselines")
BACKUP_MANIFEST = os.path.join(
    PROJECT, "10_Backups", "v1_original_2026-10-21", "SHA256_MANIFEST_before.txt"
)
# Checksums of the 64-run v2 baseline outputs, taken before the audit fixes.
V2_BASELINE_MANIFEST = os.path.join(
    PROJECT, "10_Backups", "v2_pre_audit_fixes_2026-10-21",
    "SHA256_v2_outputs_before_fixes.txt",
)

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def close(a, b, tol=1e-9):
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main():
    summary = pd.read_csv(os.path.join(OUTPUT_DIR, "benchmark_results.csv"))
    tasks = pd.read_csv(os.path.join(OUTPUT_DIR, "task_results.csv"))
    trace = pd.read_csv(os.path.join(OUTPUT_DIR, "tick_trace.csv"))
    manifest = pd.read_csv(os.path.join(FIGURES_DIR, "figure_manifest.csv"))

    metric_columns = [
        c for c in summary.columns
        if c not in ("Run ID", "Policy", "Preemptive", "DVFS", "Workload")
    ]
    partial_stats = {"tasks": 0, "partial": 0, "unused": 0.0, "max": 0.0}

    # ---------- 1. Independent recomputation ----------
    for _, row in summary.iterrows():
        rid = row["Run ID"]
        t = tasks[tasks["Run ID"] == rid]
        tr = trace[trace["Run ID"] == rid]
        makespan = t["Completion"].max()
        busy = tr[tr["busy"] == 1]

        recomputed = {
            "Average Waiting Time": t["Waiting"].mean(),
            "Average Turnaround Time": (t["Completion"] - t["Arrival"]).mean(),
            "Average Completion Time": t["Completion"].mean(),
            "Average Response Time": (t["Start"] - t["Arrival"]).mean(),
            "Makespan": makespan,
            "Deadline Misses": int((t["Completion"] > t["Deadline"]).sum()),
            "Total Tardiness": (t["Completion"] - t["Deadline"]).clip(lower=0).sum(),
            "Average Temperature": tr["temperature"].mean(),
            "Peak Temperature": tr["temperature"].max(),
            "Thermal Exposure (HOT core-ticks)": int(tr["thermal_state"].isin(["HOT", "CRITICAL"]).sum()),
            "Core-ticks >= 60C": int((tr["temperature"] >= 60).sum()),
            "Throttled Busy Core-ticks": int((busy["frequency_used"] < 2.5).sum()),
            "Heat Generated (model units)": tr["heat"].sum(),
            "Core-time Utilization (%)": len(busy) / (2 * makespan) * 100,
            "Preemptions": t["Preemptions"].sum(),
            "Migrations": t["Migrations"].sum(),
        }
        check(set(recomputed) == set(metric_columns), "metric column mismatch")

        for metric, value in recomputed.items():
            check(close(row[metric], value),
                  f"run {rid} {metric}: CSV {row[metric]} vs recomputed {value}")

        # ---------- 4. Invariants ----------
        check(len(tr) == 2 * makespan, f"run {rid}: trace rows != 2 * makespan")
        per_tick = tr[tr["busy"] == 1].groupby("time")["pid"]
        check((per_tick.nunique() == per_tick.count()).all(),
              f"run {rid}: a task ran on two cores in one tick")
        final_rows = busy.set_index(["pid", "time"])["frequency_used"]
        for _, task_row in t.iterrows():
            final_capacity = final_rows.loc[(task_row["PID"], task_row["Completion"])] / 2.5
            unused = task_row["Executed Work"] - task_row["Burst"]
            check(-WORK_TOLERANCE <= unused < final_capacity - WORK_TOLERANCE,
                  f"run {rid} pid {task_row['PID']}: unused final-tick capacity "
                  f"{unused} outside [0, {final_capacity})")
            partial_stats["tasks"] += 1
            if unused > WORK_TOLERANCE:
                partial_stats["partial"] += 1
                partial_stats["unused"] += unused
                partial_stats["max"] = max(partial_stats["max"], unused)
        busy_by_pid = busy.groupby("pid").size()
        for _, task_row in t.iterrows():
            check(busy_by_pid.get(task_row["PID"], 0) == task_row["Busy Ticks"],
                  f"run {rid} pid {task_row['PID']}: busy ticks mismatch")
        check((t["Start"] >= t["Arrival"]).all(), f"run {rid}: start before arrival")

    # ---------- 2. Fresh re-run ----------
    workload_functions = dict(WORKLOADS)
    policy_classes = {p.name: p for p in BENCHMARK_POLICIES}

    for _, row in summary.iterrows():
        _, _, metrics = run_one(
            policy_classes[row["Policy"]], row["DVFS"],
            workload_functions[row["Workload"]],
        )
        for metric in metric_columns:
            check(close(row[metric], metrics[metric]),
                  f"re-run {row['Run ID']} {metric} differs")

    # ---------- 3. Figures vs CSV ----------
    check(len(manifest) == 2 * 12 * 32, f"unexpected manifest size {len(manifest)}")
    indexed = summary.set_index(["DVFS", "Workload", "Policy"])

    for _, m in manifest.iterrows():
        expected = indexed.loc[(m["DVFS"], m["Workload"], m["Policy"]), m["Metric"]]
        check(close(m["Plotted Value"], expected),
              f"{m['Figure']} {m['Workload']} {m['Policy']}: plotted "
              f"{m['Plotted Value']} vs CSV {expected}")

    for figure in manifest["Figure"].unique():
        check(os.path.isfile(os.path.join(FIGURES_DIR, figure)), f"missing {figure}")

    # ---------- 5. Re-render figures; trace figure vs raw trace ----------
    saved_pngs = sorted(f for f in os.listdir(FIGURES_DIR) if f.endswith(".png"))
    figures, rerendered_manifest = plot_results.build_all_figures(summary, trace)
    check(sorted(name for _, name in figures) == saved_pngs,
          "re-rendered figure set differs from saved PNGs")
    saved_rows = manifest.to_dict("records")
    check(len(rerendered_manifest) == len(saved_rows)
          and all(
              all(str(a[k]) == str(b[k]) for k in a if k != "Plotted Value")
              and close(a["Plotted Value"], b["Plotted Value"])
              for a, b in zip(rerendered_manifest, saved_rows)
          ),
          "re-rendered manifest differs from saved figure_manifest.csv")

    pixel_identical = 0
    trace_points = 0

    with tempfile.TemporaryDirectory() as scratch:
        for fig, filename in figures:
            if filename == plot_results.TRACE_FIGURE:
                axes = fig.axes
                check(len(axes) == len(plot_results.TRACE_POLICIES),
                      "trace figure panel count")
                for ax, policy in zip(axes, plot_results.TRACE_POLICIES):
                    rows = trace[trace["Run ID"] == plot_results.trace_run_id(summary, policy)]
                    core_lines = [ln for ln in ax.lines if ln.get_label().startswith("Core ")]
                    check(len(core_lines) == 2, f"trace {policy}: expected 2 core lines")
                    for core_id, line in zip((1, 2), core_lines):
                        raw = rows[rows["core"] == core_id]
                        check(np.array_equal(line.get_xdata(), raw["time"].to_numpy())
                              and np.allclose(line.get_ydata(), raw["temperature"].to_numpy(),
                                              rtol=0, atol=1e-12),
                              f"trace {policy} core {core_id}: line data != tick_trace.csv")
                        trace_points += len(raw)

            plot_results.save_figure(fig, scratch, filename)
            fresh = mpimg.imread(os.path.join(scratch, filename))
            saved = mpimg.imread(os.path.join(FIGURES_DIR, filename))
            same = fresh.shape == saved.shape and np.array_equal(fresh, saved)
            check(same, f"{filename}: saved PNG differs from re-render of the CSV")
            pixel_identical += same

    # ---------- 6. Originals unchanged ----------
    def verify_manifest(manifest_path, label):
        matched = 0
        with open(manifest_path, encoding="utf-8") as file:
            for line in file:
                digest, path = line.strip().split(None, 1)
                path = path.lstrip("*")
                with open(os.path.join(PROJECT, path), "rb") as original:
                    ok = hashlib.sha256(original.read()).hexdigest() == digest
                check(ok, f"{label} file changed: {path}")
                matched += ok
        return matched

    unchanged = verify_manifest(BACKUP_MANIFEST, "original v1")
    v2_unchanged = (
        verify_manifest(V2_BASELINE_MANIFEST, "v2 baseline")
        if os.path.isfile(V2_BASELINE_MANIFEST) else 0
    )

    # ---------- Report ----------
    print(f"Runs checked:                     {len(summary)}")
    print(f"Metric values recomputed:         {len(summary) * len(metric_columns)}")
    print(f"Fresh re-runs compared:           {len(summary)}")
    print(f"Plotted values checked:           {len(manifest)}")
    print(f"PNGs pixel-identical to re-render: {pixel_identical} of {len(saved_pngs)}")
    print(f"Trace-figure points vs raw trace: {trace_points}")
    print(f"Task work accounting checked:     {partial_stats['tasks']} task rows; "
          f"{partial_stats['partial']} finish partway through their final tick "
          f"(unused capacity total {partial_stats['unused']:.3f}, "
          f"max {partial_stats['max']:.3f} work units)")
    print(f"Original files verified unchanged: {unchanged}")
    print(f"v2 baseline outputs unchanged since pre-fix snapshot: {v2_unchanged}")

    if failures:
        print(f"\nFAILED: {len(failures)} problem(s)")
        for message in failures[:30]:
            print("  -", message)
        sys.exit(1)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
