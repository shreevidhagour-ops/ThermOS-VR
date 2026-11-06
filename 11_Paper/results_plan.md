# Results Plan: tables and figures (preparation phase 1)

Prepared 2026-10-21. **No figure or table has been generated or modified.** Everything below maps to existing, checksummed files (`11_Paper/evidence_freeze_manifest_2026-10-21.sha256`). Claim IDs refer to `claim_evidence_matrix.md`.

## Ground rules for every table and figure

- **Units:** simulated °C, abstract ticks and unit-less model heat. Never W, J, mAh, ms or "device temperature".
- **Every caption must state:** deterministic Python simulation, two identical modelled cores, four workloads × six one-shot tasks, one run per configuration.
- **Keep DVFS settings apart:** DVFS-off and DVFS-on results always appear in separate tables or panels, each labelled.
- **No v1 baseline numbers:** nothing from `05_Results/experiment_results.csv` or the v1 PNGs in `06_Figures/` (root) is used as a baseline. Thermal-DVFS v1 is invalid (C4.2).
- **ThermOS-VR and FCFS:** where ThermOS-VR equals FCFS, say so in the caption rather than implying two distinct results (C3.1).
- **No significance language:** no "significantly", error bars or p-values.

---

## Proposed tables

| # | Table | Exact source | Metrics and units | Workloads / policies | Supports | Mandatory caveat |
|---|---|---|---|---|---|---|
| T1 | **Workload definitions and feasibility** | `05_Results/v2_modern_baselines/task_results.csv`, Runs 1, 9, 17, 25 (columns PID, Task, Arrival, Burst, Priority, Intensity, Deadline); `03_Code/day1_basic_scheduler/workloads.py` | ticks; intensity in % | 4 workloads, 6 tasks each | C1.2, C8.1, C8.2 | Add the derived total work and lower bound on makespan (work / 2): N 28 → 14; Bu 63 → 31.5; S 245 → 122.5; H 405 → 202.5. Burst, Sustained and HOT deadlines are partly or largely infeasible. |
| T2 | **Simulation parameters** | `05_Results/v2_modern_baselines/run_metadata.json` (`thermal_parameters`, `cores`); README (DVFS thresholds) | °C, GHz, ticks | — | C1.4, C2.1, C2.2 | Uncalibrated model; cores identical. |
| T3 | **Policy summary** (order, preemption, core choice, uses deadline, uses temperature) | `03_Code/day5_modern_baselines/README.md` "Policies" table | — | 8 policies | C5, C9, C10 | Mark TA-EDF as **ours**; label EEVDF as **inspired**; note EAS was not evaluated. |
| T4 | **Metric definitions** | `05_Results/v2_modern_baselines/metric_definitions.csv` | — | — | C1.5 | Use the corrected wording for *Migrations* (see the claim matrix). |
| T5 | **Responsiveness, DVFS on**: average waiting time, total tardiness, deadline misses, makespan | `benchmark_results.csv` Runs 33–64 | ticks; count | 4 workloads × 8 policies | C5.1–C5.4, C8.3 | Bold the best value **including ties**. Footnote: FCFS ≡ ThermOS-VR. Misses saturate in S and H. |
| T6 | **Simulated thermal outcomes, DVFS on**: peak temperature, average temperature, core-ticks ≥ 60 °C, throttled busy core-ticks, migrations | `benchmark_results.csv` Runs 33–64 | °C; core-ticks; count | same | C7.1, C7.3, C7.7, C10.4 | HOT exposure is 0 everywhere (do not tabulate, state it in the text). Round Robin's thermal advantage comes with the worst responsiveness (cross-reference T5). |
| T7 | **Simulated thermal outcomes, DVFS off**: peak temperature, HOT core-ticks, core-ticks ≥ 60 °C, heat generated | `benchmark_results.csv` Runs 1–32 | °C; core-ticks; model heat units | same | C7.2, C7.4 | Heat is identical across policies per workload (18.20 / 58.00 / 205.00 / 359.25): placement cannot change total heat in this model. HOT exposure is non-zero only in the HOT workload. |
| T8 | **DVFS effect for one policy** (FCFS: off vs on) | `benchmark_results.csv` Runs 1/33, 9/41, 17/49, 25/57 | peak °C, makespan, waiting | FCFS (≡ ThermOS-VR) | C3.2, C7.5 | Simulated trade-off. Optional; it could be folded into the text. |
| T9 | **Overhead sensitivity: TA-EDF − EDF** (tardiness, makespan, misses, peak °C, ≥ 60 °C) at migration cost 0 / 0.1 / 0.25 / 0.5 | `05_Results/v2_sensitivity/sensitivity_results.csv` (filter `Policy ∈ {EDF, TA-EDF}`, `Context Switch Cost = 0`; repeat for DVFS off); AF table | ticks; °C; core-ticks | 4 workloads; DVFS on (main) and off (appendix or text) | C6.1–C6.5 | Costs are hypothetical fractions of a tick. Also state the whole-grid result: 96 / 96 configurations worse for TA-EDF at migration cost ≥ 0.1. |
| T10 | **Context-switch-only sensitivity for preemptive policies** (tardiness at cs = 0 / 0.1 / 0.25, migration cost 0) | `sensitivity_results.csv` | ticks | RR, EEVDF-inspired, EDF, TA-EDF; S and H | C6.4, fairness note | Shows that the zero-overhead benchmark favours preemptive policies. |
| T11 | **v1 issues corrected** | `03_Code/day5_modern_baselines/CONFIRMED_BUGS.md` (B1–B8) | — | — | C4.1–C4.3 | Short; appendix-sized. |
| T12 | **Verification summary** (tests, recomputations, re-runs, pixel checks, checksums) | `05_Results/v2_sensitivity/validation_log_2026-10-21.txt`; `05_Results/v2_modern_baselines/test_and_verification_log.txt`; AF | counts | — | C5.5, C6.7 | Distinguish shipped checks from the audit-only probes run in session scratch. |

Recommended for the main text: T1, T3, T5, T6, T7, T9. The rest go to an appendix or are merged into text.

---

## Existing figures: suitability

All candidate figures are in `06_Figures/v2_modern_baselines/` (pixel-identical to re-renders of the CSV; `figure_manifest.csv` lists every plotted value).

Every figure is a 2 × 2 panel (one panel per workload) with 8 policies. That needs a full-width (two-column) figure in IEEE format, roughly 0.35–0.45 page each, so **use 4–5 figures at most**.

### Recommended

| Figure file | Measures | Claim supported | Caveat for the caption |
|---|---|---|---|
| `hysteresis_waiting_time.png` | Average waiting time (ticks), DVFS on | C5.1, C5.3 | FCFS ≡ ThermOS-VR; EDF ≈ TA-EDF; ties in Normal VR |
| `hysteresis_total_tardiness.png` | Total tardiness (ticks), DVFS on | C5.1, C8.3 | Overloaded workloads; misses not dropped |
| `hysteresis_peak_temperature.png` | Peak simulated temperature (dot plot, non-zero axis), DVFS on | C7.7 | Differences of 0.1–2.5 °C in a model; not significant; dot plot because the axis does not start at 0 |
| `hysteresis_core_ticks_above_60c.png` | Core-ticks ≥ 60 °C, DVFS on | C7.3 | Normal and Burst panels are all zero; RR is low only because of interleaving |
| `hysteresis_hot_temperature_trace.png` | Per-core temperature over time, HOT workload, DVFS on, for FCFS / ThermOS-VR / EDF / TA-EDF | C3.1, C10.4 (illustrative) | FCFS and ThermOS-VR panels look identical by construction; TA-EDF's two curves converge because of migrations; one workload only |

### Usable, but secondary (appendix)

| Figure file | Why secondary |
|---|---|
| `off_thermal_exposure.png` | Only the HOT panel is non-zero; T7 shows the same information more compactly |
| `off_peak_temperature.png` | Complements T7 |
| `off_waiting_time.png`, `off_total_tardiness.png` | Rankings nearly identical to DVFS on; one sentence suffices |
| `hysteresis_throttled_core_ticks.png` | Supports the TA-EDF throttling caveat (HOT: 321 vs 294) |

### Not recommended (redundant or misleading)

| Figure file | Problem |
|---|---|
| `hysteresis_thermal_exposure.png` | **All panels are zero**, so the figure carries no information. State "0 for all policies" in the text instead. |
| `*_completion_time.png`, `*_turnaround_time.png` | Largely redundant with waiting time: in this simulator turnaround = waiting + busy ticks for every task, and each tick between arrival and completion is one or the other |
| `*_utilization.png` | Low information (90–100 %); can mislead readers into reading utilisation as efficiency |
| `*_average_temperature.png` | Average temperature depends on run length and timing; in a linear model placement cannot change it (C7.4), and readers may over-interpret it. Use the T6/T7 values with a caveat, or omit. |
| `off_heat_generated.png` | All bars per workload are equal; one sentence or T7 is better |
| `hysteresis_heat_generated.png` | Unit-less model heat invites misreading as energy |
| **Any v1 figure in `06_Figures/` (root)**, e.g. `hot_waiting_time.png`, `*_workload_*.png` | **Must not be used**: they include the invalid v1 Thermal-DVFS bars, unequal DVFS across baselines and inconsistent v1 logging rules (BUGS B1, B6, B7) |

### Figures that do not exist yet (would need approval to create)

| Proposed figure | Source | Note |
|---|---|---|
| F-new-1: TA-EDF − EDF total tardiness vs migration cost (one line per workload; DVFS on) | `05_Results/v2_sensitivity/sensitivity_results.csv` | Would need a **new** plotting script writing to a **new** folder (e.g. `06_Figures/v2_sensitivity/`), plus a manifest and checks. **Not created in this phase.** |
| F-new-2: Simulator architecture / tick-order diagram | `sim_engine.py` docstring | Not a data figure; can be drawn for the paper |

---

## Comparisons that must carry limitations

| Comparison | Required limitation statement |
|---|---|
| Any policy vs any other | Single deterministic run; differences are not statistically tested |
| TA-EDF vs EDF | Zero-cost migrations in the main benchmark; reversed for responsiveness at migration cost ≥ 0.1 (T9) |
| Thermal metrics | Simulated, uncalibrated, two identical cores, no inter-core heat transfer |
| DVFS on vs off | The governor never needed 1.8 / 1.4 GHz under these parameters (BUGS B3) |
| Deadline misses | Workloads are partly infeasible; misses saturate |
| EEVDF-inspired | Not Linux EEVDF; no lag bound on 2 cores |
| RR / EEVDF "coolest" results | Achieved by interleaving at the cost of the worst waiting times and 6 / 6 misses |
