# ThermOS-VR v2: modern scheduling baselines

This folder adds EDF, Thermal-aware EDF and an EEVDF-inspired policy to the
ThermOS-VR **simulation**. Every policy runs in one shared engine with the same
inputs and metric definitions.

> **Simulation outputs only.** Every temperature, frequency, heat value and
> "throttling" count reported here is the output of a simplified discrete-time
> Python model. **None of them is a measured CPU, SoC or headset temperature,
> and the model has no notion of power, voltage or energy.** "Heat Generated" is
> the model's unit-less heat term `(w/100)(f/2.5)²`, not joules. The two cores
> are identical model cores, not real Performance and Efficiency cores.

The v1 code (`day1`–`day4`), `05_Results/experiment_results.csv` and the v1
figures are **unchanged** (verified by SHA-256). The backups are:
- `10_Backups/v1_original_2026-10-21/`: the v1 project.
- `10_Backups/v2_pre_audit_fixes_2026-10-21/`: the day5 sources as they were when the 64-run benchmark was produced, plus checksums of its outputs.

The v1 bugs found during inspection are in [CONFIRMED_BUGS.md](CONFIRMED_BUGS.md).
The audit corrections are in [AUDIT_FIXES.md](AUDIT_FIXES.md).

## How to run (safe commands)

Run these from `03_Code/day5_modern_baselines/`. Use `python -B` so that Python
does not write `__pycache__` files into the v1 folders it imports from.

```
python -B -m unittest discover -s tests -v   # unit, equivalence, overhead and guard tests
python -B verify_outputs.py                  # read-only checks of the 64-run benchmark + figures
python -B verify_sensitivity.py              # read-only checks of the overhead experiment
```

The output-producing scripts **refuse to write into a non-empty output
folder** (exit code 2, nothing changed) unless `--overwrite` is given:

```
python -B run_benchmark.py   [--overwrite]   # 64 runs   -> 05_Results/v2_modern_baselines/
python -B plot_results.py    [--overwrite]   # 25 PNGs   -> 06_Figures/v2_modern_baselines/
python -B run_sensitivity.py [--overwrite]   # 1024 runs -> 05_Results/v2_sensitivity/
```

None of these scripts writes to the v1 folders, the v1 results or `10_Backups/`.

## Files

| File | Purpose |
|---|---|
| `sim_engine.py` | Shared time loop, DVFS governors, two-core platform (reuses v1 `Process`, `Core`, `ThermalModel` unchanged) |
| `policies.py` | All 8 policies |
| `metrics_v2.py` | Metric definitions (one definition for every policy) |
| `overhead_engine.py` | `OverheadSimulator`: subclass that adds migration / context-switch costs (sensitivity only; the base engine is unchanged) |
| `output_guard.py` | `--overwrite` protection and environment-version metadata |
| `run_benchmark.py` | 64-run benchmark (zero overhead) |
| `plot_results.py` | 25 figures from the benchmark CSV, plus `figure_manifest.csv` |
| `run_sensitivity.py` | 1024-run overhead sensitivity experiment |
| `verify_outputs.py` | Benchmark checks: metrics recomputed from raw traces, fresh re-runs, partial-tick work accounting, every PNG pixel-compared with a fresh render, trace-figure line data vs `tick_trace.csv`, v1 and v2-baseline checksums |
| `verify_sensitivity.py` | Sensitivity checks: grid completeness, zero-overhead rows equal the benchmark, events and overhead recomputed from the trace, fresh re-runs, checksums |
| `tests/` | Hand-verified unit tests, governor tests, v1-equivalence tests, overhead tests, guard tests |

## Simulation model (shared by every policy)

- **Platform:** 2 cores, labelled Performance / Efficiency as in v1. **They are physically identical:** same frequencies, speed and thermal parameters. There is no heat transfer between cores.
- **Tick order:** dispatch → execute (`frequency / 2.5` work units) → thermal update → DVFS → `t += 1` → completions → log.
- **Thermal model:** v1 parameters: ambient 25 °C, start 45 °C, heat `(w/100)(f/2.5)²` per busy tick, cooling `0.02(T−25)`. An idle core generates no heat.
- **Preemption:** only at tick boundaries. In the 64-run benchmark, migrations and context switches cost nothing; their effect is studied separately below.
- **Deadlines:** absolute. A miss means `completion > deadline`. Late tasks are **not dropped**; they run to completion (soft real-time), so every task has a turnaround.
- **Arrivals:** a task can be dispatched at the tick equal to its arrival time.
- **Partial ticks:** a task whose remaining work is smaller than one tick's capacity (for example 0.12 units left at 2.2 GHz, where a tick holds 0.88) finishes at the *end* of that tick. The core is counted busy, and generates heat, for the whole tick. The same rule applies to every policy.

### What placement can and cannot change (linear model, identical cores)

The thermal update is linear in temperature, and both cores have identical parameters. Therefore:

- **With DVFS off (fixed 2.5 GHz)**, the total heat generated is fixed by the workload: every policy gives exactly the same "Heat Generated" (verified to 4 decimal places).
- **Which core runs a task does not change total heat or average temperature.** Average temperature differs between policies only through *when* work runs (task order and timing), not *where* it runs.
- **Placement can redistribute heat between cores.** That changes the *peak* temperature and threshold-based counts (core-ticks ≥ 60 °C, HOT exposure), which are non-linear in temperature.
- **With DVFS on**, total heat can also change, because each policy produces a different mix of 2.5 and 2.2 GHz ticks.

### DVFS settings (every policy runs under both)

- `off`: fixed 2.5 GHz.
- `hysteresis`: the corrected four-level governor. It steps down one level at 60 / 70 / 80 °C and up at 58 / 68 / 78 °C, at most one step per tick.

**Verified reachability (bug B3):** with the v1 thermal parameters, only 2.5 and 2.2 GHz ever occur. At 2.2 GHz the core settles at 63.7 °C, below the 70 °C step-down point, so the multi-level fix changes nothing on the four workloads (tested). With a stress parameter set (`heat_coefficient = 2.5`), the corrected governor reaches all four levels and holds the core near 80 °C, while the v1 logic overheats past 80 °C (tested).

## Policies

| Policy | Order | Preemptive | Core selection | Uses deadline | Uses temperature |
|---|---|---|---|---|---|
| FCFS | (arrival, PID) | no | lowest idle ID | no | no |
| Priority | (priority, arrival, PID) | no | lowest idle ID | no | no |
| Round Robin | FIFO queue, quantum 1 | yes | lowest idle ID | no | no |
| ThermOS-VR (v1, faithful port) | (arrival, PID) | no | v1 score: thermal + core type + deadline | in score only (no effect, B4) | yes |
| EDF-NP | (deadline, arrival, PID) | no | lowest idle ID | yes | no |
| EDF (global, preemptive) | (deadline, arrival, PID) | yes | keep current core, else lowest free ID | yes | no |
| TA-EDF (ours) | (deadline, arrival, PID) | yes | urgent: fastest core; otherwise: coolest core | yes | yes |
| EEVDF-inspired | eligible first, then (virtual deadline, arrival, PID) | yes | keep current core, else lowest free ID | no | no |

"Thermal-DVFS" from v1 is FCFS run under the `hysteresis` setting. It is not a
separate policy here; bug B1 is fixed by the engine. **The v1 Thermal-DVFS rows
in `05_Results/experiment_results.csv` and the v1 figures are invalid** and
must not be cited as a baseline.

### EDF (global, preemptive)

At every tick boundary, the m = 2 tasks with the earliest absolute deadlines
among running and ready tasks are selected.

- **Ties:** earlier arrival, then lower PID.
- **Selected tasks:** a selected task that is already running keeps its core. A newly selected task takes the lowest free core ID, so EDF is thermally blind.
- **Preemption:** a running task that is no longer among the top m is preempted.
- **Late tasks:** keep their original deadline and therefore keep high priority. This is standard EDF; under overload it can cause a chain of misses.

EDF-NP uses the same order, but a dispatched task runs to completion. Both were
checked against an independently written reference simulator: 4 workloads plus
3,000 random task sets, on 1–3 cores, with 0 mismatches in completion time,
waiting time or miss flag.

### Thermal-aware EDF (TA-EDF): our own policy, not an established scheduler

Task order is the same as EDF. Define `slack = deadline − t − remaining_work`.
The parameters (2, 59 °C, 10) were fixed before any benchmark run and were not tuned.

1. **Deadline-aware core choice.**
   - An *urgent* task (`slack ≤ 2`) takes the core with the highest current frequency, then the coolest.
   - Any other task takes the **coolest** core, then the highest frequency.
   - Remaining ties go to the task's current core, then the lowest ID.
   - With DVFS off, both cores always have the same frequency, so both rules reduce to "coolest core".
2. **Thermal idle insertion (hold-back rule).**
   - Candidates are considered in EDF order while free cores remain.
   - If the core chosen for a candidate is at or above 59 °C and the candidate has `slack ≥ 10`, that candidate is skipped for this tick and the next candidate is considered.
   - A core is therefore left idle only if **every** remaining candidate is skipped. The delay is bounded: slack falls by 1 per waiting tick (unit-tested).

**What actually happened in the 64-run benchmark.**
- No core-tick was ever left idle by the hold-back rule.
- A core at or above 59 °C coexisted with a task that had `slack ≥ 10` in 3 ticks (Sustained) and 28 ticks (HOT), in both DVFS settings. The rule nevertheless did not idle a core, because of how dispatch works:
  - In 31 cases, the coolest free core, the one the slack-rich task was offered, was still **below** 59 °C, so the task was placed normally.
  - In 9 cases (HOT), the earlier-deadline candidates had **already filled both cores** before the slack-rich task was considered.
  - In exactly 1 case per DVFS setting (HOT, t = 32, *Extreme Rendering*, slack 10.0, core 2 at 59.14 °C), the task **was** skipped. The next EDF candidate took the core immediately, so the core did not idle; the only effect was a one-tick reordering.
- Idle insertion needs a moment when every free core is at least 59 °C and no remaining candidate is urgent. These workloads do not produce one, because once the cores are warm most tasks have little or negative slack.
- **Consequently, the TA-EDF vs EDF differences in the benchmark come from coolest-core placement, which works through migrations (up to 193 per run).** The idle-insertion mechanism is untested by the benchmark.

**How it differs:**
- **From EDF:** the same task order, but placement is temperature- and frequency-aware, and the policy may skip a slack-rich task when its best core is hot.
- **From ThermOS-VR v1:**
  - Task order is by deadline instead of arrival.
  - It preempts.
  - The urgency term changes *which core* a task gets. In v1 the deadline score is identical for every core.
  - It can withhold work for thermal reasons.

### EEVDF-inspired: simplified, not the Linux implementation

This is an *EEVDF-inspired weighted-fair policy*. It is **not** a faithful
implementation of Linux EEVDF.

**Modeled concepts (after the EEVDF algorithm of Stoica & Abdel-Wahab, and Linux ≥ 6.6):**
- Weights from priority via the kernel's nice-to-weight table. The mapping priority 1–5 → nice −10, −5, 0, 5, 10 (weights 9548, 3121, 1024, 335, 110) is **our assumption**.
- Virtual runtime advanced by `1024 / w` per tick of execution (wall-clock ticks, not frequency-scaled).
- `V` = weighted average virtual runtime of the runnable tasks. Total lag Σw(V−v) stays at 0 to within floating-point error.
- Eligibility `v ≤ V` (lag ≥ 0).
- Virtual deadline `vd = v + slice · 1024 / w`, renewed when a slice is used.
- The eligible task with the earliest `vd` is picked.
- New tasks are placed at zero lag.

**Simplifications:**
- One global runqueue shared by both cores (Linux has per-CPU runqueues plus load balancing).
- Slice = 1 tick, so tasks are re-picked every tick.
- No sleep/wakeup, so no lag handling on wakeup and no wakeup preemption.
- **Real task deadlines and temperatures are not used** (it is a fairness scheduler).
- **It stays work-conserving by dispatching ineligible tasks.** If fewer tasks are eligible than there are cores, the remaining core runs the earliest-`vd` *ineligible* task. An eligible task is never left waiting while an ineligible one runs (tested).

**Consequence for fairness:**
- **On one core**, the model behaves as EEVDF should. No ineligible task is ever dispatched, and lag stays under 1 slice on all four workloads.
- **On two cores, fairness and lag bounds are NOT guaranteed.** Ineligible tasks were dispatched in 4 / 15 / 27 / 56 ticks (Normal / Burst / Sustained / HOT, DVFS on), and the largest lag reached 22.6 slices in HOT.
- This is inherent to a global queue with weight ratios up to 87:1: a heavy task's fair share can exceed one whole core.
- A two-core test records this limitation without asserting a bound.

### EAS-inspired: not implemented

Linux Energy-Aware Scheduling is enabled only on platforms with asymmetric CPU
capacity and an energy model (per-CPU power at each frequency). The model has
neither: its two cores are identical and it has no power or energy model. Every
placement would therefore have the same estimated energy, and an EAS-style
policy would reduce to an arbitrary choice.

Making it meaningful would require new core capacities and a power table. That
would change the platform under the four existing workloads, so the results
would no longer be comparable with v1. It is left as a separate future
experiment on an explicitly asymmetric platform.

## Metrics

Every metric uses the same definition for every policy. The definitions are
exported in `05_Results/v2_modern_baselines/metric_definitions.csv`.
Temperature samples are the post-tick values for ticks 1 through makespan (the
t = 0 initial state is not a sample).

- **Waiting time:** counts every tick a task has arrived, is unfinished and is not running, including time after a preemption.
- **Core-time utilization:** busy core-ticks / (2 × makespan).
- **Thermal exposure:** core-ticks in HOT/CRITICAL (≥ 70 °C).
- **Core-ticks ≥ 60 °C:** reported because, with DVFS on, no policy ever reaches HOT.

### Task-level columns (`task_results.csv`)

- **Executed Work:** the *capacity* of all busy ticks, i.e. the sum of `f/2.5` over every tick the task occupied a core. It **includes the unused part of the final tick** when a task finishes partway through a throttled tick, so it is **not** the useful work done.
- **Useful work** always equals `Burst` in the benchmark, and `Burst + Overhead Work` in the sensitivity experiment.
- The unused final-tick capacity is `Executed Work − Burst` (minus overhead). It lies in `[0, capacity of the final tick)`. 88 of 384 benchmark task rows have some unused capacity (at most 0.96 units, total 44.4). This is checked in `verify_outputs.py`.
- **Busy Ticks:** ticks during which the task occupied a core.

## Overhead sensitivity experiment (`run_sensitivity.py`)

**Grid:** migration cost × context-switch cost ∈ {0, 0.1, 0.25, 0.5} simulated
work units (1.0 = one tick of work at 2.5 GHz). That is 16 cost pairs × 8 policies × 4 workloads × 2 DVFS settings = 1,024 runs.

**How overhead is charged** (`overhead_engine.py`): a *dispatch event* happens when a task runs in tick t but did not run on the same core in tick t−1. Each event is classified once:

| Event | Condition | Charge |
|---|---|---|
| first dispatch | task has never run | none |
| migration | task last ran on a different core (with or without a gap) | `migration_cost` |
| resume | task last ran on this core, but not in the previous tick | `context_switch_cost` |

- A migration is **never also charged as a context switch**.
- A task that keeps running on the same core is never charged.
- The charge is added to the task's remaining work, so the core spends that capacity busy, heating at the task's intensity, before the task progresses.
- With both costs at 0, `OverheadSimulator` produces traces and metrics identical to the unmodified engine. This is tested for all 64 configurations and re-checked against the benchmark CSV in `verify_sensitivity.py`.

**Limitations of the overhead model:**
- Costs are hypothetical fractions of a tick. The simulator has no real time scale, so they **do not correspond to measured migration or context-switch latencies**.
- Only the incoming task is charged per dispatch. The outgoing task's save cost and any scheduler run-time cost are not modelled.
- Overhead heats the core like useful work. Cache or TLB effects on *later* ticks are not modelled; the cost is a one-off lump at dispatch.
- Overhead feeds back into scheduling (it increases remaining work, which changes slack and later decisions), so effects are not simply additive.
- Still deterministic, single runs, 6 tasks per workload.

**Outcome for TA-EDF vs EDF** (details in [AUDIT_FIXES.md](AUDIT_FIXES.md)):
- **EDF performs no migrations** in any run. Its results move by at most 2 tardiness ticks across the whole cost grid.
- **TA-EDF's results depend on the migration cost.** At 0.1 work units per migration it already has more total tardiness and a longer makespan than EDF in every workload, under both DVFS settings. At 0.25 and above it also misses more deadlines in Burst VR.
- Context-switch cost alone changes TA-EDF vs EDF by at most 5 tardiness ticks.
- TA-EDF keeps a lower peak temperature than EDF in Normal, Sustained and HOT across the grid (roughly 1–2.5 °C), but not in Burst VR, where its peak becomes higher once migrations cost anything.

## Deviations from the inspection plan

1. **No new workloads.** You asked for the four existing workloads only. Consequence: in Sustained and HOT the deadlines are infeasible for *any* policy (Sustained needs at least 245 / 2 ≈ 123 ticks of work against deadlines of 45–60), so deadline misses stay saturated at 4–6 of 6. Total tardiness is reported because it still discriminates between policies.
2. **EAS not implemented** (reason above).
3. **Thermal-DVFS is not kept as a separate buggy policy.** It equals FCFS under the `hysteresis` setting.

## Validity notes and limitations

- **ThermOS-VR v1 == FCFS under the same DVFS setting**, on every metric and every workload. The engine reproduces v1 exactly: every task outcome and every per-tick temperature match on all four workloads (`test_legacy_equivalence.py`).
- **TA-EDF's idle insertion never idled a core** (see above). Its benchmark differences from EDF come from migration-based coolest-core placement. Those differences are reversed for responsiveness once migrations cost 0.1 tick or more.
- **The EEVDF-inspired policy has no fairness guarantee on two cores** (see above).
- Each configuration is one deterministic run of 6 one-shot tasks, with no randomness or variance, so **no difference can be called statistically significant**. Differences of a few tenths of a degree should not be read as meaningful.
- Time advances in one-unit ticks; the tick has no defined real-time length.
- No measured hardware data of any kind (temperature, power, energy, latency) is used or produced.
