# ThermOS-VR v2: modern scheduling baselines

This folder adds EDF, Thermal-aware EDF and an EEVDF-inspired policy to the
ThermOS-VR **simulation**. Every policy runs in one shared engine with the same
inputs and metric definitions. Everything here is a Python simulation: the
temperatures, frequencies and heat values are model outputs. They are not
measurements from a real CPU or headset.

The v1 code (`day1`–`day4`), `05_Results/experiment_results.csv` and the v1
figures are **unchanged** (verified by SHA-256 in `verify_outputs.py`). A
backup is in `10_Backups/v1_original_2026-10-21/`. The v1 bugs found during
inspection are listed in [CONFIRMED_BUGS.md](CONFIRMED_BUGS.md).

## How to run

```
cd 03_Code/day5_modern_baselines
python -m unittest discover -s tests -v   # 32 tests
python run_benchmark.py                   # 64 runs -> 05_Results/v2_modern_baselines/
python plot_results.py                    # 25 figures -> 06_Figures/v2_modern_baselines/
python verify_outputs.py                  # independent cross-checks
```

## Files

| File | Purpose |
|---|---|
| `sim_engine.py` | Shared time loop, DVFS governors, two-core platform (reuses v1 `Process`, `Core`, `ThermalModel` unchanged) |
| `policies.py` | All 8 policies |
| `metrics_v2.py` | Metric definitions (one definition for every policy) |
| `run_benchmark.py` | Benchmark runner (writes only to `05_Results/v2_modern_baselines/`) |
| `plot_results.py` | Figures from the CSV + `figure_manifest.csv` |
| `verify_outputs.py` | Recomputes metrics from raw traces, re-runs all simulations, checks figures vs the CSV, checks the v1 files are unchanged |
| `tests/` | Hand-verified unit tests, governor tests, v1-equivalence tests |

## Simulation model (shared by every policy)

- **Platform:** 2 cores, labelled Performance / Efficiency as in v1. **They are physically identical:** same frequencies, speed and thermal parameters.
- **Tick order:** dispatch → execute (`frequency / 2.5` work units) → thermal update → DVFS → `t += 1` → completions → log.
- **Thermal model:** v1 parameters: ambient 25 °C, start 45 °C, heat `(w/100)(f/2.5)²`, cooling `0.02(T−25)`. An idle core generates no heat.
- **Preemption:** happens only at tick boundaries. Migration and context switches cost nothing in this model.
- **Deadlines:** absolute. A miss means `completion > deadline`. Late tasks are **not dropped**; they run to completion (soft real-time), so every task has a turnaround.
- **Arrivals:** a task can be dispatched at the tick equal to its arrival time.

### DVFS settings (every policy runs under both)

- `off`: fixed 2.5 GHz.
- `hysteresis`: the corrected four-level governor. It steps down one level at 60 / 70 / 80 °C and up at 58 / 68 / 78 °C, at most one step per tick.

**Verified reachability (bug B3):** with the v1 thermal parameters, only 2.5 and 2.2 GHz ever occur. At 2.2 GHz the core settles at 63.7 °C, which is below the 70 °C step-down point. So the multi-level fix changes nothing on the four workloads (tested). With a stress parameter set (`heat_coefficient = 2.5`) the corrected governor reaches all four levels and holds the core near 80 °C, while the v1 logic overheats past 80 °C (tested).

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

"Thermal-DVFS" from v1 is FCFS run under the `hysteresis` setting. It is not a separate policy here (bug B1 is fixed by the engine).

### EDF (global, preemptive)

At every tick boundary, the m = 2 tasks with the earliest absolute deadlines
among running and ready tasks are selected.

- **Ties:** earlier arrival, then lower PID.
- **Selected tasks:** a selected task that is already running keeps its core. A newly selected task takes the lowest free core ID, so EDF is thermally blind.
- **Preemption:** a running task that is no longer among the top m is preempted.
- **Late tasks:** keep their original deadline and therefore keep high priority. This is standard EDF; under overload it can cause a chain of misses.

EDF-NP uses the same order, but a dispatched task runs to completion.

### Thermal-aware EDF (TA-EDF): our own policy, not an established scheduler

Task order is the same as EDF. Define `slack = deadline − t − remaining_work`.

1. **Deadline-aware core choice.**
   - An *urgent* task (`slack ≤ 2`) takes the core with the highest current frequency, then the coolest.
   - Any other task takes the **coolest** core, then the highest frequency.
   - Remaining ties go to the task's current core, then the lowest ID.
2. **Thermal idle insertion.**
   - A core at or above 59 °C (1 °C below the DVFS throttle point) accepts only tasks with `slack < 10`.
   - A task with more slack is held back so the core can cool before DVFS slows it.
   - The delay is bounded: slack falls by 1 per waiting tick, so a held task is dispatched once its slack drops below 10 (unit-tested).

**How it differs:**
- **From EDF:** the same tasks run in the same order, but placement is temperature- and frequency-aware, and it may deliberately idle a hot core.
- **From ThermOS-VR v1:**
  - Task order is by deadline instead of arrival.
  - It preempts.
  - The urgency term changes *which core* a task gets. In v1 the deadline score is identical for every core, so it never affects the choice.
  - It can withhold work for thermal reasons.

### EEVDF-inspired: simplified, not the Linux implementation

**Modeled (after Stoica & Abdel-Wahab 1995 and Linux ≥ 6.6):**
- weights from priority via the kernel's nice-to-weight table (priority 1–5 → nice −10, −5, 0, 5, 10 → weights 9548, 3121, 1024, 335, 110)
- virtual runtime advanced by `1024 / w` per tick of execution
- `V` = weighted average virtual runtime of runnable tasks
- eligibility `v ≤ V` (lag ≥ 0)
- virtual deadline `vd = v + slice · 1024 / w`
- the eligible task with the earliest `vd` is picked
- new tasks are placed at zero lag

**Simplified:**
- one global runqueue (Linux has per-CPU runqueues plus load balancing)
- slice = 1 tick, so tasks are re-picked every tick
- if fewer tasks are eligible than there are cores, ineligible tasks fill the rest (work-conserving)
- no sleep/wakeup modelling
- **real task deadlines and temperatures are not used** (it is a fairness scheduler)

### EAS-inspired: not implemented

Linux Energy-Aware Scheduling is enabled only on platforms with asymmetric CPU
capacity and an energy model (per-CPU power at each frequency). In this
simulator the two cores are identical, so every placement has the same
estimated energy and an EAS-style policy would reduce to an arbitrary choice.

Making it meaningful would require new core capacities and a power table.
That would change the platform under the four existing workloads, so the
results would no longer be comparable with v1. It is left as a separate
future experiment on an explicitly asymmetric platform.

## Metrics

Every metric uses the same definition for every policy. The definitions are
exported in `05_Results/v2_modern_baselines/metric_definitions.csv`.
Temperature samples are the post-tick values for ticks 1 through makespan
(the t = 0 initial state is not a sample).

- **Waiting time:** counts every tick a task has arrived, is unfinished and is not running, including time after a preemption.
- **Core-time utilization:** busy core-ticks / (2 × makespan).
- **Thermal exposure:** core-ticks in HOT/CRITICAL (≥ 70 °C).
- **Core-ticks ≥ 60 °C:** reported because, with DVFS on, no policy ever reaches HOT.

## Deviations from the inspection plan

1. **No new workloads.** You asked for the four existing workloads only. Consequence: in Sustained and HOT the deadlines are infeasible for *any* policy (Sustained needs at least 245 / 2 ≈ 123 ticks of work against deadlines of 45–60), so deadline misses stay saturated at 4–6 of 6. Total tardiness is reported because it still discriminates between policies.
2. **EAS not implemented** (reason above).
3. **Thermal-DVFS is not kept as a separate buggy policy.** It equals FCFS under the `hysteresis` setting.

## Validity notes and limitations

- **ThermOS-VR v1 == FCFS under the same DVFS setting**, on every metric and every workload. The engine reproduces v1 exactly: every task outcome and every per-tick temperature match on all four workloads (`test_legacy_equivalence.py`).
- **TA-EDF's idle insertion never triggered** in the 64 benchmark runs. By the time a core reaches 59 °C, no waiting task has 10 ticks of slack. Every difference between TA-EDF and EDF comes from coolest-core placement, which relies on frequent migrations (up to 193 per run). The model charges nothing for these; on real hardware migrations cost cache and TLB state.
- Each configuration is one deterministic run of 6 tasks, with no randomness or variance. Differences of a few tenths of a degree should not be read as significant.
