"""
Independent verification of 05_Results/v2_sensitivity/. Writes nothing.

  1. Grid completeness: 16 cost pairs x 64 configurations, no duplicates.
  2. Zero-overhead rows (0, 0) equal the original 64-run benchmark CSV on
     every shared metric.
  3. Recompute from the saved task CSV + tick trace, using identities that
     do not rely on the engine's counters:
        waiting      = (completion - arrival) - busy ticks
        preemptions  = gaps in a task's busy ticks
        migrations   = core changes between consecutive busy ticks
        resumes      = gaps that end on the same core
        overhead     = migration_cost * migrations + cs_cost * resumes
        unused final-tick capacity = executed - burst - overhead, in [0, final capacity)
     plus makespan, misses, tardiness, peak temperature, HOT exposure and
     core-ticks >= 60 °C.
  4. Re-run every configuration and compare all reported metrics.
  5. Original v1 files and v2 baseline outputs still match their checksums.
"""

import hashlib
import math
import os
import sys

import pandas as pd

from run_sensitivity import OUTPUT_DIR, COSTS, run_one
from run_benchmark import OUTPUT_DIR as BASELINE_DIR, WORKLOADS, PROJECT
from policies import BENCHMARK_POLICIES

TOL = 1e-6
MANIFESTS = [
    ("v1 original", os.path.join(PROJECT, "10_Backups", "v1_original_2026-10-21",
                                 "SHA256_MANIFEST_before.txt")),
    ("v2 baseline", os.path.join(PROJECT, "10_Backups", "v2_pre_audit_fixes_2026-10-21",
                                 "SHA256_v2_outputs_before_fixes.txt")),
]

failures = []


def check(ok, message):
    if not ok:
        failures.append(message)


def close(a, b, tol=1e-9):
    return math.isclose(float(a), float(b), rel_tol=tol, abs_tol=tol)


def main():
    S = pd.read_csv(os.path.join(OUTPUT_DIR, "sensitivity_results.csv"))
    T = pd.read_csv(os.path.join(OUTPUT_DIR, "sensitivity_task_results.csv"))
    R = pd.read_csv(os.path.join(OUTPUT_DIR, "sensitivity_tick_trace.csv.gz"))
    B = pd.read_csv(os.path.join(BASELINE_DIR, "benchmark_results.csv"))

    # ---------- 1. Grid ----------
    keys = ["Migration Cost", "Context Switch Cost", "DVFS", "Workload", "Policy"]
    check(len(S) == len(COSTS) ** 2 * 64, f"expected {len(COSTS) ** 2 * 64} rows, got {len(S)}")
    check(not S.duplicated(keys).any(), "duplicate configurations")

    # ---------- 2. Zero overhead == original benchmark ----------
    zero = S[(S["Migration Cost"] == 0) & (S["Context Switch Cost"] == 0)]
    shared = [c for c in B.columns if c not in ("Run ID", "Policy", "Preemptive", "DVFS", "Workload")]
    merged = zero.merge(B, on=["DVFS", "Workload", "Policy"], suffixes=("", " [baseline]"))
    check(len(merged) == 64, "zero-overhead rows do not match 64 baseline rows")
    for _, row in merged.iterrows():
        for c in shared:
            check(close(row[c], row[c + " [baseline]"]),
                  f"zero-overhead {row['Policy']} {row['Workload']} {row['DVFS']} {c} differs from baseline")
        check(row["Total Overhead Work"] == 0, "zero-overhead row charged overhead")

    # ---------- 3. Independent recomputation ----------
    busy = R[R["busy"] == 1].copy()
    busy["pid"] = busy["pid"].astype(int)
    busy_groups = {k: g.sort_values("time") for k, g in busy.groupby(["Run ID", "pid"])}
    run_groups = dict(tuple(R.groupby("Run ID")))
    task_groups = dict(tuple(T.groupby("Run ID")))
    partial = 0

    for _, row in S.iterrows():
        rid = row["Run ID"]
        t, tr = task_groups[rid], run_groups[rid]
        mig_cost, cs_cost = row["Migration Cost"], row["Context Switch Cost"]
        totals = {"wait": 0, "pre": 0, "mig": 0, "res": 0, "over": 0.0}

        for _, task in t.iterrows():
            g = busy_groups[(rid, task["PID"])]
            times, cores = g["time"].tolist(), g["core"].tolist()
            gaps = [(a, b) for a, b in zip(times, times[1:]) if b > a + 1]
            gap_index = {b for _, b in gaps}
            migrations = sum(1 for c1, c2 in zip(cores, cores[1:]) if c1 != c2)
            resumes = sum(1 for i in range(1, len(times))
                          if times[i] in gap_index and cores[i] == cores[i - 1])
            overhead = mig_cost * migrations + cs_cost * resumes
            waiting = (task["Completion"] - task["Arrival"]) - len(times)

            check(waiting == task["Waiting"], f"run {rid} pid {task['PID']}: waiting")
            check(len(times) == task["Busy Ticks"], f"run {rid} pid {task['PID']}: busy ticks")
            check(times[-1] == task["Completion"], f"run {rid} pid {task['PID']}: completion tick")
            check(times[0] == task["Start"] + 1, f"run {rid} pid {task['PID']}: start tick")
            check(migrations == task["Migrations"] == task["Migration Events"],
                  f"run {rid} pid {task['PID']}: migrations")
            check(resumes == task["Resume Events"], f"run {rid} pid {task['PID']}: resumes")
            check(len(gaps) == task["Preemptions"], f"run {rid} pid {task['PID']}: preemptions")
            check(close(overhead, task["Overhead Work"], 1e-9), f"run {rid} pid {task['PID']}: overhead")

            final_capacity = g["frequency_used"].iloc[-1] / 2.5
            unused = task["Executed Work"] - task["Burst"] - overhead
            check(-TOL <= unused < final_capacity - TOL,
                  f"run {rid} pid {task['PID']}: unused capacity {unused} outside [0, {final_capacity})")
            partial += unused > TOL

            totals["wait"] += waiting
            totals["pre"] += len(gaps)
            totals["mig"] += migrations
            totals["res"] += resumes
            totals["over"] += overhead

        n = len(t)
        recomputed = {
            "Average Waiting Time": totals["wait"] / n,
            "Makespan": t["Completion"].max(),
            "Deadline Misses": int((t["Completion"] > t["Deadline"]).sum()),
            "Total Tardiness": (t["Completion"] - t["Deadline"]).clip(lower=0).sum(),
            "Peak Temperature": tr["temperature"].max(),
            "Thermal Exposure (HOT core-ticks)": int(tr["thermal_state"].isin(["HOT", "CRITICAL"]).sum()),
            "Core-ticks >= 60C": int((tr["temperature"] >= 60).sum()),
            "Preemptions": totals["pre"],
            "Migrations": totals["mig"],
            "Migration Events Charged": totals["mig"],
            "Resume Events Charged": totals["res"],
            "Total Overhead Work": totals["over"],
        }
        check(len(tr) == 2 * recomputed["Makespan"], f"run {rid}: trace length")
        for metric, value in recomputed.items():
            check(close(row[metric], value), f"run {rid} {metric}: CSV {row[metric]} vs {value}")

    # ---------- 4. Fresh re-run ----------
    workloads = dict(WORKLOADS)
    policies = {p.name: p for p in BENCHMARK_POLICIES}
    compared = [c for c in S.columns if c not in keys + ["Run ID", "Preemptive"]]
    for _, row in S.iterrows():
        processes, _, metrics = run_one(
            policies[row["Policy"]], row["DVFS"], workloads[row["Workload"]],
            row["Migration Cost"], row["Context Switch Cost"],
        )
        metrics["Migration Events Charged"] = sum(p.migration_events for p in processes)
        metrics["Resume Events Charged"] = sum(p.resume_events for p in processes)
        metrics["Total Overhead Work"] = sum(p.overhead_work for p in processes)
        for c in compared:
            check(close(row[c], metrics[c]), f"re-run {row['Run ID']} {c} differs")

    # ---------- 5. Protected files ----------
    protected = 0
    for label, manifest in MANIFESTS:
        with open(manifest, encoding="utf-8") as file:
            for line in file:
                digest, path = line.strip().split(None, 1)
                with open(os.path.join(PROJECT, path.lstrip("*")), "rb") as f:
                    ok = hashlib.sha256(f.read()).hexdigest() == digest
                check(ok, f"{label} file changed: {path}")
                protected += ok

    print(f"Sensitivity runs checked:            {len(S)}")
    print(f"Zero-overhead rows == baseline:      {len(merged)} rows x {len(shared)} metrics")
    print(f"Task rows recomputed from trace:     {len(T)} ({partial} finish partway through a tick)")
    print(f"Fresh re-runs compared:              {len(S)}")
    print(f"Protected files unchanged (v1 + v2): {protected}")

    if failures:
        print(f"\nFAILED: {len(failures)} problem(s)")
        for message in failures[:30]:
            print("  -", message)
        sys.exit(1)
    print("\nALL SENSITIVITY CHECKS PASSED")


if __name__ == "__main__":
    main()
