# ThermOS-VR research presentation: speaking notes

Deck: `07_Report/ThermOS_VR_Research_Presentation.pptx` (16 slides, about 20–25 minutes). The same notes are embedded in each slide's speaker notes. All numbers are computed from the frozen result CSVs by `thermos_vr_ieee_paper/build_presentation.py`.

## Slide 1: Title slide

Good morning. Our project re-examines a thermal-aware scheduling idea for AR/VR-style workloads using a reproducible Python simulation. We compare eight policies, including modern deadline-driven baselines, under the same thermal model and DVFS governor. Everything we show is simulated; there are no hardware or headset measurements.

## Slide 2: Why scheduling and heat matter for AR/VR

AR and VR combine several time-critical activities. Motion-to-photon latency has been studied as a perceptual constraint in head-mounted displays (Jerald and Whitton 2009; Zhao et al. 2017). On phones, Zhang et al. (AIVR 2020) measured temperatures that kept rising over 20-minute VR and AR sessions despite frequency scaling, with peak CPU/GPU temperatures above 70 C in an AR game. The OS responds with DVFS, which lowers power density but slows execution. The question is whether the scheduler itself helps, or whether frequency control does the work.

## Slide 3: Research question and objectives

Our research question asks how three factors jointly affect two kinds of outcome. The objectives follow directly: re-evaluate ThermOS-VR fairly, add deadline-driven and fairness baselines, measure with DVFS off and on, and test how sensitive the results are to migration and context-switch costs. Scope is explicitly a simulation.

## Slide 4: Gap in the original evaluation and our contributions

The gap is partly in our own earlier prototype: only two of its five schedulers used DVFS, and its Thermal-DVFS baseline could run one task on two cores in the same tick. Published thermal-aware schedulers use detailed thermal models; our contribution is a controlled comparison under one shared simple model, with verification and honest negative results.

## Slide 5: Simulator architecture: one shared engine for every policy

Every tick follows the same order for every policy: form the ready set, let the policy map tasks to cores, execute one tick, update each core's temperature, let the governor pick the next frequency, record completions and log one trace row per core. The overhead model is used only in the sensitivity experiment.

## Slide 6: Workloads and system model

Four hand-specified workloads inherited from the prototype, each with six one-shot tasks. Dividing total work by two cores gives a lower bound on makespan; comparing it with the deadlines shows that Burst, Sustained and HOT are partly or largely infeasible for any policy, so miss counts saturate and we also report total tardiness. The two cores are identical in the model; the Performance/Efficiency labels are inherited names only.

## Slide 7: Thermal model and DVFS governor

Each core follows a first-order heating and cooling update with the parameters in the run metadata. Under full load a core settles at 75 C at 2.5 GHz and 63.7 C at 2.2 GHz, so the governor only ever uses 2.5 and 2.2 GHz on these workloads. The model is uncalibrated: these are model degrees, not device temperatures.

## Slide 8: Eight scheduling policies compared

Three classical baselines, the original ThermOS-VR heuristic, two EDF variants, our thermal-aware EDF, and an EEVDF-inspired weighted-fair policy. TA-EDF is our own variant, not an established scheduler. The EEVDF policy is inspired by the algorithm, not a reproduction of Linux EEVDF; it omits per-CPU queues, load balancing and sleep handling. EAS was not evaluated because it needs asymmetric cores and an energy model.

## Slide 9: Experimental methodology and verification

The main benchmark runs every combination once: 64 runs. The sensitivity study repeats all 64 for 16 migration and context-switch cost pairs: 1,024 runs. Costs are hypothetical simulated work units. Verification: 42 unit tests, independent recomputation of every metric from raw traces, fresh re-runs, an independent EDF reference implementation and pixel checks of every figure.

## Slide 10: Results: deadline-driven order gives the best responsiveness

With DVFS on, in Sustained and HOT the EDF variants have the lowest waiting times. Across all 16 workload, DVFS and metric cases an EDF variant attains the minimum, often tied. EDF and TA-EDF never differ by more than half a tick of waiting or two ticks of tardiness, so we do not claim either is more responsive. Round Robin is worst everywhere. Misses saturate in Sustained and HOT.

## Slide 11: Results: DVFS, not core scoring, drives the thermal reduction

ThermOS-VR matched FCFS on all 16 metrics in all 8 configurations: its core score cannot change outcomes because the cores are identical, the deadline term is the same for every core, and FCFS fixes the order. DVFS is what lowered the simulated peak: for FCFS on HOT, 71.74 to 62.49 C and HOT core-ticks 64 to 0, at the cost of a longer makespan (205 to 226). With DVFS on, no policy reached the HOT state; that is a property of the modelled governor, not proof of hardware safety. The chart shows core-ticks at or above 60 C.

## Slide 12: Migration overhead reverses the TA-EDF vs EDF comparison

TA-EDF achieves its lower peak by moving tasks to the cooler core: 193 migrations in HOT versus zero for EDF. In the main benchmark migrations are free. In the sensitivity study, once each migration costs 0.1 work units or more, TA-EDF has more tardiness and a longer makespan than EDF in all 96 matched configurations. Its simulated peak stays 0.99 to 2.49 C below EDF in Normal, Sustained and HOT; in Burst it becomes higher. Its idle-insertion rule never left a core idle.

## Slide 13: Key findings: what worked, what tied, what did not

Deadline-driven order is the consistent gain. DVFS produces the thermal reduction, at a makespan cost. ThermOS-VR ties FCFS. TA-EDF gives a small simulated peak reduction that depends on free migrations. Two mechanisms are untested or unguaranteed: idle insertion never fired, and the EEVDF-inspired policy has no lag bound on two cores (4, 15, 27 and 56 ineligible dispatches).

## Slide 14: Limitations and threats to validity

We state these limits explicitly. The thermal model is uncalibrated and linear; the two cores are identical; workloads are six one-shot hand-specified tasks; each configuration runs once, so no statistics; migrations are free in the main benchmark and the sensitivity costs are hypothetical; time is abstract ticks with partial-tick rounding; and there is no hardware, power or energy data.

## Slide 15: Conclusion and future work

Within this model: ThermOS-VR behaves like FCFS under equal DVFS; deadline-driven order gives the best responsiveness; TA-EDF's coolest-core placement lowers the simulated peak only through migrations that stop paying off once they cost anything. Next steps are realistic: periodic frame workloads, randomised repeated runs, asymmetric cores with a power model, a sticky TA-EDF, trace-driven XR workloads and eventually hardware validation.

## Slide 16: Key references and questions

These are the key verified references; the paper lists all 38 with DOIs. Numbers match the paper's reference list. Thank you; we welcome your questions.
