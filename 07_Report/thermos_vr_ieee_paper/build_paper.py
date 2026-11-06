# -*- coding: utf-8 -*-
"""
Build the ThermOS-VR paper from a single content source.

Outputs (in this folder):
  ThermOS_VR_Research_Report.docx   IEEE-style two-column Word document
  ThermOS_VR_Research_Report.tex    IEEEtran conference LaTeX source
  references.bib                    BibTeX (generated from paper_refs.py)
  build_report.txt                  fact checks, citation coverage, copies made

All tables are generated from the frozen result CSVs (read-only), and every
number quoted in the prose is asserted against those CSVs before writing.
Run with:  python -B build_paper.py   (python-docx must be importable)
"""

import hashlib
import json
import os
import re
import shutil
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)

import paper_content as C  # noqa: E402
import paper_refs as R  # noqa: E402

B = pd.read_csv(os.path.join(ROOT, "05_Results", "v2_modern_baselines", "benchmark_results.csv"))
T = pd.read_csv(os.path.join(ROOT, "05_Results", "v2_modern_baselines", "task_results.csv"))
S = pd.read_csv(os.path.join(ROOT, "05_Results", "v2_sensitivity", "sensitivity_results.csv"))
META = json.load(open(os.path.join(ROOT, "05_Results", "v2_modern_baselines", "run_metadata.json"),
                      encoding="utf-8"))

POL = ["FCFS", "Priority", "Round Robin", "ThermOS-VR", "EDF-NP", "EDF", "TA-EDF", "EEVDF-inspired"]
POL_SHORT = {"Round Robin": "RR", "EEVDF-inspired": "EEVDF-insp."}
WL = ["Normal VR Workload", "Burst VR Workload", "Sustained Thermal Workload", "HOT Thermal Workload"]
WS = {"Normal VR Workload": "Normal", "Burst VR Workload": "Burst",
      "Sustained Thermal Workload": "Sustained", "HOT Thermal Workload": "HOT"}
IDX = B.set_index(["DVFS", "Workload", "Policy"])
LOG = []


def v(d, w, p, m):
    return IDX.loc[(d, w, p), m]


# ======================================================================
# Fact assertions: every number used in the prose
# ======================================================================
TRACE = pd.read_csv(os.path.join(ROOT, "05_Results", "v2_modern_baselines", "tick_trace.csv"))


def imbalance(dvfs, policy, workload="HOT Thermal Workload"):
    """Mean absolute inter-core temperature difference over a run (from tick_trace.csv)."""
    rid = B[(B.DVFS == dvfs) & (B.Workload == workload) & (B.Policy == policy)]["Run ID"].item()
    t = TRACE[TRACE["Run ID"] == rid].pivot(index="time", columns="core", values="temperature")
    return round(float((t[1] - t[2]).abs().mean()), 2)


def sens_diff():
    key = ["DVFS", "Workload", "Migration Cost", "Context Switch Cost"]
    a = S[S.Policy == "TA-EDF"].set_index(key).select_dtypes("number")
    e = S[S.Policy == "EDF"].set_index(key).select_dtypes("number")
    return (a - e).reset_index()


def facts():
    D = sens_diff()
    on, off = "hysteresis", "off"
    m1 = D[D["Migration Cost"] >= 0.1]
    nsh = D[D.Workload != WL[1]]["Peak Temperature"]
    burst_pos = D[(D.Workload == WL[1]) & (D["Migration Cost"] > 0)]["Peak Temperature"]
    zero_gap = [v(d, w, "EDF", "Peak Temperature") - v(d, w, "TA-EDF", "Peak Temperature")
                for d in (on, off) for w in WL]
    tasks = {w: T[T["Run ID"] == B[(B.Workload == w) & (B.Policy == "FCFS") & (B.DVFS == off)]["Run ID"].item()]
             for w in WL}
    F = [
        ("runs", len(B), 64), ("task records", len(T), 384), ("sensitivity runs", len(S), 1024),
        ("ThermOS==FCFS diffs", sum(abs(v(d, w, "ThermOS-VR", m) - v(d, w, "FCFS", m)) > 1e-12
                                    for d in (on, off) for w in WL
                                    for m in B.columns[5:]), 0),
        ("FCFS HOT peak off", round(v(off, WL[3], "FCFS", "Peak Temperature"), 2), 71.74),
        ("FCFS HOT peak on", round(v(on, WL[3], "FCFS", "Peak Temperature"), 2), 62.49),
        ("FCFS HOT HOT-ticks off", v(off, WL[3], "FCFS", "Thermal Exposure (HOT core-ticks)"), 64),
        ("FCFS HOT makespan off/on", (v(off, WL[3], "FCFS", "Makespan"), v(on, WL[3], "FCFS", "Makespan")), (205, 226)),
        ("FCFS Sus peak off/on", (round(v(off, WL[2], "FCFS", "Peak Temperature"), 2),
                                  round(v(on, WL[2], "FCFS", "Peak Temperature"), 2)), (67.61, 61.28)),
        ("FCFS Sus makespan off/on", (v(off, WL[2], "FCFS", "Makespan"), v(on, WL[2], "FCFS", "Makespan")), (125, 135)),
        ("Normal/Burst never 60C", int(B[B.Workload.isin(WL[:2])]["Core-ticks >= 60C"].sum()), 0),
        ("Normal waiting min", round(min(v(on, WL[0], p, "Average Waiting Time") for p in POL), 2), 2.83),
        ("Normal waiting ties", sorted(p for p in POL if abs(v(on, WL[0], p, "Average Waiting Time") -
                                       min(v(on, WL[0], q, "Average Waiting Time") for q in POL)) < 1e-9),
         sorted(["Priority", "EDF-NP", "EDF", "TA-EDF"])),
        ("Normal tardiness=2 count", sum(v(on, WL[0], p, "Total Tardiness") == 2 for p in POL), 6),
        ("Sus waiting TA/EDF", (round(v(on, WL[2], "TA-EDF", "Average Waiting Time"), 2),
                                round(v(on, WL[2], "EDF", "Average Waiting Time"), 2)), (40.83, 41.33)),
        ("HOT waiting TA/EDF", (round(v(on, WL[3], "TA-EDF", "Average Waiting Time"), 2),
                                round(v(on, WL[3], "EDF", "Average Waiting Time"), 2)), (69.17, 69.5)),
        ("HOT tardiness EDF/TA", (v(on, WL[3], "EDF", "Total Tardiness"), v(on, WL[3], "TA-EDF", "Total Tardiness")), (368, 369)),
        ("max EDF/TA waiting gap<=0.5", max(abs(v(d, w, "EDF", "Average Waiting Time") - v(d, w, "TA-EDF", "Average Waiting Time"))
                                            for d in (on, off) for w in WL) <= 0.5 + 1e-9, True),
        ("max EDF/TA tardiness gap", max(abs(v(d, w, "EDF", "Total Tardiness") - v(d, w, "TA-EDF", "Total Tardiness"))
                                         for d in (on, off) for w in WL), 2),
        ("EDF variant min everywhere", all(min(v(d, w, "EDF", m), v(d, w, "TA-EDF", m)) <= min(v(d, w, p, m) for p in POL) + 1e-9
                                           for d in (on, off) for w in WL for m in ("Average Waiting Time", "Total Tardiness")), True),
        ("EDF-NP Burst tie", round(v(on, WL[1], "EDF-NP", "Average Waiting Time"), 2), 4.33),
        ("RR HOT tardiness on", v(on, WL[3], "Round Robin", "Total Tardiness"), 697),
        ("RR worst / EEVDF 2nd waiting", all(sorted(POL, key=lambda p: v(d, w, p, "Average Waiting Time"))[-2:] == ["EEVDF-inspired", "Round Robin"]
                                             for d in (on, off) for w in WL), True),
        ("misses S/H", sorted({(p, v(d, w, p, "Deadline Misses")) for d in (on, off) for w in WL[2:] for p in ("Round Robin", "EEVDF-inspired", "EDF", "FCFS")}),
         sorted({("Round Robin", 6), ("EEVDF-inspired", 6), ("EDF", 4), ("FCFS", 4)})),
        ("HOT exposure on all zero", int(B[B.DVFS == on]["Thermal Exposure (HOT core-ticks)"].sum()), 0),
        ("ge60 Sus on RR/TA/EDF", tuple(v(on, WL[2], p, "Core-ticks >= 60C") for p in ("Round Robin", "TA-EDF", "EDF")), (5, 28, 108)),
        ("ge60 HOT on RR/TA/EDF", tuple(v(on, WL[3], p, "Core-ticks >= 60C") for p in ("Round Robin", "TA-EDF", "EDF")), (49, 257, 286)),
        ("zero-overhead peak gap range", (round(min(zero_gap), 2), round(max(zero_gap), 2)), (0.08, 2.49)),
        ("throttled HOT TA/EDF", (v(on, WL[3], "TA-EDF", "Throttled Busy Core-ticks"), v(on, WL[3], "EDF", "Throttled Busy Core-ticks")), (321, 294)),
        ("HOT exposure off", tuple(v(off, WL[3], p, "Thermal Exposure (HOT core-ticks)") for p in
                                   ("Round Robin", "TA-EDF", "EDF-NP", "FCFS", "Priority", "ThermOS-VR", "EDF", "EEVDF-inspired")),
         (18, 26, 35, 64, 64, 64, 65, 104)),
        ("HOT exposure off only HOT", sorted(B[(B.DVFS == off) & (B["Thermal Exposure (HOT core-ticks)"] > 0)].Workload.unique()), [WL[3]]),
        ("ge60 off TA vs EDF", (v(off, WL[2], "TA-EDF", "Core-ticks >= 60C"), v(off, WL[2], "EDF", "Core-ticks >= 60C"),
                                v(off, WL[3], "TA-EDF", "Core-ticks >= 60C"), v(off, WL[3], "EDF", "Core-ticks >= 60C")), (154, 137, 304, 299)),
        ("heat off identical", tuple(round(B[(B.DVFS == off) & (B.Workload == w)]["Heat Generated (model units)"].agg(lambda x: x.max() - x.min()), 9) for w in WL), (0, 0, 0, 0)),
        ("heat off values", tuple(round(v(off, w, "FCFS", "Heat Generated (model units)"), 2) for w in WL), (18.2, 58.0, 205.0, 359.25)),
        ("TA migrations on", tuple(v(on, w, "TA-EDF", "Migrations") for w in WL), (8, 41, 77, 193)),
        ("TA migrations off", tuple(v(off, w, "TA-EDF", "Migrations") for w in WL), (8, 41, 64, 114)),
        ("EDF migrations", int(B[B.Policy == "EDF"]["Migrations"].sum()), 0),
        ("EDF sens tardiness spread", int(S[S.Policy == "EDF"].groupby(["DVFS", "Workload"])["Total Tardiness"].agg(lambda x: x.max() - x.min()).max()), 2),
        ("cs-only diff range", (D[D["Migration Cost"] == 0]["Total Tardiness"].min(), D[D["Migration Cost"] == 0]["Total Tardiness"].max()), (-4, 5)),
        ("mig>=0.1 count", len(m1), 96),
        ("mig>=0.1 all worse", bool((m1["Total Tardiness"] > 0).all() and (m1["Makespan"] > 0).all()), True),
        ("mig>=0.1 ranges", (m1["Total Tardiness"].min(), m1["Total Tardiness"].max(), m1["Makespan"].min(), m1["Makespan"].max()), (1, 365, 2, 121)),
        ("Burst extra misses", (D[(D["Migration Cost"] >= 0.25) & (D.Workload == WL[1])]["Deadline Misses"].min(),
                                D[(D["Migration Cost"] >= 0.25) & (D.Workload == WL[1])]["Deadline Misses"].max()), (3, 4)),
        ("HOT 0.5 on extra miss", sorted(D[(D["Migration Cost"] == 0.5) & (D.Workload == WL[3]) & (D.DVFS == on)]["Deadline Misses"].unique()), [1]),
        ("N/S/H peak below EDF range", (round(-nsh.max(), 2), round(-nsh.min(), 2)), (0.99, 2.49)),
        ("N/S/H always below", bool((nsh < 0).all()), True),
        ("Burst above range", (round(burst_pos.min(), 2), round(burst_pos.max(), 2)), (0.7, 3.93)),
        ("workload totals", tuple(int(tasks[w].Burst.sum()) for w in WL), (28, 63, 245, 405)),
        ("deadline ranges", tuple((int(tasks[w].Deadline.min()), int(tasks[w].Deadline.max())) for w in WL),
         ((8, 20), (10, 24), (45, 60), (75, 100))),
        ("thermal params", (META["thermal_parameters"]["ambient_temperature"], META["thermal_parameters"]["initial_temperature"],
                            META["thermal_parameters"]["heat_coefficient"], META["thermal_parameters"]["cooling_coefficient"]),
         (25.0, 45.0, 1.0, 0.02)),
        ("steady state 2.5/2.2", (round(25 + 1 / 0.02, 1), round(25 + (2.2 / 2.5) ** 2 / 0.02, 1)), (75.0, 63.7)),
        ("off Sus EDF=TA waiting/tardiness", (round(v(off, WL[2], "EDF", "Average Waiting Time"), 2),
                                              round(v(off, WL[2], "TA-EDF", "Average Waiting Time"), 2),
                                              v(off, WL[2], "EDF", "Total Tardiness"), v(off, WL[2], "TA-EDF", "Total Tardiness")),
         (39.17, 39.17, 182, 182)),
        ("off HOT waiting EDF/TA, tardiness tie", (round(v(off, WL[3], "EDF", "Average Waiting Time"), 2),
                                                   round(v(off, WL[3], "TA-EDF", "Average Waiting Time"), 2),
                                                   v(off, WL[3], "EDF", "Total Tardiness"), v(off, WL[3], "TA-EDF", "Total Tardiness")),
         (64.17, 64.33, 305, 305)),
        ("HOT inter-core |dT| on EDF/TA/FCFS, off EDF/TA",
         (imbalance(on, "EDF"), imbalance(on, "TA-EDF"), imbalance(on, "FCFS"),
          imbalance(off, "EDF"), imbalance(off, "TA-EDF")), (3.22, 1.43, 0.72, 5.58, 3.01)),
    ]
    bad = [(n, got, exp) for n, got, exp in F if not (got == exp or (isinstance(got, float) and abs(got - exp) < 1e-9))]
    for n, got, exp in F:
        LOG.append(f"[{'OK ' if (n, got, exp) not in bad else 'BAD'}] {n}: {got}")
    if bad:
        raise SystemExit(f"FACT CHECK FAILED: {bad}")
    return len(F)


# ======================================================================
# Tables (generated from CSV)
# ======================================================================
def f2(x):
    return f"{x:.2f}"


def fi(x):
    return f"{int(round(x))}"


def ps(p):
    return POL_SHORT.get(p, p)


def bold_min(values):
    m = min(values)
    return [abs(x - m) < 1e-9 for x in values]


def tab_params():
    tp = META["thermal_parameters"]
    rows = [
        ["Cores", "2, identical (labels only)"],
        ["Initial / ambient temperature", f"{tp['initial_temperature']:g} °C / {tp['ambient_temperature']:g} °C"],
        ["Heat per busy tick", f"α(w/100)(f/2.5)², α = {tp['heat_coefficient']:g}"],
        ["Cooling per tick", f"β(T − 25), β = {tp['cooling_coefficient']:g}"],
        ["Thermal states", "COOL < 60, WARM < 70, HOT < 80 °C"],
        ["Frequency levels", "2.5, 2.2, 1.8, 1.4 GHz"],
        ["Work per tick", "f / 2.5 GHz units"],
        ["Governor down / up", "60, 70, 80 / 58, 68, 78 °C"],
        ["DVFS settings", "off (2.5 GHz), hysteresis"],
        ["TA-EDF rules", "urgent s ≤ 2; hold-back T ≥ 59 °C, s ≥ 10"],
        ["EEVDF slice / weights", "1 tick; 9548, 3121, 1024, 335, 110"],
        ["Overhead costs (sensitivity)", "{0, 0.1, 0.25, 0.5} work units"],
        ["Runs", "64 benchmark; 1,024 sensitivity"],
    ]
    return dict(caption="Simulation parameters (from run metadata and source code)",
                head=[[("Parameter", 1), ("Value", 1)]], rows=rows, bold=None, wide=False,
                align="ll", colw=[1.45, 1.95])


def tab_policies():
    rows = [
        ["FCFS", "arrival", "no", "lowest free core", "no", "no"],
        ["Priority", "priority, arrival", "no", "lowest free core", "no", "no"],
        ["Round Robin", "FIFO queue, quantum 1", "yes", "lowest free core", "no", "no"],
        ["ThermOS-VR", "arrival", "no", "max. score S (3)", "constant term", "yes"],
        ["EDF-NP", "absolute deadline", "no", "lowest free core", "yes", "no"],
        ["EDF", "absolute deadline", "yes", "keep core, else lowest free", "yes", "no"],
        ["TA-EDF (ours)", "absolute deadline", "yes", "urgent: fastest; else coolest", "yes (slack)", "yes"],
        ["EEVDF-inspired", "eligible, virtual deadline", "yes", "keep core, else lowest free", "no", "no"],
    ]
    return dict(caption="Scheduling policies evaluated. Ties: earlier arrival, then lower task "
                        "identifier. Late tasks are never dropped.",
                head=[[("Policy", 1), ("Task order", 1), ("Preemptive", 1), ("Core choice", 1),
                       ("Deadline", 1), ("Temperature", 1)]],
                rows=rows, bold=None, wide=True, align="llllll",
                colw=[1.15, 1.45, 0.75, 1.75, 0.95, 0.85])


def tab_workloads():
    rows, rules = [], []
    for w in WL:
        rid = B[(B.Workload == w) & (B.Policy == "FCFS") & (B.DVFS == "off")]["Run ID"].item()
        t = T[T["Run ID"] == rid].sort_values("PID")
        for i, r in enumerate(t.itertuples()):
            rows.append([WS[w] if i == 0 else "", str(r.PID), r.Task, fi(r.Arrival), fi(r.Burst),
                         fi(r.Deadline), fi(r.Priority), fi(r.Intensity)])
        work = int(t.Burst.sum())
        rows.append(["", "", f"Total work {work}; two-core bound {work / 2:g}", "", "", "", "", ""])
        rules.append(len(rows))
    return dict(caption="Workloads: six one-shot tasks each (times in ticks, intensity in %). The "
                        "bound is total work divided by two cores at full speed.",
                head=[[("Workload", 1), ("ID", 1), ("Task", 1), ("Arr.", 1), ("Burst", 1),
                       ("Deadline", 1), ("Prio.", 1), ("Int.", 1)]],
                rows=rows, bold=None, wide=True, align="lllrrrrr", rules=rules,
                colw=[0.8, 0.35, 2.55, 0.5, 0.55, 0.7, 0.5, 0.5], italic_rows=rules)


def group_head(groups, sub):
    top = [("Policy", 1)] + [(g, len(sub)) for g in groups]
    bottom = [("", 1)] + [(s, 1) for _ in groups for s in sub]
    return [top, bottom]


def tab_resp():
    d = "hysteresis"
    rows, bold = [], []
    cols = [(w, m) for w in WL for m in ("Average Waiting Time", "Total Tardiness", "Deadline Misses")]
    colvals = [[v(d, w, p, m) for p in POL] for w, m in cols]
    colbold = [bold_min(c) for c in colvals]
    for i, p in enumerate(POL):
        row = [ps(p)]
        brow = [False]
        for j, (w, m) in enumerate(cols):
            x = colvals[j][i]
            row.append(f2(x) if m == "Average Waiting Time" else fi(x))
            brow.append(colbold[j][i])
        rows.append(row)
        bold.append(brow)
    return dict(caption="Responsiveness with DVFS enabled: average waiting time W and total "
                        "tardiness T (ticks), and deadline misses M (of 6). Bold marks the minimum, "
                        "including ties.",
                head=group_head([WS[w] for w in WL], ["W", "T", "M"]), rows=rows, bold=bold,
                wide=True, align="l" + "r" * 12, colw=[1.0] + [0.49] * 12)


def tab_thermon():
    d = "hysteresis"
    spec = [("Peak °C", "Peak Temperature", WL, f2), ("Core-ticks ≥ 60 °C", "Core-ticks >= 60C", WL[2:], fi),
            ("Throttled busy core-ticks", "Throttled Busy Core-ticks", WL[2:], fi),
            ("Migrations", "Migrations", WL[2:], fi), ("Makespan", "Makespan", WL[2:], fi)]
    top = [("Policy", 1)] + [(g, len(ws)) for g, _, ws, _ in spec]
    bottom = [("", 1)] + [(WS[w][0] if g == "Peak °C" else WS[w][:3], 1) for g, _, ws, _ in spec for w in ws]
    rows = []
    for p in POL:
        row = [ps(p)]
        for g, m, ws, fmt in spec:
            row += [fmt(v(d, w, p, m)) for w in ws]
        rows.append(row)
    return dict(caption="Simulated thermal outcomes with DVFS enabled (model °C, core-ticks). "
                        "Peak: N, B, S, H workloads; other columns: Sustained and HOT only, because "
                        "Normal and Burst never reach 60 °C. No run reached the HOT state.",
                head=[top, bottom], rows=rows, bold=None, wide=True, align="l" + "r" * 12,
                colw=[1.0] + [0.49] * 12)


def tab_thermoff():
    d = "off"
    spec = [("Peak °C", "Peak Temperature", WL[2:], f2), ("HOT c.-t.", "Thermal Exposure (HOT core-ticks)", WL[3:], fi),
            ("≥ 60 °C", "Core-ticks >= 60C", WL[2:], fi), ("Waiting", "Average Waiting Time", WL[2:], f2),
            ("Tardiness", "Total Tardiness", WL[2:], fi)]
    top = [("Policy", 1)] + [(g, len(ws)) for g, _, ws, _ in spec]
    bottom = [("", 1)] + [(WS[w][:3], 1) for g, _, ws, _ in spec for w in ws]
    rows = []
    for p in POL:
        row = [ps(p)]
        for g, m, ws, fmt in spec:
            row += [fmt(v(d, w, p, m)) for w in ws]
        rows.append(row)
    return dict(caption="DVFS disabled (fixed 2.5 GHz), Sustained (Sus) and HOT workloads. Total "
                        "model heat is identical for all policies in each workload.",
                head=[top, bottom], rows=rows, bold=None, wide=True, align="l" + "r" * 9,
                colw=[1.1] + [0.62] * 9)


def tab_sens():
    D = sens_diff()
    D = D[D["Context Switch Cost"] == 0]
    spec = [("Δ tardiness (ticks)", "Total Tardiness", fi), ("Δ makespan (ticks)", "Makespan", fi),
            ("Δ peak (°C)", "Peak Temperature", lambda x: f"{x:+.2f}")]
    top = [("DVFS, cost", 1)] + [(g, 4) for g, _, _ in spec]
    bottom = [("", 1)] + [(WS[w][0], 1) for _ in spec for w in WL]
    rows = []
    for dv, lab in (("hysteresis", "on"), ("off", "off")):
        for c in (0.0, 0.1, 0.25, 0.5):
            row = [f"{lab}, {c:g}"]
            for g, m, fmt in spec:
                for w in WL:
                    x = D[(D.DVFS == dv) & (D.Workload == w) & (D["Migration Cost"] == c)][m].item()
                    row.append(fmt(x) if m == "Peak Temperature" else f"{int(x):+d}" if x else "0")
            rows.append(row)
    return dict(caption="TA-EDF minus EDF at each migration cost (simulated work units; "
                        "context-switch cost 0), matched on workload (N, B, S, H) and DVFS setting. "
                        "Positive Δ tardiness or makespan means TA-EDF is worse.",
                head=[top, bottom], rows=rows, bold=None, wide=True, align="l" + "r" * 12,
                colw=[0.85] + [0.505] * 12, rules=[4])


def tab_verify():
    rows = [
        ["Unit tests (python -B -m unittest)", "42 tests, OK"],
        ["Metrics recomputed from raw traces", "1,024 values, all equal"],
        ["Fresh re-runs", "64 + 1,024 runs, identical"],
        ["Figures vs CSV", "768 plotted values; 25/25 PNGs pixel-identical"],
        ["EDF vs independent reference", "18,024 comparisons, 0 mismatches"],
        ["v1 equivalence (4 policies)", "exact task outcomes and temperatures"],
        ["Zero-overhead sensitivity rows", "equal benchmark (64 × 16 metrics)"],
        ["Numbers quoted in this paper", "asserted against the CSVs at build"],
        ["Preservation", "179 frozen files, SHA-256 unchanged"],
    ]
    return dict(caption="Verification performed on the final code and outputs",
                head=[[("Check", 1), ("Result", 1)]], rows=rows, bold=None, wide=False,
                align="ll", colw=[1.75, 1.65],
                # plain "ll" is 33.6 pt wider than the column in LaTeX
                tex_align=r">{\raggedright\arraybackslash}p{0.43\columnwidth}"
                          r">{\raggedright\arraybackslash}p{0.49\columnwidth}")


TABLES = {"tab:params": tab_params, "tab:policies": tab_policies, "tab:workloads": tab_workloads,
          "tab:resp": tab_resp, "tab:thermon": tab_thermon, "tab:thermoff": tab_thermoff,
          "tab:sens": tab_sens, "tab:verify": tab_verify}

# ======================================================================
# Inline tokenizer
# ======================================================================
TOKEN = re.compile(r"\[@([^\]]+)\]|\{\{([^}]+)\}\}|`([^`]+)`|\*([^*]+)\*")
SUB = re.compile(r"([A-Za-zαβℓ])_(\{[^}]+\}|[A-Za-z0-9]+)")


def tokenize(text):
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            out += split_sub(text[pos:m.start()], "text")
        if m.group(1):
            out.append(("cite", [k.strip().lstrip("@") for k in m.group(1).split(";")]))
        elif m.group(2):
            out.append(("ref", m.group(2)))
        elif m.group(3):
            out.append(("code", m.group(3)))
        else:
            out += split_sub(m.group(4), "em")
        pos = m.end()
    if pos < len(text):
        out += split_sub(text[pos:], "text")
    return out


def split_sub(s, kind):
    out, pos = [], 0
    for m in SUB.finditer(s):
        if m.start() > pos:
            out.append((kind, s[pos:m.start()]))
        out.append((kind, m.group(1)))
        out.append(("sub", m.group(2).strip("{}")))
        pos = m.end()
    if pos < len(s):
        out.append((kind, s[pos:]))
    return out


# ======================================================================
# Numbering: sections, tables, figures, equations, citations
# ======================================================================
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]
LETTERS = "ABCDEFGHIJ"


def number_things():
    sec, sub, tab, fig, eq = {}, {}, {}, {}, {}
    s = ss = 0
    for b in C.BODY:
        if b[0] == "h1":
            s += 1
            ss = 0
            sec[b[1]] = ROMAN[s - 1]
        elif b[0] == "h2":
            ss += 1
            sec[b[1]] = f"{ROMAN[s - 1]}-{LETTERS[ss - 1]}"
        elif b[0] == "table":
            tab[b[1]] = ROMAN[len(tab)]
        elif b[0] == "figure":
            fig[b[1]] = len(fig) + 1
        elif b[0] == "eq":
            eq[b[1]] = len(eq) + 1
    return sec, tab, fig, eq


SEC, TAB, FIG, EQN = number_things()


def cite_order():
    order = []
    texts = [C.ABSTRACT] + [b[1] for b in C.BODY if b[0] == "p"] + \
            [i for b in C.BODY if b[0] == "ul" for i in b[1]]
    # keep document order: walk BODY properly
    texts = [C.ABSTRACT]
    for b in C.BODY:
        if b[0] == "p":
            texts.append(b[1])
        elif b[0] == "ul":
            texts.extend(b[1])
    for t in texts:
        for kind, val in tokenize(t):
            if kind == "cite":
                for k in val:
                    if k not in REFS_KEYS:
                        raise SystemExit(f"unknown citation key {k}")
                    if k not in order:
                        order.append(k)
    return order


REFS_KEYS = set(R.REFS)
CITE_ORDER = cite_order()
CITE_NUM = {k: i + 1 for i, k in enumerate(CITE_ORDER)}


def cite_label(keys):
    nums = sorted(CITE_NUM[k] for k in keys)
    parts, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        parts.append(f"[{nums[i]}]–[{nums[j]}]" if j - i >= 2 else
                     ", ".join(f"[{n}]" for n in nums[i:j + 1]))
        i = j + 1
    return ", ".join(parts)


def ref_text(key):
    if key.startswith("tab:"):
        return f"Table {TAB[key]}"
    if key.startswith("fig:"):
        return f"Fig. {FIG[key]}"
    if key.startswith("eq:"):
        return f"({EQN[key]})"
    return f"Section {SEC[key].split('-')[0]}" if "-" not in SEC[key] else f"Section {SEC[key]}"


# ======================================================================
# DOCX renderer
# ======================================================================
def build_docx(path):
    from docx import Document
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, Inches

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    st.font.size = Pt(10)
    pf = st.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

    def set_cols(section, n):
        sectPr = section._sectPr
        for c in sectPr.findall(qn("w:cols")):
            sectPr.remove(c)
        cols = OxmlElement("w:cols")
        cols.set(qn("w:num"), str(n))
        cols.set(qn("w:space"), "360")
        sectPr.append(cols)

    def page_setup(section):
        section.page_width, section.page_height = Inches(8.5), Inches(11)
        section.top_margin, section.bottom_margin = Inches(0.75), Inches(1.0)
        section.left_margin = section.right_margin = Inches(0.625)

    sec0 = doc.sections[0]
    page_setup(sec0)
    set_cols(sec0, 1)

    def runs(par, text, size=None, bold=False, italic=False):
        for kind, val in tokenize(text):
            if kind == "cite":
                r = par.add_run(cite_label(val))
            elif kind == "ref":
                r = par.add_run(ref_text(val))
            elif kind == "code":
                r = par.add_run(val)
                r.font.name = "Courier New"
                r.font.size = Pt((size or 10) - 1)
                continue
            elif kind == "sub":
                r = par.add_run(val)
                r.font.subscript = True
                r.italic = italic
            else:
                r = par.add_run(val)
                r.italic = italic or kind == "em"
            r.bold = bold
            if size:
                r.font.size = Pt(size)

    def para(text, size=10, indent=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, bold=False, italic=False,
             space_after=0):
        p = doc.add_paragraph()
        p.alignment = align
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.14)
        p.paragraph_format.space_after = Pt(space_after)
        runs(p, text, size=size, bold=bold, italic=italic)
        return p

    def switch(ncols):
        s = doc.add_section(WD_SECTION.CONTINUOUS)
        page_setup(s)
        set_cols(s, ncols)

    # ---- title block (one column)
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run(C.TITLE)
    r.font.size = Pt(20)
    t.paragraph_format.space_after = Pt(10)
    a = doc.add_paragraph()
    a.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, (name, reg) in enumerate(C.AUTHORS):
        rr = a.add_run(f"{name} ({reg})")
        rr.font.size = Pt(11)
        if i < len(C.AUTHORS) - 1:
            a.add_run(",   ").font.size = Pt(11)
    a2 = doc.add_paragraph()
    a2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ra = a2.add_run(C.AFFILIATION)
    ra.italic = True
    ra.font.size = Pt(10)
    a2.paragraph_format.space_after = Pt(12)

    switch(2)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    h = p.add_run("Abstract—")
    h.bold = h.italic = True
    h.font.size = Pt(9)
    runs(p, C.ABSTRACT, size=9, bold=True)
    p.paragraph_format.space_after = Pt(6)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    h = p.add_run("Index Terms—")
    h.bold = h.italic = True
    h.font.size = Pt(9)
    rr = p.add_run(C.INDEX_TERMS)
    rr.bold = True
    rr.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(6)

    col_w = 3.5

    def add_table(key):
        spec = TABLES[key]()
        wide = spec["wide"]
        if wide:
            switch(1)
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_before = Pt(6)
        c1 = cap.add_run(f"TABLE {TAB[key]}")
        c1.font.size = Pt(8)
        cap2 = doc.add_paragraph()
        cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap2.paragraph_format.space_after = Pt(3)
        runs(cap2, spec["caption"].upper() if False else spec["caption"], size=8)
        ncol = sum(span for _, span in spec["head"][0])
        tb = doc.add_table(rows=0, cols=ncol)
        tb.style = "Table Grid"
        tb.alignment = WD_TABLE_ALIGNMENT.CENTER
        fs = 7 if wide else 7.5
        for hr in spec["head"]:
            cells = tb.add_row().cells
            ci = 0
            for text, span in hr:
                cell = cells[ci]
                if span > 1:
                    cell = cell.merge(cells[ci + span - 1])
                cell.text = ""
                pp = cell.paragraphs[0]
                pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                rr = pp.add_run(text)
                rr.bold = True
                rr.font.size = Pt(fs)
                ci += span
        italic_rows = set(spec.get("italic_rows", []))
        for ri, row in enumerate(spec["rows"]):
            cells = tb.add_row().cells
            if ri + 1 in italic_rows:
                merged = cells[2].merge(cells[-1])
                merged.text = ""
                rr = merged.paragraphs[0].add_run(row[2])
                rr.italic = True
                rr.font.size = Pt(fs)
                for ci in (0, 1):
                    cells[ci].text = ""
                continue
            for ci, text in enumerate(row):
                cell = cells[ci]
                cell.text = ""
                pp = cell.paragraphs[0]
                pp.alignment = (WD_ALIGN_PARAGRAPH.LEFT if spec["align"][ci] == "l"
                                else WD_ALIGN_PARAGRAPH.RIGHT)
                rr = pp.add_run(text)
                rr.font.size = Pt(fs)
                if spec["bold"] and spec["bold"][ri][ci]:
                    rr.bold = True
        for ci, wdt in enumerate(spec["colw"]):
            for row in tb.rows:
                try:
                    row.cells[ci].width = Inches(wdt)
                except IndexError:
                    pass
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        if wide:
            switch(2)

    def add_figure(key):
        f = C.FIGURES[key]
        if f["wide"]:
            switch(1)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.add_run().add_picture(os.path.join(HERE, "figures", os.path.basename(f["path"])),
                                width=Inches(f["width_in"] if f["wide"] else min(f["width_in"], col_w)))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        cp.paragraph_format.space_after = Pt(6)
        r1 = cp.add_run(f"Fig. {FIG[key]}. ")
        r1.font.size = Pt(8)
        runs(cp, f["caption"], size=8)
        if f["wide"]:
            switch(2)

    for b in C.BODY:
        kind = b[0]
        if kind == "h1":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(f"{SEC[b[1]]}. {b[2].upper()}")
            r.font.size = Pt(10)
        elif kind == "h2":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(f"{SEC[b[1]].split('-')[1]}. {b[2]}")
            r.italic = True
        elif kind == "p":
            para(b[1])
        elif kind == "ul":
            for item in b[1]:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.left_indent = Inches(0.2)
                p.paragraph_format.first_line_indent = Inches(-0.12)
                p.add_run("• ")
                runs(p, item)
        elif kind == "eq":
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(col_w / 2), WD_TAB_ALIGNMENT.CENTER)
            p.paragraph_format.tab_stops.add_tab_stop(Inches(col_w), WD_TAB_ALIGNMENT.RIGHT)
            p.add_run("\t")
            runs(p, b[3], italic=True)
            p.add_run(f"\t({EQN[b[1]]})")
        elif kind == "table":
            add_table(b[1])
        elif kind == "figure":
            add_figure(b[1])

    # references
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.add_run("REFERENCES").font.size = Pt(10)
    for k in CITE_ORDER:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.3)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        r1 = p.add_run(f"[{CITE_NUM[k]}]\t")
        r1.font.size = Pt(8)
        r2 = p.add_run(R.ieee_plain(k).replace("--", "–"))
        r2.font.size = Pt(8)
    doc.core_properties.title = C.TITLE
    doc.core_properties.author = ", ".join(n for n, _ in C.AUTHORS)
    doc.save(path)


# ======================================================================
# LaTeX renderer
# ======================================================================
TEX_MAP = [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"),
           ("$", r"\$"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\^{}")]
UNI = {"°": r"\textdegree{}", "≥": r"$\geq$", "≤": r"$\leq$", "−": r"$-$", "×": r"$\times$",
       "→": r"$\rightarrow$", "π": r"$\pi$", "κ": r"$\kappa$", "δ": r"$\delta$", "ℓ": r"$\ell$",
       "α": r"$\alpha$", "β": r"$\beta$", "Σ": r"$\Sigma$", "²": r"\textsuperscript{2}",
       "–": "--", "—": "---", "“": "``", "”": "''", "’": "'", "é": r"\'{e}", "í": r"\'{i}",
       "ü": r"\"{u}", "≈": r"$\approx$", "Δ": r"$\Delta$", "•": r"\textbullet{}", "±": r"$\pm$"}


def tex_escape(s):
    for a, b in TEX_MAP:
        s = s.replace(a, "\x00" + str(TEX_MAP.index((a, b))) + "\x00")
    for i, (a, b) in enumerate(TEX_MAP):
        s = s.replace("\x00" + str(i) + "\x00", b)
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    for a, b in UNI.items():
        s = s.replace(a, b)
    return s


def tex_inline(text):
    out = []
    for kind, val in tokenize(text):
        if kind == "cite":
            out.append(r"~\cite{" + ",".join(val) + "}")
        elif kind == "ref":
            if val.startswith("tab:"):
                out.append(r"Table~\ref{" + val + "}")
            elif val.startswith("fig:"):
                out.append(r"Fig.~\ref{" + val + "}")
            elif val.startswith("eq:"):
                out.append(r"\eqref{" + val + "}")
            else:
                out.append(r"Section~\ref{" + val + "}")
        elif kind == "code":
            out.append(r"\texttt{" + tex_escape(val) + "}")
        elif kind == "sub":
            out.append(r"\textsubscript{" + tex_escape(val) + "}")
        elif kind == "em":
            out.append(r"\emph{" + tex_escape(val) + "}")
        else:
            out.append(tex_escape(val))
    s = "".join(out)
    return s.replace(" ~\\cite", "~\\cite")


def tex_table(key):
    spec = TABLES[key]()
    env = "table*" if spec["wide"] else "table"
    ncol = sum(span for _, span in spec["head"][0])
    L = [rf"\begin{{{env}}}[!t]", r"\centering", r"\scriptsize" if spec["wide"] else r"\footnotesize",
         rf"\caption{{{tex_inline(spec['caption'])}}}", rf"\label{{{key}}}",
         r"\setlength{\tabcolsep}{3pt}",
         rf"\begin{{tabular}}{{{spec.get('tex_align', spec['align'])}}}", r"\toprule"]
    for hi, hr in enumerate(spec["head"]):
        cells, col, rules = [], 1, []
        for text, span in hr:
            t = tex_inline(text)
            if span > 1:
                cells.append(rf"\multicolumn{{{span}}}{{c}}{{{t}}}")
                rules.append(rf"\cmidrule(lr){{{col}-{col + span - 1}}}")
            else:
                cells.append(t)
            col += span
        L.append(" & ".join(cells) + r" \\")
        if hi < len(spec["head"]) - 1 and rules:
            L.append(" ".join(rules))
    L.append(r"\midrule")
    italic_rows = set(spec.get("italic_rows", []))
    for ri, row in enumerate(spec["rows"]):
        if ri + 1 in italic_rows:
            L.append(rf" & & \multicolumn{{{ncol - 2}}}{{l}}{{\emph{{{tex_inline(row[2])}}}}} \\")
            if ri + 1 != len(spec["rows"]):
                L.append(r"\midrule")
            continue
        cells = []
        for ci, c in enumerate(row):
            t = tex_inline(c)
            if spec["bold"] and spec["bold"][ri][ci]:
                t = r"\textbf{" + t + "}"
            cells.append(t)
        L.append(" & ".join(cells) + r" \\")
        if ri + 1 in set(spec.get("rules", [])) and ri + 1 not in italic_rows:
            L.append(r"\midrule")
    L += [r"\bottomrule", r"\end{tabular}", rf"\end{{{env}}}", ""]
    return "\n".join(L)


def tex_figure(key):
    f = C.FIGURES[key]
    env = "figure*" if f["wide"] else "figure"
    width = r"\textwidth" if f["wide"] else r"\columnwidth"
    return "\n".join([rf"\begin{{{env}}}[!t]", r"\centering",
                      rf"\includegraphics[width={width}]{{figures/{os.path.basename(f['path'])}}}",
                      rf"\caption{{{tex_inline(f['caption'])}}}", rf"\label{{{key}}}",
                      rf"\end{{{env}}}", ""])


def build_tex(path):
    L = [r"\documentclass[conference]{IEEEtran}",
         r"% Compile: pdflatex, bibtex, pdflatex, pdflatex (IEEEtran.cls and IEEEtran.bst required).",
         r"\usepackage{cite}", r"\usepackage{amsmath,amssymb}", r"\usepackage{graphicx}",
         r"\usepackage{textcomp}", r"\usepackage{array}", r"\usepackage{booktabs}",
         r"\usepackage[hyphens]{url}",
         r"\usepackage[T1]{fontenc}", "",
         r"\begin{document}", "",
         rf"\title{{{tex_escape(C.TITLE)}}}", "",
         r"\author{\IEEEauthorblockN{" + r" \quad ".join(
             f"{tex_escape(n)} ({r})" for n, r in C.AUTHORS) + "}",
         r"\IEEEauthorblockA{\textit{" + tex_escape(C.AFFILIATION) + "}}}", "",
         r"\maketitle", "",
         r"\begin{abstract}", tex_inline(C.ABSTRACT), r"\end{abstract}", "",
         r"\begin{IEEEkeywords}", tex_escape(C.INDEX_TERMS), r"\end{IEEEkeywords}", ""]
    for b in C.BODY:
        kind = b[0]
        if kind == "h1":
            L.append(rf"\section{{{tex_escape(b[2])}}}\label{{{b[1]}}}")
        elif kind == "h2":
            L.append(rf"\subsection{{{tex_escape(b[2])}}}\label{{{b[1]}}}")
        elif kind == "p":
            L += [tex_inline(b[1]), ""]
        elif kind == "ul":
            L.append(r"\begin{itemize}")
            L += [r"\item " + tex_inline(i) for i in b[1]]
            L += [r"\end{itemize}", ""]
        elif kind == "eq":
            L += [r"\begin{equation}", b[2], rf"\label{{{b[1]}}}", r"\end{equation}", ""]
        elif kind == "table":
            L.append(tex_table(b[1]))
        elif kind == "figure":
            L.append(tex_figure(b[1]))
    L += [r"\bibliographystyle{IEEEtran}", r"\bibliography{references}", "", r"\end{document}", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ======================================================================
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    n = facts()
    uncited = sorted(set(R.REFS) - set(CITE_ORDER))
    if uncited:
        raise SystemExit(f"References never cited (would be padding): {uncited}")
    os.makedirs(os.path.join(HERE, "figures"), exist_ok=True)
    copies = []
    for key, f in C.FIGURES.items():
        src = os.path.join(ROOT, f["path"])
        dst = os.path.join(HERE, "figures", os.path.basename(f["path"]))
        if os.path.abspath(src) != os.path.abspath(dst):
            shutil.copy2(src, dst)
            assert sha(src) == sha(dst)
            copies.append(f"copied {f['path']} -> figures/{os.path.basename(dst)} (sha256 equal)")
    with open(os.path.join(HERE, "references.bib"), "w", encoding="utf-8") as f:
        f.write(R.bibtex())
    build_tex(os.path.join(HERE, "ThermOS_VR_Research_Report.tex"))
    build_docx(os.path.join(HERE, "ThermOS_VR_Research_Report.docx"))
    words = sum(len(re.sub(r"\[@[^\]]+\]|\{\{[^}]+\}\}", "", t).split())
                for t in [C.ABSTRACT] + [b[1] for b in C.BODY if b[0] == "p"] +
                [i for b in C.BODY if b[0] == "ul" for i in b[1]])
    report = [f"Build OK. {n} prose facts asserted against CSVs.",
              f"Citations: {len(CITE_ORDER)} references cited, 0 uncited; order of first appearance:",
              "  " + ", ".join(f"[{CITE_NUM[k]}] {k}" for k in CITE_ORDER),
              f"Tables: {len(TAB)}; figures: {len(FIG)}; equations: {len(EQN)}; body words ~{words}",
              *copies, "", "Fact log:", *LOG]
    with open(os.path.join(HERE, "build_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report[:5]))


if __name__ == "__main__":
    main()
