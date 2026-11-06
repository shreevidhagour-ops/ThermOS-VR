# Audit fixes (2026-10-21)

Corrections applied after the research-quality audit of `day5_modern_baselines/`.
The full validation output is in `05_Results/v2_sensitivity/validation_log_2026-10-21.txt`.

## What was preserved

- **v1:** source, `05_Results/experiment_results.csv`, v1 figures and `10_Backups/v1_original_2026-10-21/` were not modified. All 49 files match their checksums.
- **The 64-run v2 benchmark** (`05_Results/v2_modern_baselines/`, 6 files) and **its figures** (`06_Figures/v2_modern_baselines/`, 25 PNGs + manifest) were neither regenerated nor modified. All 32 files match the checksums taken before any fix (`10_Backups/v2_pre_audit_fixes_2026-10-21/SHA256_v2_outputs_before_fixes.txt`).
- **The simulation sources were not edited:** `sim_engine.py`, `policies.py`, `metrics_v2.py`. They still match the hashes recorded in the benchmark's `run_metadata.json`.
- **`run_benchmark.py` was edited** (overwrite guard, version metadata), so it no longer matches its recorded hash. The exact version that produced the benchmark is in `10_Backups/v2_pre_audit_fixes_2026-10-21/day5_modern_baselines/`. A fresh re-run with the current version reproduces all 64 rows exactly (`verify_outputs.py`).

## Files changed and why

| File | Status | Why |
|---|---|---|
| `overhead_engine.py` | new | `OverheadSimulator` subclass with migration / context-switch charges. Keeps `sim_engine.py` untouched |
| `run_sensitivity.py` | new | 1,024-run overhead sensitivity experiment; writes only to `05_Results/v2_sensitivity/` |
| `verify_sensitivity.py` | new | Independent checks of the sensitivity outputs |
| `output_guard.py` | new | `--overwrite` protection and Python / pandas / matplotlib / numpy version metadata |
| `run_benchmark.py` | modified | Refuses to write into a non-empty output folder without `--overwrite`; records library versions. Simulation code unchanged |
| `plot_results.py` | modified | Same guard. Figures are now built by functions that return the figure, so the verifier can re-render them. Corrected the "768 bars" message (temperature metrics are points). Drawing code unchanged: all 25 saved PNGs are pixel-identical to fresh renders |
| `verify_outputs.py` | modified | Replaced the always-passing "executed work ≥ burst" check with a partial-tick-aware check. Added a pixel comparison of all 25 PNGs, a check of the trace-figure line data against `tick_trace.csv`, and a v2-baseline checksum check |
| `tests/test_schedulers.py` | modified | Renamed `test_lag_stays_bounded` → `test_one_core_equal_weight_vruntime_spread_within_one_slice` (it is a one-core property). Added a two-core EEVDF test that documents the limitation without asserting a bound |
| `tests/test_overhead.py` | new | Hand-verified overhead charging, plus zero-cost equivalence with the unmodified engine (64 configurations) |
| `tests/test_output_guard.py` | new | Guard behaviour, using temporary folders only |
| `README.md` | modified | Corrections listed below |
| `AUDIT_FIXES.md` | new | This file |

### README corrections

1. **Idle insertion.** The old text gave the wrong reason ("no waiting task has 10 ticks of slack"). What actually happened:
   - A core at or above 59 °C coexisted with a task that had slack ≥ 10 in 3 ticks (Sustained) and 28 ticks (HOT).
   - In 31 cases the task was placed on the other core, which was still below 59 °C.
   - In 9 cases the earlier-deadline tasks had already filled both cores.
   - In 1 case per DVFS setting (HOT, t = 32) the task was skipped, but the next EDF candidate took the core immediately.
   - So **no core-tick was ever idled.**
2. **EEVDF on two cores.** The policy dispatches ineligible tasks to stay work-conserving (4 / 15 / 27 / 56 ticks; largest lag 22.6 slices in HOT). Fairness and lag bounds are not guaranteed with two cores. On one core it behaves as EEVDF should (lag below 1 slice).
3. **Linear model.** With identical cores and DVFS off, placement cannot change total heat or average temperature. It can only redistribute heat, which affects peak temperature and threshold counts.
4. **Simulation outputs vs hardware.** An explicit statement that no value is a measured temperature, power or energy.
5. **`Executed Work`** is defined as the capacity of the busy ticks, including the unused part of a task's final tick. It is not the useful work done.
6. **Safe commands:** `python -B`, `--overwrite`, and the new scripts.

## Commands executed and actual results

All commands were run from `03_Code/day5_modern_baselines/`.

| Command | Result |
|---|---|
| `python -B -m unittest discover -s tests -v` | **42 tests, OK** |
| `python -B verify_outputs.py` | **ALL CHECKS PASSED.** 64 runs; 1,024 metric values recomputed; 64 fresh re-runs; 768 plotted values; **25 of 25 PNGs pixel-identical** to re-render; 1,798 trace-figure points equal the raw trace; 384 task rows pass the work check (88 finish partway through their final tick, unused capacity total 44.44, max 0.96); 49 v1 files and 32 v2-baseline files unchanged |
| `python -B run_sensitivity.py` | 1,024 runs written (about 7 s) |
| `python -B verify_sensitivity.py` | **ALL SENSITIVITY CHECKS PASSED.** Full 16 × 64 grid, no duplicates; zero-overhead rows equal the benchmark on 64 rows × 16 metrics; 6,144 task rows recomputed from the trace (waiting, busy ticks, start, completion, migrations, resumes, preemptions, overhead, unused capacity); 1,024 fresh re-runs; 81 protected files unchanged |
| `python -B run_benchmark.py` (no flag) | Refused, exit 2, nothing changed |
| `python -B plot_results.py` (no flag) | Refused, exit 2, nothing changed |
| `python -B run_sensitivity.py` (no flag, after it had run) | Refused, exit 2, nothing changed |
| `sha256sum -c` on both manifests | 49 / 49 and 32 / 32 OK |
| Newest `.pyc` in the v1 `__pycache__` folders | 2026-09-16, so nothing was written there |

**Failures during this work (all fixed, then re-run):**
- One new test failed on its first run: `test_allows_new_or_desktop_ini_only_directory`. **The test was wrong**, not the guard: it reused a folder in which it had just created a subfolder.
- The first `verify_outputs.py` run printed a matplotlib "more than 20 figures open" warning. It was silenced with an rcParam that does not affect rendering; the pixel identity was confirmed afterwards.

**Remaining failures:** none.

**Environment:** Python 3.14.0, pandas 3.0.5, matplotlib 3.10.7, numpy 2.3.4, Windows 11 (recorded in `sensitivity_metadata.json`). The original benchmark's `run_metadata.json` predates the version recording. It was produced in the same environment during this project, but that file does not record it.

## New output paths

`05_Results/v2_sensitivity/`:
- `sensitivity_results.csv`: 1,024 rows. Each row holds the two costs, the policy, the DVFS setting and the workload; the 16 benchmark metrics (including waiting time, makespan, deadline misses, total tardiness, peak temperature, HOT exposure, migrations and preemptions); and the migration events charged, resume events charged and total overhead work.
- `sensitivity_task_results.csv`: 6,144 task rows.
- `sensitivity_tick_trace.csv.gz`: per-core, per-tick trace.
- `sensitivity_metadata.json`: costs, overhead model, source hashes, versions.
- `validation_log_2026-10-21.txt`: full output of the validation commands.

## Overhead model (summary; full definition in README / `overhead_engine.py`)

| Event | Condition | Charge |
|---|---|---|
| first dispatch | task has never run | none |
| migration | task last ran on a different core (with or without a gap) | `migration_cost` |
| resume | task last ran on the same core, but not in the previous tick | `context_switch_cost` |

- A migration is never also charged as a context switch (tested).
- The charge is extra work at dispatch: the core is busy and heating while it is spent.
- Costs are hypothetical fractions of a tick; the tick has no real-time length.

## Do the sensitivity results change the interpretation of TA-EDF?

**Yes.** TA-EDF's benchmark parity with EDF on responsiveness exists only when migrations are free.

TA-EDF minus EDF, DVFS on, context-switch cost 0 (negative = TA-EDF lower). For reference, EDF's tardiness is 2 / 17 / 210 / 368.

| Migration cost | Tardiness (Normal / Burst / Sustained / HOT) | Peak °C (N / B / S / H) | Core-ticks ≥ 60 °C (S / H) |
|---|---|---|---|
| 0 | 0 / 0 / −2 / +1 | −2.49 / −0.08 / −1.04 / −0.99 | −80 / −29 |
| 0.1 | +1 / +8 / +13 / +37 | −2.09 / +1.05 / −1.08 / −1.06 | −83 / −20 |
| 0.25 | +2 / +24 / +39 / +113 | −2.09 / +2.22 / −1.09 / −1.10 | −80 / +7 |
| 0.5 | +4 / +71 / +159 / +365 | −2.02 / +2.97 / −1.18 / −1.11 | −86 / +94 |

Checked over the **whole** grid (all 16 cost pairs, both DVFS settings):

- **EDF makes 0 migrations**, so its results move by at most 2 tardiness ticks across the grid.
- **Responsiveness:** for every migration cost ≥ 0.1 (96 of 96 configurations), TA-EDF has **more total tardiness** (+1 to +365) and a **longer makespan** (+2 to +121) than EDF.
- **Deadline misses:** TA-EDF misses 3–4 more in Burst VR at migration cost ≥ 0.25, and 1 more in HOT at 0.5 with DVFS on.
- **Context-switch cost alone** (migration cost 0) changes TA-EDF − EDF tardiness only within −4 to +5.
- **Peak temperature:** TA-EDF stays 1.0–2.5 °C below EDF in Normal, Sustained and HOT at every cost. In Burst VR it is 0.7–3.9 °C *above* EDF whenever migrations cost anything.
- **Threshold counts:**
  - With DVFS on, Sustained core-ticks ≥ 60 °C stay lower (−80 to −87) at every cost. In HOT the reduction (−20 to −29) turns into an increase at 0.25 and above.
  - With DVFS off, HOT exposure (≥ 70 °C) stays about 40 core-ticks lower at every cost. But core-ticks ≥ 60 °C are *higher* than EDF throughout.

**Interpretation:** TA-EDF's coolest-core placement buys a modest reduction in simulated peak temperature at the cost of migrations. Once migrations cost anything, it trades responsiveness for that reduction. It is a trade-off, not a free improvement.

## Claims the report can safely make

1. ThermOS-VR v2 is a deterministic Python simulation of a two-core platform with identical modeled cores, evaluated on four existing workloads of six one-shot tasks each, with one-unit time steps.
2. With the same DVFS governor, ThermOS-VR v1 produces exactly the same results as FCFS on every metric and workload. Its v1 thermal improvements come from DVFS, not from its core-selection score.
3. The v1 Thermal-DVFS baseline was invalid (one task could run on two cores at once); it was corrected and re-run.
4. At zero overhead, the preemptive EDF variants (EDF and TA-EDF) have the lowest or joint-lowest average waiting time and total tardiness on all four workloads, under both DVFS settings. The ties:
   - **Normal VR:** waiting ties with Priority and EDF-NP; tardiness (2) ties with FCFS, Priority, ThermOS-VR and EDF-NP.
   - **Best of the two:** EDF and TA-EDF are within 0.5 ticks of waiting and 2 of tardiness of each other.

   EDF-NP is strictly better than FCFS, Priority and ThermOS-VR only in Sustained and HOT; in Burst VR it ties them. Round Robin is last on both metrics in every workload.
5. With free migrations, TA-EDF matches EDF's responsiveness (within ±0.5 ticks of waiting and ±2 of tardiness) and has a lower simulated peak temperature in all four workloads.
6. With a migration cost of 0.1 work units or more, TA-EDF has more tardiness and a longer makespan than EDF in every tested configuration. It still has a 1–2.5 °C lower simulated peak in three of the four workloads.
7. With DVFS on, Round Robin has the lowest simulated average temperature in Sustained and HOT, the lowest peak in HOT, and the fewest core-ticks ≥ 60 °C in both. It gets these by interleaving light and heavy tasks. Round Robin and the EEVDF-inspired policy have the worst and second-worst waiting times in every workload, and both miss 6 of 6 deadlines in Sustained and HOT.
8. Each of these statements is about a deterministic model with one run per configuration.

## Claims the report must avoid

- Any **statistical significance**, confidence or generalisation beyond these four workloads (single deterministic runs, n = 6 tasks).
- Any **real** temperature, power, energy, battery or headset result, or that the simulator models real P/E cores.
- That TA-EDF "reduces heat without cost", or that its **idle-insertion** mechanism contributed: it never idled a core.
- That the EEVDF-inspired policy is **Linux EEVDF**, or that it is fair or lag-bounded on two cores.
- That **EAS** was evaluated, or that any energy result exists.
- That placement reduced **average temperature or total heat** with DVFS off (impossible in this model).
- That the migration / context-switch costs correspond to **real latencies**.
- Citing **v1 Thermal-DVFS** numbers or v1 figures as valid baselines.
- That deadline-miss counts separate the policies in Sustained / HOT: every policy misses 4–6 of 6 because those deadlines are infeasible.
