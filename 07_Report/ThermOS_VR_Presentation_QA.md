# ThermOS-VR presentation: likely viva questions and accurate answers

Every figure quoted here comes from the frozen result files, checked by `thermos_vr_ieee_paper/build_presentation.py` and `thermos_vr_ieee_paper/evidence/evidence_checks.py`. "Model °C" means the simulator's temperature unit, not a measured temperature.

## Scope and method

**Q1. Did you modify an operating-system kernel or test on a headset?**
No. This is a deterministic Python simulation of two cores. No kernel was changed and no phone, headset, power meter or thermal camera was used. All temperatures are outputs of an uncalibrated model.

**Q2. What exactly did you run?**
- The main benchmark: 8 policies × 4 workloads × 2 DVFS settings (off and hysteresis) = 64 runs, one per configuration.
- A separate sensitivity study: all 64 repeated for 16 combinations of migration cost and context-switch cost in {0, 0.1, 0.25, 0.5} simulated work units, giving 1,024 runs.

**Q3. Why are the Performance and Efficiency cores identical?**
- The labels come from the original prototype, but in the model both cores have the same frequencies, speed and thermal parameters.
- We kept them identical so the four workloads stay comparable with the original study.
- As a consequence, we cannot make claims about real big.LITTLE heterogeneity.

**Q4. How do you know the simulator is correct?**
- 42 unit tests pass, including hand-derived EDF examples.
- EDF and EDF-NP agree with an independently written reference simulator in 18,024 comparisons, with 0 mismatches.
- Every one of the 1,024 metric values was recomputed from the raw per-tick traces.
- All 64 + 1,024 runs were re-executed and gave identical results.
- All 25 benchmark figures are pixel-identical to re-renders from the CSVs.
- For FCFS, Priority, Round Robin and ThermOS-VR, the engine reproduces the original prototype's per-task outcomes and temperatures exactly.

**Q5. Why no statistical significance?**
- The workloads and simulator are deterministic, so each configuration was run once.
- With no randomness and no repeated trials, there is no variance from which to compute confidence intervals or significance tests.
- We report the observed differences only.

## Thermal model and DVFS

**Q6. What is the thermal model?**
- Each tick: T(k+1) = T(k) + α·(w/100)·(f/2.5)² − β·(T(k) − 25), with α = 1 and β = 0.02.
- Each core starts at 45 °C; ambient is 25 °C. An idle core produces no heat, and there is no heat transfer between cores.
- Thermal states: COOL below 60, WARM below 70, HOT below 80, and CRITICAL at 80 model °C or above.

**Q7. Why does the governor never use 1.8 or 1.4 GHz?**
- Under full load the model settles at 25 + (f/2.5)²/0.02. That is 75.0 °C at 2.5 GHz and 63.7 °C at 2.2 GHz.
- 63.7 °C is below the 70 °C step-down threshold, so the governor never needs a lower level on these workloads.
- The lower levels were exercised only in a stress test with a higher heat coefficient.

**Q8. Does "no policy reached HOT with DVFS on" mean the system is thermally safe?**
No. It is a property of this governor and these model parameters. It says nothing about real hardware.

## Results

**Q9. Why does ThermOS-VR give exactly the same results as FCFS?**
- It keeps FCFS order and runs tasks to completion, so every task's start and finish time is fixed before a core is chosen.
- Its score can only choose between two identical idle cores, and its deadline term adds the same constant to both.
- Swapping tasks between identical cores changes no aggregate metric.
- Result: all 16 metrics were identical in all 8 configurations, 128 comparisons in total.

**Q10. Then where did ThermOS-VR's original thermal benefit come from?**
- From DVFS: in the original comparison only ThermOS-VR and Thermal-DVFS used the governor.
- With the same governor, FCFS on the HOT workload drops from a peak of 71.74 to 62.49 model °C, and its HOT core-ticks from 64 to 0.
- The cost is a longer makespan: 205 to 226 ticks.

**Q11. What was wrong with the original Thermal-DVFS baseline?**
- Its ready list did not exclude running tasks, so a task could be assigned to a second core in the same tick, and its waiting times were inflated.
- Its v1 results are invalid and are not used. In the corrected engine it is simply FCFS under the hysteresis governor.

**Q12. Which policy is most responsive?**
- An EDF variant (EDF or TA-EDF) had the lowest or tied-lowest average waiting time and total tardiness in all 16 combinations of workload, DVFS setting and metric.
- EDF and TA-EDF never differed by more than 0.5 ticks of waiting or 2 ticks of tardiness, in both directions, so we do not claim either is better.
- Round Robin was worst in every configuration.

**Q13. Why do almost all policies miss 4 or 6 deadlines in Sustained and HOT?**
The deadlines are infeasible on two cores:

| Workload | Total work | Makespan lower bound | Deadlines |
|---|---|---|---|
| Sustained | 245 | 122.5 | 45–60 |
| HOT | 405 | 202.5 | 75–100 |

Miss counts therefore saturate, which is why we also report total tardiness.

**Q14. Does TA-EDF reduce temperature?**
- At zero migration cost, its simulated peak is below EDF's in all 8 configurations, by 0.08–2.49 model °C.
- Across the sensitivity grid it stays 0.99–2.49 °C below EDF in Normal, Sustained and HOT. In Burst VR it is 0.70–3.93 °C *above* EDF once migrations cost anything.
- With DVFS off it has *more* core-ticks at or above 60 °C than EDF (154 vs 137 in Sustained, 304 vs 299 in HOT).
- These are model values from single runs, so the effect is small and mixed.

**Q15. How does TA-EDF lower the peak?**
- By coolest-core placement, which it does through frequent migrations: 8 / 41 / 77 / 193 in Normal / Burst / Sustained / HOT with DVFS on, compared with 0 for EDF.
- Its hold-back (idle-insertion) rule never left a core idle in any of the 64 runs. By the time a core reached 59 °C, the task it would hold back either had another, cooler core free or had been beaten to the cores by earlier-deadline tasks.

**Q16. What happens when migrations are not free?**
- For every migration cost of 0.1 work units or more, TA-EDF had higher total tardiness (+1 to +365 ticks) and a longer makespan (+2 to +121 ticks) than EDF in all 96 matched configurations.
- EDF never migrates, so its tardiness changed by at most 2 ticks across the whole cost grid.
- Context-switch cost alone (migration cost 0) changed the TA-EDF − EDF tardiness difference only within −4 to +5 ticks.

**Q17. Are the overhead costs realistic?**
- They are hypothetical fractions of an abstract tick, not measured latencies.
- They test sensitivity: real context switches have measurable indirect costs (Li, Ding and Shen, ExpCS 2007), but we did not calibrate to them.

**Q18. Is your EEVDF policy the Linux EEVDF scheduler?**
- No. It models weights, virtual runtime, lag, eligibility and virtual deadlines with one global queue and a one-tick slice.
- It omits per-CPU queues, load balancing, sleep and lag handling, and wake-up preemption.
- On one core its lag stayed below one slice. On two cores it dispatched ineligible tasks in 4 / 15 / 27 / 56 ticks and lag reached 22.59 slices, so it carries no fairness guarantee there.

**Q19. Why did you not evaluate Energy Aware Scheduling?**
- The Linux documentation states that EAS does not support symmetric CPU topologies, and that it needs an energy model and the schedutil governor.
- Our cores are identical and the model has no power or energy, so any EAS-style policy would reduce to an arbitrary choice.

**Q20. Does placement reduce total heat?**
- Not with DVFS off. The model is linear and the cores are identical, so total heat is fixed by the work: 18.20 / 58.00 / 205.00 / 359.25 model units for every policy.
- Placement can only redistribute heat, which changes peak temperature and threshold counts.

## Limitations and future work

**Q21. What are the main limitations?**
- An uncalibrated linear thermal model.
- Identical cores with no heat transfer between them.
- Four hand-specified workloads of six one-shot tasks, without periodic frames and with partly infeasible deadlines.
- Single deterministic runs.
- Zero overhead in the main benchmark, and hypothetical costs in the sensitivity study.
- Abstract ticks, with a partial final tick counted as fully busy (88 of 384 task records).
- No hardware, power or energy data.

**Q22. What would you do next?**
- Periodic frame-task workloads with feasible deadlines.
- Seeded random workloads with repeated runs and confidence intervals.
- Asymmetric cores plus a power model, which would allow an EAS-style comparison.
- A sticky, rate-limited TA-EDF.
- Trace-driven XR workloads, for example from ILLIXR.
- Validation on real hardware.

**Q23. What is your own contribution versus prior work?**
- A verified, shared simulator.
- The finding that ThermOS-VR ≡ FCFS under equal DVFS.
- A corrected baseline.
- An evaluation of EDF variants and our TA-EDF.
- A migration-overhead sensitivity analysis showing TA-EDF's dependence on free migrations.
- Thermal-aware scheduling, EDF and EEVDF themselves are prior work, cited in the paper.
