"""
Independent verification of the v2 benchmark outputs.

  1. Recompute every summary metric from tick_trace.csv + task_results.csv
     (without metrics_v2) and compare with benchmark_results.csv.
  2. Re-run every simulation from scratch and compare all metrics.
  3. Check every plotted value in figure_manifest.csv against the CSV.
  4. Check trace invariants (one task per core, no task on two cores,
     executed work >= burst, rows = cores x makespan).
  5. Check that every original v1 file still matches its backup checksum.

Exit code 0 only if every check passes.
"""

import collections
import hashlib
import math
import os
import sys

import pandas as pd

from run_benchmark import run_one, WORKLOADS, OUTPUT_DIR, PROJECT
from policies import BENCHMARK_POLICIES

FIGURES_DIR = os.path.join(PROJECT, "06_Figures", "v2_modern_baselines")
BACKUP_MANIFEST = os.path.join(
    PROJECT, "10_Backups", "v1_original_2026-10-21", "SHA256_MANIFEST_before.txt"
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
        check((t["Executed Work"] >= t["Burst"] - 1e-9).all(),
              f"run {rid}: executed work below burst")
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

    # ---------- 5. Originals unchanged ----------
    unchanged = 0
    with open(BACKUP_MANIFEST, encoding="utf-8") as file:
        for line in file:
            digest, path = line.strip().split(None, 1)
            path = path.lstrip("*")
            with open(os.path.join(PROJECT, path), "rb") as original:
                ok = hashlib.sha256(original.read()).hexdigest() == digest
            check(ok, f"original file changed: {path}")
            unchanged += ok

    # ---------- Report ----------
    print(f"Runs checked:                     {len(summary)}")
    print(f"Metric values recomputed:         {len(summary) * len(metric_columns)}")
    print(f"Fresh re-runs compared:           {len(summary)}")
    print(f"Plotted values checked:           {len(manifest)}")
    print(f"Original files verified unchanged: {unchanged}")

    if failures:
        print(f"\nFAILED: {len(failures)} problem(s)")
        for message in failures[:30]:
            print("  -", message)
        sys.exit(1)

    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
