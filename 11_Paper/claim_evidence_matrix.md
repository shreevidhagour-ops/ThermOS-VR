# Claim–Evidence Matrix (ThermOS-VR paper, preparation phase 1)

Prepared 2026-10-21. Read-only analysis; no result file was modified.
All paths are relative to the project root `ThermOS-VR/`.
Every evidence file listed here is checksummed in `11_Paper/evidence_freeze_manifest_2026-10-21.sha256`.

**Abbreviations.**
- **B** = `05_Results/v2_modern_baselines/benchmark_results.csv` (64 rows, zero overhead).
- **T** = `05_Results/v2_modern_baselines/task_results.csv`.
- **S** = `05_Results/v2_sensitivity/sensitivity_results.csv` (1,024 rows).
- **README** = `03_Code/day5_modern_baselines/README.md`; **AF** = `03_Code/day5_modern_baselines/AUDIT_FIXES.md`; **BUGS** = `03_Code/day5_modern_baselines/CONFIRMED_BUGS.md`.
- "Run n" = the `Run ID` column in B.
- DVFS on = `DVFS = hysteresis`.
- Workloads: N = Normal VR, Bu = Burst VR, S = Sustained Thermal, H = HOT Thermal.

**Run-ID map for B** (same for `off` with Run − 32):

| DVFS on | FCFS | Priority | RR | ThermOS-VR | EDF-NP | EDF | TA-EDF | EEVDF-insp. |
|---|---|---|---|---|---|---|---|---|
| Normal | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 |
| Burst | 41 | 42 | 43 | 44 | 45 | 46 | 47 | 48 |
| Sustained | 49 | 50 | 51 | 52 | 53 | 54 | 55 | 56 |
| HOT | 57 | 58 | 59 | 60 | 61 | 62 | 63 | 64 |

**Status legend.** **DIRECT** = directly supported. **QUALIFIED** = supported only with the stated caveat. **UNSUPPORTED** = the evidence does not support it; do not make the claim.

---

## 1. Simulation scope and assumptions

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C1.1 | The study is a deterministic, discrete-time Python simulation, not a kernel implementation or hardware experiment. | README "Simulation outputs only" box and "Simulation model"; `03_Code/day5_modern_baselines/sim_engine.py` (module docstring: tick order); `run_metadata.json` | DIRECT | No kernel code, no device, no measured data. | "We evaluate all policies in a deterministic discrete-time Python simulator; no operating-system kernel was modified and no physical device was measured." |
| C1.2 | Four existing workloads, each with six one-shot (non-periodic) tasks. | T: 6 rows per Run ID; `03_Code/day1_basic_scheduler/workloads.py` (functions `create_vr_workload`, `create_burst_vr_workload`, `create_sustained_thermal_workload`, `create_hot_thermal_workload`) | DIRECT | Tasks are not periodic frames; workloads are hand-specified, not traces from real AR/VR applications. | "Each of the four workloads consists of six hand-specified one-shot tasks loosely modelled on AR/VR subsystems (rendering, tracking, physics, sensors, audio, background)." |
| C1.3 | One run per configuration; no randomness. | `run_metadata.json` (`runs: 64`); README "Validity notes" | DIRECT | No variance, confidence intervals or significance tests are possible. | "Because the simulator and workloads are deterministic, each configuration was executed once; we therefore report no statistical tests." |
| C1.4 | Thermal model: ΔT = (w/100)(f/2.5)² − 0.02(T − 25), start 45 °C, ambient 25 °C, an idle core produces no heat, no heat transfer between cores. | `run_metadata.json` → `thermal_parameters`; `03_Code/day2_thermal_model/thermal_model.py`; README "Simulation model" | DIRECT | Unvalidated against any real chip; units are nominal °C. | "Temperatures are outputs of a first-order lumped model with the parameters in Table X; they are not calibrated to any processor." |
| C1.5 | All 8 policies share identical workloads, thermal parameters, initial temperatures, governor setting and metric definitions. | README "Simulation model"; AF "Commands executed" (`verify_outputs.py` re-runs); `05_Results/v2_modern_baselines/metric_definitions.csv` | DIRECT | — | "All policies execute in the same engine with identical inputs and metric definitions (Table Y)." |

## 2. Identical modelled cores and one-unit ticks

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C2.1 | The two cores are labelled Performance / Efficiency but are identical in frequency levels, speed and thermal parameters. | `run_metadata.json` → `cores: "2 (labels Performance/Efficiency; physically identical)"`; `sim_engine.py:create_cores` | DIRECT | The results say nothing about real heterogeneous (big.LITTLE) cores. | "Although inherited from v1 as 'Performance' and 'Efficiency', both modelled cores are identical; the platform is effectively a symmetric dual-core." |
| C2.2 | Time advances in one-unit ticks; preemption only at tick boundaries; the tick has no defined real-time length. | README "Simulation model"; `sim_engine.py` run loop | DIRECT | Latencies cannot be converted to milliseconds. | "Time is measured in abstract ticks; we make no claim about wall-clock latencies such as motion-to-photon time." |
| C2.3 | A task that finishes partway through a tick completes at the end of that tick, and the core heats for the whole tick. | README "Partial ticks"; AF (88 of 384 task rows) | DIRECT | Small rounding bias, applied equally to every policy. | Describe in System Model; no results claim needed. |

## 3. ThermOS-VR versus FCFS

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C3.1 | Under the same governor, ThermOS-VR (v1 policy) gives identical metrics to FCFS on all four workloads. | B: Runs 33 vs 36, 41 vs 44, 49 vs 52, 57 vs 60 (and 1 vs 4 … 25 vs 28), all 16 metric columns equal; test `test_thermos_v1_equals_fcfs_with_same_dvfs` (log: `05_Results/v2_sensitivity/validation_log_2026-10-21.txt`) | DIRECT | Per-core placement differs in Normal VR, but every metric is equal; true for these workloads only. | "With an identical DVFS governor, the original ThermOS-VR core-selection score produced results identical to FCFS on every metric and workload." |
| C3.2 | ThermOS-VR's v1 thermal gains come from DVFS, not from core selection. | B Run 25 (FCFS, off) peak 71.74, HOT exposure 64 vs Run 60 (ThermOS-VR, on) peak 62.49, exposure 0; and Run 57 (FCFS, on) equals Run 60 | DIRECT | Applies to this model. | "Its thermal improvement over FCFS in v1 is fully explained by the DVFS governor that only it (and Thermal-DVFS) used in v1." |
| C3.3 | Why: the cores are identical and order is non-preemptive FCFS; the deadline term is identical across cores (bug B4). | BUGS B4, B8; README Policies table | DIRECT | — | State as explanation, citing the code analysis. |
| C3.4 | "ThermOS-VR reduces temperature compared with FCFS." | v1 `05_Results/experiment_results.csv` | **UNSUPPORTED** as a policy effect | Only true when FCFS lacks DVFS (unfair comparison, BUGS B7). | Do not claim. |

## 4. The corrected v1 Thermal-DVFS bug

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C4.1 | The v1 Thermal-DVFS scheduler could assign a running task to a second core in the same tick. | BUGS B1 (measured 4 / 2 / 3 / 2 double assignments); `03_Code/day3_thermos_scheduler/thermal_dvfs_scheduler.py:get_ready_processes` | DIRECT | — | "The v1 Thermal-DVFS baseline did not exclude running tasks from its ready set, so a task could execute on two cores simultaneously; its v1 results are invalid." |
| C4.2 | v1 Thermal-DVFS results (e.g. Sustained waiting 70.17) are invalid and are not used. | v1 CSV rows "Thermal-DVFS - *"; BUGS B1 | DIRECT | The v1 figures in `06_Figures/*.png` (root) include these rows. | "We do not report v1 Thermal-DVFS numbers; the corrected equivalent is FCFS under the DVFS governor." |
| C4.3 | Other confirmed v1 issues: DVFS never below 2.2 GHz (B2); CRITICAL unreachable (B3); inconsistent logging (B6); unequal DVFS across baselines (B7). | BUGS B2–B7; `tests/test_governor.py` | DIRECT | Fixing B2 changes nothing on the four workloads (B3). | Brief paragraph in Methodology. |

## 5. EDF and TA-EDF responsiveness

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C5.1 | At zero overhead, EDF / TA-EDF have the lowest or joint-lowest average waiting time and total tardiness in all four workloads under both DVFS settings. | B, `Average Waiting Time` and `Total Tardiness`. DVFS on: waiting EDF 2.83 / 3.00 / 41.33 / 69.50 and TA-EDF 2.83 / 3.00 / 40.83 / 69.17; tardiness EDF 2 / 17 / 210 / 368 and TA-EDF 2 / 17 / 208 / 369 (Runs 38, 46, 54, 62 and 39, 47, 55, 63) | QUALIFIED | **Ties.** Normal VR: waiting ties Priority and EDF-NP (2.83); tardiness 2 ties FCFS, Priority, ThermOS-VR and EDF-NP. Deterministic single runs. | "On these workloads, the preemptive EDF variants achieved the lowest (or tied-lowest) waiting time and total tardiness." |
| C5.2 | EDF and TA-EDF differ by at most 0.5 ticks of waiting time and 2 ticks of tardiness at zero overhead. | B Runs 38/39, 46/47, 54/55, 62/63 and 6/7 … 30/31 | DIRECT | — | "At zero overhead, TA-EDF matched EDF to within 0.5 ticks of waiting and 2 ticks of tardiness." |
| C5.3 | Round Robin is last on waiting and tardiness in every workload; EEVDF-inspired is second-last on waiting. | B (RR waiting 4.33 / 5.83 / 71.67 / 126.50, on) | DIRECT | — | As stated. |
| C5.4 | EDF-NP improves on FCFS / Priority / ThermOS-VR only in Sustained and HOT; it ties them in Burst. | B Runs 45 vs 41/42/44 (4.33 = 4.33) | DIRECT | — | As stated. |
| C5.5 | EDF implementation correctness. | `tests/test_schedulers.py` (hand-verified cases); audit: independent reference simulator, 18,024 comparisons, 0 mismatches (README "EDF") | DIRECT | The reference comparison was a read-only audit run; its script is not in the repository (it lives in session scratch), so cite it as an audit check, not as a shipped test. | "EDF and EDF-NP were cross-checked against an independently written reference simulator." |
| C5.6 | "TA-EDF improves responsiveness over EDF." | B | **UNSUPPORTED** | Differences are ±0.5 ticks and in both directions (HOT on: TA-EDF waiting lower but tardiness 369 > 368). | Do not claim. |

## 6. Migration / context-switch sensitivity

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C6.1 | EDF performs 0 migrations in every run; its tardiness varies by at most 2 ticks across the 16 cost pairs. | S (`Policy = EDF`, `Migrations` = 0); AF "Do the sensitivity results change…" | DIRECT | — | As stated. |
| C6.2 | For every migration cost ≥ 0.1 work units (96 of 96 configurations), TA-EDF has more total tardiness (+1 to +365) and a longer makespan (+2 to +121) than EDF. | S, TA-EDF minus EDF by (`DVFS`, `Workload`, `Migration Cost`, `Context Switch Cost`); AF table | DIRECT | Costs are hypothetical fractions of a tick and do not correspond to measured latencies. | "When each migration costs as little as 0.1 tick of work, TA-EDF's tardiness exceeds EDF's in every configuration tested." |
| C6.3 | TA-EDF misses 3–4 more deadlines than EDF in Burst VR at migration cost ≥ 0.25, and 1 more in HOT at 0.5 (DVFS on). | S | DIRECT | — | As stated. |
| C6.4 | Context-switch cost alone (migration cost 0) changes TA-EDF − EDF tardiness only within −4 to +5. | S rows with `Migration Cost = 0` | DIRECT | — | As stated. |
| C6.5 | TA-EDF stays 1.0–2.5 °C (simulated) below EDF's peak in Normal, Sustained and HOT at every cost; in Burst it is 0.7–3.9 °C above EDF once migrations cost anything. | S `Peak Temperature` | DIRECT | Simulated °C; one run each. | "Its lower simulated peak persists in three of four workloads, but at a responsiveness cost." |
| C6.6 | Overhead model definition (first dispatch free; migration vs resume charged once). | `03_Code/day5_modern_baselines/overhead_engine.py` docstring; `sensitivity_metadata.json` → `overhead_model`; `tests/test_overhead.py` | DIRECT | Only the incoming task is charged; no cache effects after dispatch. | Describe in Methodology. |
| C6.7 | The zero-overhead sensitivity rows reproduce the benchmark exactly. | `verify_sensitivity.py` output in the validation log (64 rows × 16 metrics) | DIRECT | — | Mention as a consistency check. |

## 7. Simulated thermal outcomes (DVFS on vs off)

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C7.1 | With DVFS on, no policy reaches HOT (≥ 70 °C) in any workload. | B `Thermal Exposure (HOT core-ticks)` = 0 for Runs 33–64 | DIRECT | Because 2.2 GHz settles at 63.7 °C (BUGS B3). | "Under the governor, simulated temperatures never reached the HOT state, so HOT exposure does not discriminate between policies." |
| C7.2 | With DVFS off, only the HOT workload reaches HOT. Exposure: RR 18 < TA-EDF 26 < EDF-NP 35 < FCFS = Priority = ThermOS-VR 64 < EDF 65 < EEVDF 104. | B Runs 25–32 | DIRECT | Single workload, single runs. | As stated, with the caveat. |
| C7.3 | With DVFS on, core-ticks ≥ 60 °C in Sustained: RR 5, TA-EDF 28, … EDF 108. In HOT: RR 49, TA-EDF 257, … EDF 286. | B Runs 49–64 `Core-ticks >= 60C` | DIRECT | RR achieves this by interleaving, at the worst responsiveness (C5.3). | Report alongside responsiveness, never alone. |
| C7.4 | With DVFS off, total heat is identical for all policies; placement cannot change total heat or average temperature in this linear model with identical cores. | B `Heat Generated (model units)`: 18.20 / 58.00 / 205.00 / 359.25 for every policy (Runs 1–32); README "What placement can and cannot change" | DIRECT | Average-temperature differences come only from timing. | "In our linear model, placement can only redistribute heat; it cannot reduce total heat." |
| C7.5 | DVFS lowers the simulated peak and lengthens execution. Example (FCFS, HOT): peak 71.74 → 62.49, makespan 205 → 226. | B Runs 25 vs 57 | DIRECT | Simulated trade-off only. | As stated. |
| C7.6 | "ThermOS-VR / TA-EDF reduces real device temperature, power or battery drain." | none | **UNSUPPORTED** | No physical measurement and no power model. | Never claim. |
| C7.7 | TA-EDF has a lower simulated peak than EDF in all four workloads at zero overhead. | B Runs 38/39 (50.59 / 48.10), 46/47 (57.58 / 57.50), 54/55 (61.28 / 60.24), 62/63 (63.33 / 62.34) | QUALIFIED | In Burst the gap is 0.08 °C; TA-EDF's Burst peak exceeds FCFS's (57.24). DVFS off: TA-EDF has *more* core-ticks ≥ 60 °C than EDF (S: 154 vs 137; H: 304 vs 299). | "At zero overhead, TA-EDF's simulated peak was below EDF's in all four workloads (by 0.08–2.49 °C), but threshold exposure did not consistently improve." |

## 8. Deadline misses and feasibility

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C8.1 | Sustained and HOT deadlines are infeasible for any policy on two cores. | T (Run 17): bursts sum to 245 → makespan ≥ 122.5, deadlines 45–60. T (Run 25): bursts sum to 405 → makespan ≥ 202.5, deadlines 75–100 | DIRECT | — | "Even an ideal two-core schedule cannot meet most deadlines in the Sustained and HOT workloads." |
| C8.2 | Burst VR is also partly infeasible: total work 63 → makespan ≥ 31.5, deadlines 10–24. | T (Run 9) | DIRECT | Some tasks can still meet their deadlines (EDF misses 2 of 6). | Include in the workload table. |
| C8.3 | In Sustained / HOT every policy misses 4 of 6 except RR and EEVDF (6 of 6). | B `Deadline Misses` | DIRECT | Miss counts saturate and cannot rank the deadline-aware policies; use total tardiness. | As stated. |
| C8.4 | Missed tasks are not dropped (soft real-time); a miss means completion > absolute deadline. | README "Deadlines"; `metric_definitions.csv` | DIRECT | — | Methodology. |

## 9. EEVDF-inspired policy limitations

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C9.1 | It models weights, virtual runtime, average vruntime V, eligibility (v ≤ V), virtual deadlines, and zero-lag placement. | `03_Code/day5_modern_baselines/policies.py` → `EEVDFInspiredPolicy`; README "EEVDF-inspired" | DIRECT | The priority→nice mapping is our assumption. | "an EEVDF-inspired weighted-fair policy" |
| C9.2 | On two cores it dispatches ineligible tasks to stay work-conserving (4 / 15 / 27 / 56 ticks); lag reached 22.6 slices (HOT). Fairness and lag bounds do not hold. | README; AF; `tests/test_schedulers.py::test_two_core_limitation_is_documented_not_bounded` (Burst: 15 dispatches, 3.55 slices) | DIRECT | The 4 / 15 / 27 / 56 and 22.6 values come from a read-only audit probe (session scratch); the Burst values are reproduced by the shipped test. | "With a single global queue on two cores, the policy loses EEVDF's lag guarantee." |
| C9.3 | It does not use deadlines or temperature. | `policies.py` | DIRECT | — | As stated. |
| C9.4 | "We evaluate Linux EEVDF." | — | **UNSUPPORTED** | Linux uses per-CPU runqueues, load balancing, sleeper/lag handling, and slices settable via `sched_setattr()` (kernel docs). | Never claim. |
| C9.5 | "EAS was evaluated." | README "EAS-inspired: not implemented" | **UNSUPPORTED** | Kernel docs: EAS "does not support platforms with symmetric CPU topologies". | State EAS was out of scope and why. |

## 10. TA-EDF idle-insertion behaviour

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C10.1 | The hold-back rule never left a core idle in the 64-run benchmark. | README "What actually happened"; AF item 1 | DIRECT | Counts (3 + 28 ticks; 31 / 9 / 1 cases; t = 32) come from read-only audit probes (session scratch), not a shipped script. | "The thermal idle-insertion mechanism never idled a core on these workloads; TA-EDF's differences from EDF therefore stem from coolest-core placement." |
| C10.2 | Its bounded delay is verified by a unit test. | `tests/test_schedulers.py::test_idle_insertion_is_bounded` | DIRECT | Synthetic one-core test, not a workload result. | Mention in Policy description. |
| C10.3 | "Idle insertion reduces temperature." | — | **UNSUPPORTED** | Never exercised. | Never claim. |
| C10.4 | TA-EDF's placement relies on migrations: 8 / 41 / 77 / 193 (DVFS on) vs 0 for EDF. | B `Migrations`, Runs 39, 47, 55, 63 | DIRECT | Free in the base benchmark. | As stated. |

## 11. Missing physical validation, energy and replication

| ID | Proposed claim | Evidence | Status | Required caveat | Recommended wording |
|---|---|---|---|---|---|
| C11.1 | No hardware temperature, power, energy, battery or latency was measured. | README box; AF "Claims the report must avoid" | DIRECT (as a limitation) | — | State explicitly in Limitations. |
| C11.2 | "Heat Generated" is a unit-less model term, not energy. | `metric_definitions.csv` | DIRECT | — | Name it "model heat units". |
| C11.3 | No statistical replication; no generalisation beyond four workloads. | `run_metadata.json`; README | DIRECT (as a limitation) | — | Threats to Validity. |
| C11.4 | Results apply to AR/VR headsets. | — | **UNSUPPORTED** | Workloads are only loosely AR/VR-inspired; there is no frame-periodic model. | Frame as motivation only. |

---

## Wording issue found in the frozen evidence (not modified)

- `metric_definitions.csv` defines **Migrations** as "Times a task resumed on a different core than it last ran on". The engine also counts a move between consecutive ticks with no gap (`sim_engine.py:_apply`; independently confirmed by `verify_sensitivity.py`, which counts core changes between consecutive busy ticks). **Use this paper definition:** "number of times a task executed on a different core from the one it last executed on."

## Evidence that is missing or only in session scratch

- **Audit-only figures (session scratch, not shipped):** the 18,024-case EDF reference comparison, the EEVDF two-core probe values (4 / 15 / 27 / 56; 22.6), and the idle-insertion case breakdown (31 / 9 / 1).
  - Either cite them as audit observations, or, before submission, add the probe scripts to the repository as a new, separately named script and re-run them read-only. Recommended; needs your approval.
- **No evidence for:** any frame-rate, motion-to-photon, energy or hardware claim; any multi-seed or statistical claim; any behaviour of real P/E cores.
