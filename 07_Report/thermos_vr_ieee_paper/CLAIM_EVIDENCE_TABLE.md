# CLAIM_EVIDENCE_TABLE: every result claim the paper may make

**Rule:** the paper may state a number only if it appears below with status **OK**. Each row names:
- the result file and the filter (or Run IDs);
- the check ID that recomputes it, either in `evidence/evidence_checks_output.txt` (prefix C / COV) or in `evidence/audit_probes_output.txt` (prefix P).

**Files**
- `B` = `05_Results/v2_modern_baselines/benchmark_results.csv`
- `T` = `.../task_results.csv`
- `S` = `05_Results/v2_sensitivity/sensitivity_results.csv`

**Run IDs in B** (DVFS on → Runs 33–64; DVFS off → Run − 32):

| | FCFS | Priority | RR | ThermOS-VR | EDF-NP | EDF | TA-EDF | EEVDF |
|---|---|---|---|---|---|---|---|---|
| Normal | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
| Burst | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 |
| Sustained | 49 | 50 | 51 | 52 | 53 | 54 | 55 | 56 |
| HOT | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |

## 1. Design and coverage

| ID | Paper statement | Evidence | Check | Status |
|---|---|---|---|---|
| D1 | 8 policies × 4 workloads × 2 DVFS settings = 64 runs, one each | B (64 rows, no duplicates) | COV-B-rows, COV-B-unique, COV-B-sets | OK |
| D2 | 6 one-shot tasks per workload (384 task records) | T | COV-T-rows | OK |
| D3 | Sensitivity: migration × context-switch cost ∈ {0, 0.1, 0.25, 0.5}², 16 pairs × 64 = 1,024 runs | S | COV-S-rows, COV-S-grid | OK |
| D4 | No missing values; 16 metrics, all defined in `metric_definitions.csv` | B, S, definitions file | COV-NaN, COV-defs | OK |
| D5 | Zero-overhead sensitivity runs reproduce the benchmark exactly (64 × 16) | S vs B | C6.7 | OK |
| D6 | Two identical modelled cores; start 45 °C; ambient 25 °C; heat (w/100)(f/2.5)²; cooling 0.02(T−25) | `run_metadata.json`; `03_Code/day2_thermal_model/thermal_model.py` | inspection | OK |
| D7 | Governor steps down at 60 / 70 / 80 °C and up at 58 / 68 / 78 °C; only 2.5 and 2.2 GHz occur on these workloads | README; `tests/test_governor.py`; BUGS B3 | 42 tests OK | OK |
| D8 | Implementation verified: 42 unit tests; independent recomputation of 1,024 metric values; 64 + 1,024 fresh re-runs; 25 / 25 figures pixel-identical to re-renders | `evidence/rerun_existing_checks_log.txt` | re-run | OK |
| D9 | EDF and EDF-NP match an independent reference simulator in 18,024 comparisons (0 mismatches) | `evidence/reproduce_audit_probes.py` | P1 | OK |

## 2. Workloads and feasibility (T1 in the paper)

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| W1 | Total work / two-core makespan lower bound / deadline range: Normal 28 / 14 / 8–20; Burst 63 / 31.5 / 10–24; Sustained 245 / 122.5 / 45–60; HOT 405 / 202.5 / 75–100 | T, Runs 1, 9, 17, 25 | C8.1/8.2 section | OK |
| W2 | Sustained and HOT deadlines cannot be met by any two-core schedule for most tasks; Burst is partly infeasible | W1 | derived | OK |
| W3 | In Sustained and HOT every policy misses 4 of 6 deadlines, except RR and EEVDF-inspired (6 of 6) | B `Deadline Misses` | C8.3 | OK |

## 3. ThermOS-VR and DVFS

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| R1 | ThermOS-VR and FCFS give identical values for all 16 metrics in all 8 (DVFS, workload) configurations | B: Runs 1/4, 9/12, 17/20, 25/28, 33/36, 41/44, 49/52, 57/60 | C3.1 (128 comparisons, 0 differ) | OK |
| R2 | FCFS (= ThermOS-VR), HOT workload: peak 71.74 → 62.49 °C, HOT core-ticks 64 → 0, makespan 205 → 226 when the governor is enabled | B Runs 25, 57 | C7.5 | OK |
| R3 | FCFS, Sustained: peak 67.61 → 61.28 °C, makespan 125 → 135 with DVFS | B Runs 17, 49 | C3.2 section | OK |
| R4 | Normal and Burst never reach 60 °C, so DVFS does not change them | B Runs 1/33, 9/41 | C3.2 section | OK |
| R5 | "ThermOS-VR's score reduces temperature compared with FCFS" | — | — | **NOT ALLOWED** (contradicted by R1) |

## 4. Responsiveness (DVFS on unless stated)

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| P1r | An EDF variant (EDF or TA-EDF) attains the minimum average waiting time and total tardiness in all 16 (DVFS × workload × metric) cases | B | C5.1 | OK |
| P2r | **Ties.** Normal: waiting 2.83 is shared by Priority, EDF-NP, EDF and TA-EDF; tardiness 2 by every policy except RR (5) and EEVDF (3). Sole minima: DVFS on, Sustained waiting and tardiness (TA-EDF 40.83 / 208); HOT waiting (TA-EDF 69.17); HOT tardiness (EDF 368). DVFS off, HOT waiting (EDF 64.17). | B | C5.1 listing | OK |
| P3r | EDF vs TA-EDF at zero overhead: at most 0.5 ticks of waiting and 2 ticks of tardiness apart | B | C5.2 | OK |
| P4r | Waiting, DVFS on (Normal / Burst / Sustained / HOT): EDF 2.83 / 3.00 / 41.33 / 69.50; TA-EDF 2.83 / 3.00 / 40.83 / 69.17; FCFS 3.50 / 4.33 / 48.83 / 80.67; RR 4.33 / 5.83 / 71.67 / 126.50; EEVDF 3.83 / 4.83 / 56.50 / 101.50 | B Runs 33–64 | values in B | OK |
| P5r | Tardiness, DVFS on: EDF 2 / 17 / 210 / 368; TA-EDF 2 / 17 / 208 / 369; FCFS 2 / 23 / 253 / 431; RR 5 / 30 / 378 / 697 | B | values in B | OK |
| P6r | RR is last on waiting and tardiness, and EEVDF-inspired second-last on waiting, in every configuration | B | C5.3 | OK |
| P7r | EDF-NP improves on FCFS / Priority / ThermOS-VR only in Sustained and HOT; it ties them in Burst (4.33) | B Runs 41–45 | values in B | OK |
| P8r | "TA-EDF improves responsiveness over EDF" | — | — | **NOT ALLOWED** (P3r: differences of ≤ 0.5 ticks, in both directions) |

## 5. Simulated thermal outcomes

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| T1t | With DVFS on, no policy reaches the HOT state (≥ 70 °C) in any workload | B Runs 33–64 | C7.1 | OK |
| T2t | DVFS off, HOT workload, HOT core-ticks: RR 18, TA-EDF 26, EDF-NP 35, FCFS = Priority = ThermOS-VR 64, EDF 65, EEVDF 104; zero in the other three workloads | B Runs 25–32 | C7.2a | OK |
| T3t | DVFS on, core-ticks ≥ 60 °C, Sustained: RR 5, TA-EDF 28, EEVDF 77, EDF-NP 90, Priority 102, FCFS = ThermOS-VR 107, EDF 108. HOT: RR 49, TA-EDF 257, EDF-NP 269, FCFS = Priority = ThermOS-VR 281, EEVDF 282, EDF 286 | B | C7.3 section | OK |
| T4t | With DVFS off, total model heat is identical across policies (18.20 / 58.00 / 205.00 / 359.25 model units) | B Runs 1–32 | C7.4 | OK |
| T5t | At zero overhead, TA-EDF's simulated peak is below EDF's in all 8 configurations, by 0.08–2.49 °C (smallest gap Burst 0.08; DVFS on: Normal 2.49, Sustained 1.04, HOT 0.99) | B | C7.7 | OK |
| T6t | DVFS off: TA-EDF has **more** core-ticks ≥ 60 °C than EDF (Sustained 154 vs 137; HOT 304 vs 299) | B Runs 22/23, 30/31 | values in B | OK |
| T7t | DVFS on, HOT: TA-EDF spends more busy core-ticks below 2.5 GHz than EDF (321 vs 294) | B Runs 62/63 `Throttled Busy Core-ticks` | values in B | OK |
| T8t | Any real temperature, power, energy or battery claim | — | — | **NOT ALLOWED** |

## 6. TA-EDF mechanism

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| M1 | TA-EDF migrations at zero overhead: 8 / 41 / 77 / 193 (DVFS on), 8 / 41 / 64 / 114 (off); EDF 0 everywhere | B `Migrations` | C10.4 section | OK |
| M2 | The thermal hold-back rule never left a core idle in any of the 64 runs | probe | P3 (0 idle core-ticks) | OK |
| M3 | Per DVFS setting: 31 ticks with a core ≥ 59 °C and a task with slack ≥ 10. Outcomes: placed on a cooler core 31 times; cores already filled 9 times; skipped once (HOT, t = 32), with the core immediately given to the next EDF candidate | probe | P3 | OK |

## 7. Overhead sensitivity

Matched on DVFS, workload, migration cost and context-switch cost.

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| O1 | EDF makes 0 migrations in all 128 of its sensitivity runs; its tardiness changes by at most 2 ticks across the cost grid | S | C6.1 | OK |
| O2 | For migration cost ≥ 0.1 (96 matched configurations), TA-EDF has higher total tardiness (+1 to +365 ticks) and longer makespan (+2 to +121 ticks) than EDF in all 96 | S | C6.2 | OK |
| O3 | TA-EDF misses 3–4 more deadlines than EDF in Burst at migration cost ≥ 0.25, and 1 more in HOT at 0.5 (DVFS on) | S | C6.3 | OK |
| O4 | With migration cost 0, varying only the context-switch cost changes TA-EDF − EDF tardiness only within −4 to +5 ticks | S | C6.4 | OK |
| O5 | In Normal, Sustained and HOT, TA-EDF's simulated peak stays **0.99–2.49 °C** below EDF's at every cost; in Burst it is 0.70–3.93 °C *above* EDF once migration cost > 0 | S | **C6.5-exact** (the "1.0–2.5" wording fails, see `OPEN_ISSUES.md`) | OK (exact wording only) |
| O6 | Table: TA-EDF − EDF tardiness, DVFS on, context-switch cost 0, at migration cost 0 / 0.1 / 0.25 / 0.5. Normal 0 / 1 / 2 / 4; Burst 0 / 8 / 24 / 71; Sustained −2 / 13 / 39 / 159; HOT 1 / 37 / 113 / 365 | S | C6 table section | OK |
| O7 | The same table for peak temperature (°C): Normal −2.49 / −2.09 / −2.09 / −2.02; Burst −0.08 / +1.05 / +2.22 / +2.97; Sustained −1.04 / −1.08 / −1.09 / −1.18; HOT −0.99 / −1.06 / −1.10 / −1.11 | S | C6 table section | OK |
| O8 | Overhead costs correspond to real migration or context-switch latencies | — | — | **NOT ALLOWED** |

## 8. EEVDF-inspired policy

| ID | Statement | Evidence | Check | Status |
|---|---|---|---|---|
| E1 | On one core it never dispatches an ineligible task; maximum lag 0.73–0.94 slices across the four workloads | probe | P2 | OK |
| E2 | On two cores it dispatches ineligible tasks in 4 / 15 / 27 / 56 ticks (Normal / Burst / Sustained / HOT, DVFS on); maximum lag 2.26 / 3.55 / 7.67 / 22.59 slices | probe; Burst also reproduced by the shipped test | P2; `test_two_core_limitation_is_documented_not_bounded` | OK |
| E3 | Linux-equivalent EEVDF behaviour or fairness guarantees | — | — | **NOT ALLOWED** |

## 9. Statements that are never allowed

- Statistical significance, confidence intervals or generalisation beyond the four workloads.
- Hardware validation; measured temperature, power, energy, battery or latency.
- That EAS was implemented or evaluated.
- That idle insertion contributed to any result.
- Using v1 Thermal-DVFS numbers or v1 figures as a baseline.
