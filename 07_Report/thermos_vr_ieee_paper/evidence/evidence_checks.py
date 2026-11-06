"""
Read-only evidence checks for the ThermOS-VR IEEE paper.

Recomputes every key numerical claim directly from the frozen CSV files
and prints PASS / FAIL with the recomputed values. Writes nothing except
its own stdout (redirect it to evidence_checks_output.txt).

Run from this folder:  python -B evidence_checks.py > evidence_checks_output.txt
"""

import os
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
B_PATH = os.path.join(ROOT, "05_Results", "v2_modern_baselines", "benchmark_results.csv")
T_PATH = os.path.join(ROOT, "05_Results", "v2_modern_baselines", "task_results.csv")
S_PATH = os.path.join(ROOT, "05_Results", "v2_sensitivity", "sensitivity_results.csv")
D_PATH = os.path.join(ROOT, "05_Results", "v2_modern_baselines", "metric_definitions.csv")

B = pd.read_csv(B_PATH)
T = pd.read_csv(T_PATH)
S = pd.read_csv(S_PATH)
D = pd.read_csv(D_PATH)

POLICIES = ["FCFS", "Priority", "Round Robin", "ThermOS-VR", "EDF-NP", "EDF", "TA-EDF", "EEVDF-inspired"]
WORKLOADS = ["Normal VR Workload", "Burst VR Workload", "Sustained Thermal Workload", "HOT Thermal Workload"]
LABEL_COLS = ["Run ID", "Policy", "Preemptive", "DVFS", "Workload"]
METRICS = [c for c in B.columns if c not in LABEL_COLS]

results = []


def check(cid, ok, detail):
    results.append((cid, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {cid}: {detail}")


def section(title):
    print(f"\n=== {title} ===")


# ------------------------------------------------------------------ coverage
section("Coverage, schema, missing values")
check("COV-B-rows", len(B) == 64, f"benchmark rows = {len(B)}")
check("COV-B-unique", not B.duplicated(["Policy", "DVFS", "Workload"]).any()
      and B.groupby(["Policy", "DVFS", "Workload"]).ngroups == 64,
      f"unique (policy, DVFS, workload) = {B.groupby(['Policy','DVFS','Workload']).ngroups}")
check("COV-B-sets", sorted(B.Policy.unique()) == sorted(POLICIES)
      and sorted(B.Workload.unique()) == sorted(WORKLOADS)
      and sorted(B.DVFS.unique()) == ["hysteresis", "off"],
      f"policies={sorted(B.Policy.unique())}; DVFS={sorted(B.DVFS.unique())}")
check("COV-T-rows", len(T) == 384 and (T.groupby("Run ID").size() == 6).all(),
      f"task rows = {len(T)}, 6 per run = {(T.groupby('Run ID').size() == 6).all()}")
check("COV-S-rows", len(S) == 1024, f"sensitivity rows = {len(S)}")
costs = sorted(S["Migration Cost"].unique())
check("COV-S-grid", costs == [0.0, 0.1, 0.25, 0.5]
      and sorted(S["Context Switch Cost"].unique()) == costs
      and S.groupby(["Migration Cost", "Context Switch Cost"]).size().eq(64).all()
      and not S.duplicated(["Migration Cost", "Context Switch Cost", "Policy", "DVFS", "Workload"]).any(),
      f"costs = {costs}; 16 pairs x 64 configurations, no duplicates")
check("COV-NaN", int(B.isna().sum().sum()) == 0 and int(S.isna().sum().sum()) == 0,
      f"NaN cells: benchmark={int(B.isna().sum().sum())}, sensitivity={int(S.isna().sum().sum())}")
check("COV-defs", sorted(D.Metric) == sorted(METRICS),
      f"metric_definitions.csv covers all {len(METRICS)} benchmark metric columns")
print("Benchmark metric columns:", METRICS)
print("Sensitivity extra columns:", [c for c in S.columns if c not in B.columns])

idx = B.set_index(["DVFS", "Workload", "Policy"])


def v(dvfs, workload, policy, metric):
    return idx.loc[(dvfs, workload, policy), metric]


# ------------------------------------------------------------- ThermOS = FCFS
section("C3.1 ThermOS-VR equals FCFS under the same governor")
diffs = []
for d in ("off", "hysteresis"):
    for w in WORKLOADS:
        for m in METRICS:
            if abs(v(d, w, "ThermOS-VR", m) - v(d, w, "FCFS", m)) > 1e-12:
                diffs.append((d, w, m))
check("C3.1", not diffs, f"{8 * len(METRICS)} metric comparisons, {len(diffs)} differ")

section("C3.2 / C7.5 DVFS effect for FCFS (= ThermOS-VR)")
for w in WORKLOADS:
    print(f"  {w:27s} peak off={v('off', w, 'FCFS', 'Peak Temperature'):.2f} "
          f"on={v('hysteresis', w, 'FCFS', 'Peak Temperature'):.2f}; "
          f"HOT core-ticks off={v('off', w, 'FCFS', 'Thermal Exposure (HOT core-ticks)'):.0f} "
          f"on={v('hysteresis', w, 'FCFS', 'Thermal Exposure (HOT core-ticks)'):.0f}; "
          f"makespan off={v('off', w, 'FCFS', 'Makespan'):.0f} on={v('hysteresis', w, 'FCFS', 'Makespan'):.0f}")
check("C7.5", abs(v("off", WORKLOADS[3], "FCFS", "Peak Temperature") - 71.74) < 0.005
      and abs(v("hysteresis", WORKLOADS[3], "FCFS", "Peak Temperature") - 62.49) < 0.005
      and v("off", WORKLOADS[3], "FCFS", "Makespan") == 205
      and v("hysteresis", WORKLOADS[3], "FCFS", "Makespan") == 226,
      "HOT, FCFS: peak 71.74 -> 62.49, makespan 205 -> 226")

# ------------------------------------------------------------ responsiveness
section("C5.1 EDF / TA-EDF lowest or tied-lowest waiting and tardiness")
ok = True
for d in ("off", "hysteresis"):
    for w in WORKLOADS:
        for m in ("Average Waiting Time", "Total Tardiness"):
            best = min(v(d, w, p, m) for p in POLICIES)
            edf_best = min(v(d, w, "EDF", m), v(d, w, "TA-EDF", m))
            tied = [p for p in POLICIES if abs(v(d, w, p, m) - best) < 1e-9]
            ok &= abs(edf_best - best) < 1e-9
            print(f"  {d:10s} {w:27s} {m:22s} best={best:.2f} by {tied}")
check("C5.1", ok, "an EDF variant attains the minimum in all 16 cases")

section("C5.2 EDF vs TA-EDF gap at zero overhead")
gw = max(abs(v(d, w, "EDF", "Average Waiting Time") - v(d, w, "TA-EDF", "Average Waiting Time"))
         for d in ("off", "hysteresis") for w in WORKLOADS)
gt = max(abs(v(d, w, "EDF", "Total Tardiness") - v(d, w, "TA-EDF", "Total Tardiness"))
         for d in ("off", "hysteresis") for w in WORKLOADS)
check("C5.2", gw <= 0.5 + 1e-9 and gt <= 2, f"max |waiting gap| = {gw:.3f}, max |tardiness gap| = {gt:.0f}")

section("C5.3 Round Robin last on waiting and tardiness; EEVDF second-last on waiting")
ok = True
for d in ("off", "hysteresis"):
    for w in WORKLOADS:
        wait = sorted(POLICIES, key=lambda p: v(d, w, p, "Average Waiting Time"))
        tard = max(POLICIES, key=lambda p: v(d, w, p, "Total Tardiness"))
        ok &= wait[-1] == "Round Robin" and wait[-2] == "EEVDF-inspired" and tard == "Round Robin"
check("C5.3", ok, "holds in all 8 (DVFS, workload) cases")

# ------------------------------------------------------------------ thermal
section("C7.1 / C7.2 HOT exposure")
on_hot = B[B.DVFS == "hysteresis"]["Thermal Exposure (HOT core-ticks)"]
check("C7.1", (on_hot == 0).all(), "DVFS on: HOT core-ticks = 0 in all 32 runs")
off_nonzero = B[(B.DVFS == "off") & (B["Thermal Exposure (HOT core-ticks)"] > 0)].Workload.unique().tolist()
check("C7.2a", off_nonzero == [WORKLOADS[3]], f"DVFS off: non-zero only in {off_nonzero}")
print("  DVFS off, HOT workload:", {p: int(v("off", WORKLOADS[3], p, "Thermal Exposure (HOT core-ticks)")) for p in POLICIES})

section("C7.4 total model heat identical across policies with DVFS off")
spread = B[B.DVFS == "off"].groupby("Workload")["Heat Generated (model units)"].agg(lambda x: x.max() - x.min())
check("C7.4", (spread < 1e-9).all(), f"max spread per workload = {spread.max():.2e}; values = "
      + str(B[B.DVFS == 'off'].groupby('Workload')['Heat Generated (model units)'].first().round(2).to_dict()))

section("C7.3 core-ticks >= 60 C, DVFS on")
for w in WORKLOADS[2:]:
    print(f"  {w}: " + ", ".join(f"{p}={v('hysteresis', w, p, 'Core-ticks >= 60C'):.0f}" for p in POLICIES))

section("C7.7 TA-EDF peak below EDF at zero overhead")
gaps = {(d, w): v(d, w, "EDF", "Peak Temperature") - v(d, w, "TA-EDF", "Peak Temperature")
        for d in ("off", "hysteresis") for w in WORKLOADS}
check("C7.7", all(g > 0 for g in gaps.values()),
      f"EDF - TA-EDF peak gaps: min {min(gaps.values()):.2f}, max {max(gaps.values()):.2f} C")
for k, g in gaps.items():
    print(f"  {k[0]:10s} {k[1]:27s} gap {g:.2f}")

# --------------------------------------------------------------- feasibility
section("C8.1 / C8.2 deadline feasibility (two cores)")
for w in WORKLOADS:
    t = T[(T["Run ID"] == B[(B.Workload == w) & (B.Policy == "FCFS") & (B.DVFS == "off")]["Run ID"].item())]
    work = t.Burst.sum()
    print(f"  {w:27s} total work {work:4d} -> makespan lower bound {work / 2:6.1f}; "
          f"deadlines {t.Deadline.min()}-{t.Deadline.max()}; "
          f"EDF misses (off) {v('off', w, 'EDF', 'Deadline Misses'):.0f}")
check("C8.3", all(v(d, w, p, "Deadline Misses") in (4, 6)
                  for d in ("off", "hysteresis") for w in WORKLOADS[2:] for p in POLICIES),
      "Sustained / HOT: every policy misses 4 or 6 of 6")

# --------------------------------------------------------------- migrations
section("C10.4 migrations at zero overhead")
for d in ("off", "hysteresis"):
    print(f"  {d:10s} " + "; ".join(f"{w.split()[0]}: TA-EDF={v(d, w, 'TA-EDF', 'Migrations'):.0f}, "
                                   f"EDF={v(d, w, 'EDF', 'Migrations'):.0f}" for w in WORKLOADS))

# -------------------------------------------------------------- sensitivity
section("C6 overhead sensitivity (matched on DVFS, workload, migration cost, context-switch cost)")
key = ["DVFS", "Workload", "Migration Cost", "Context Switch Cost"]
a = S[S.Policy == "TA-EDF"].set_index(key)
e = S[S.Policy == "EDF"].set_index(key)
diff = (a.select_dtypes("number") - e.select_dtypes("number")).reset_index()
check("C6.1", int(S[S.Policy == "EDF"].Migrations.sum()) == 0
      and S[S.Policy == "EDF"].groupby(["DVFS", "Workload"])["Total Tardiness"].agg(lambda x: x.max() - x.min()).max() <= 2,
      "EDF: 0 migrations in all 128 rows; tardiness varies by <= 2 ticks per (DVFS, workload)")
m1 = diff[diff["Migration Cost"] >= 0.1]
check("C6.2", len(m1) == 96 and (m1["Total Tardiness"] > 0).all() and (m1["Makespan"] > 0).all(),
      f"{len(m1)} matched configurations with migration cost >= 0.1; TA-EDF tardiness higher in "
      f"{int((m1['Total Tardiness'] > 0).sum())}, makespan longer in {int((m1['Makespan'] > 0).sum())}; "
      f"tardiness diff {m1['Total Tardiness'].min():.0f}..{m1['Total Tardiness'].max():.0f}, "
      f"makespan diff {m1['Makespan'].min():.0f}..{m1['Makespan'].max():.0f}")
bm = diff[(diff["Migration Cost"] >= 0.25) & (diff.Workload == WORKLOADS[1])]["Deadline Misses"]
hm = diff[(diff["Migration Cost"] == 0.5) & (diff.Workload == WORKLOADS[3]) & (diff.DVFS == "hysteresis")]["Deadline Misses"]
check("C6.3", bm.min() == 3 and bm.max() == 4 and (hm == 1).all(),
      f"Burst, mig >= 0.25: extra misses {bm.min():.0f}..{bm.max():.0f}; HOT, mig 0.5, DVFS on: extra misses {sorted(hm.unique())}")
m0 = diff[diff["Migration Cost"] == 0]["Total Tardiness"]
check("C6.4", m0.min() == -4 and m0.max() == 5, f"migration cost 0: tardiness diff {m0.min():.0f}..{m0.max():.0f}")
for w in WORKLOADS:
    g = diff[diff.Workload == w]
    z, p = g[g["Migration Cost"] == 0]["Peak Temperature"], g[g["Migration Cost"] > 0]["Peak Temperature"]
    print(f"  peak diff (TA-EDF - EDF) {w:27s} mig=0: {z.min():+.2f}..{z.max():+.2f}; mig>0: {p.min():+.2f}..{p.max():+.2f}")
three = diff[(diff.Workload != WORKLOADS[1])]["Peak Temperature"]
burst = diff[(diff.Workload == WORKLOADS[1]) & (diff["Migration Cost"] > 0)]["Peak Temperature"]
# As worded in AUDIT_FIXES.md / README ("1.0-2.5 C below EDF"). Kept as a
# record of a documented rounding discrepancy; it is expected to FAIL.
check("C6.5-as-documented", (three < 0).all() and (-three).min() >= 1.0 - 1e-9 and (-three).max() <= 2.5
      and (burst > 0).all(),
      f"claim '1.0-2.5 C below EDF': actual N/S/H range {(-three).min():.2f}..{(-three).max():.2f} C "
      f"(minimum is below 1.0)")
# Exact statement used in the paper.
check("C6.5-exact", (three < 0).all() and abs((-three).min() - 0.99) < 0.005
      and abs((-three).max() - 2.49) < 0.005 and (burst > 0).all()
      and abs(burst.min() - 0.70) < 0.005 and abs(burst.max() - 3.93) < 0.005,
      f"N/S/H: TA-EDF peak {(-three).min():.2f}..{(-three).max():.2f} C below EDF at every cost; "
      f"Burst with mig > 0: {burst.min():+.2f}..{burst.max():+.2f} C above EDF")

section("Table for paper: TA-EDF - EDF, DVFS on, context-switch cost 0")
tab = diff[(diff.DVFS == "hysteresis") & (diff["Context Switch Cost"] == 0)]
print(tab.pivot_table(index="Migration Cost", columns="Workload",
                      values="Total Tardiness")[WORKLOADS].to_string())
print(tab.pivot_table(index="Migration Cost", columns="Workload",
                      values="Peak Temperature")[WORKLOADS].round(2).to_string())

section("Zero-overhead sensitivity rows equal the benchmark")
z = S[(S["Migration Cost"] == 0) & (S["Context Switch Cost"] == 0)].merge(
    B, on=["Policy", "DVFS", "Workload"], suffixes=("", "_b"))
bad = sum(abs(z[m] - z[m + "_b"]).gt(1e-9).sum() for m in METRICS)
check("C6.7", len(z) == 64 and bad == 0, f"{len(z)} rows x {len(METRICS)} metrics, {bad} mismatches")

passed = sum(ok for _, ok in results)
print(f"\nSUMMARY: {passed} of {len(results)} checks passed")
sys.exit(0 if passed == len(results) else 1)
