# -*- coding: utf-8 -*-
"""
Paper content (single source for the DOCX and LaTeX renderers).

Inline markup:
  [@key] or [@k1;@k2]   citation (keys in paper_refs.REFS)
  {{tab:x}} {{fig:x}} {{sec:x}}   cross-references
  *text*                emphasis
Every number in the prose is asserted against the result CSVs in build_paper.py.
"""

TITLE = ("Thermal-Aware Scheduling for AR/VR-Inspired Workloads: A Reproducible "
         "Simulation Study of EDF, a Thermal-Aware EDF Variant and Classical Baselines")

AUTHORS = [
    ("Shreevidha Gour", "25BCE1337"),
    ("Vidhi Gulgulia", "25BCE1944"),
    ("Yahvi Tewari", "25BCE5364"),
]
AFFILIATION = ("B.Tech Computer Science and Engineering, School of Computer Science and "
               "Engineering, Vellore Institute of Technology")

ABSTRACT = (
    "Augmented- and virtual-reality (AR/VR) applications combine sustained computation with "
    "tight timing requirements, so on mobile processors they are exposed to both heat build-up "
    "and frequency throttling. This paper asks how scheduling policy, dynamic voltage and "
    "frequency scaling (DVFS) and task-migration overhead jointly affect responsiveness and "
    "simulated thermal behaviour under AR/VR-inspired workloads. We answer the question with a "
    "deterministic, tick-based Python simulator of two identical cores, a first-order thermal "
    "model and a threshold DVFS governor. Eight policies are compared: first-come first-served "
    "(FCFS), static priority, round robin, the original ThermOS-VR heuristic, non-preemptive and "
    "preemptive earliest deadline first (EDF), a thermal-aware EDF variant (TA-EDF) proposed "
    "here, and an EEVDF-inspired weighted-fair policy. The main benchmark contains 64 runs over "
    "four workloads of six one-shot tasks, and a separate sensitivity study adds 1,024 runs with "
    "migration and context-switch costs. Under an identical governor, ThermOS-VR produced exactly "
    "the same results as FCFS, which shows that its earlier thermal benefit came from DVFS rather "
    "than from its core-scoring rule. The EDF variants gave the lowest or tied-lowest waiting time "
    "and total tardiness in every configuration. With free migrations, TA-EDF lowered the "
    "simulated peak temperature by 0.08–2.49 °C relative to EDF while matching its "
    "responsiveness; once each migration cost 0.1 work units or more, TA-EDF had higher "
    "tardiness and a longer makespan than EDF in all 96 matched configurations. All temperatures "
    "are model outputs; no hardware, power or energy measurements were made.")

INDEX_TERMS = ("Thermal-aware scheduling, earliest deadline first, dynamic voltage and frequency "
               "scaling, AR/VR workloads, task migration, discrete-time simulation, reproducibility")

# Block types: ("h1", key, title) ("h2", key, title) ("p", text) ("ul", [items])
#              ("eq", label, latex, plain) ("table", key) ("figure", key)
BODY = [
# ---------------------------------------------------------------- I
("h1", "sec:intro", "Introduction"),
("p", "AR/VR applications run several interacting activities at once: frame rendering, head "
      "and hand tracking, physics, sensor fusion and audio. Users perceive delays between head "
      "motion and the displayed image, and both perception thresholds and measurement methods for "
      "this motion-to-photon latency have been studied in head-mounted displays "
      "[@jerald2009;@zhao2017]. Delivering high-quality VR on phone-class hardware therefore "
      "requires careful use of limited compute resources [@lai2017]. The same workloads heat the "
      "device: measurements on smartphones running VR video streaming and an AR game reported "
      "steadily rising component and surface temperatures over 20-minute sessions despite "
      "frequency scaling, with peak CPU and GPU temperatures above 70 °C in the AR case "
      "[@zhang2020]."),
("p", "Operating systems manage this tension through two complementary mechanisms. Dynamic "
      "thermal management and DVFS lower the operating frequency when temperature rises, which "
      "reduces power density but also slows execution [@brooks2001;@pillai2001]. Scheduling "
      "decides *which* task runs *where* and *when*; thermal-aware schedulers additionally use "
      "temperature when placing or ordering work [@kong2012]. Whether the scheduler itself can "
      "reduce thermal stress without harming responsiveness, or whether frequency control is "
      "doing most of the work, is not obvious, and the answer can depend on overheads that simple "
      "models ignore."),
("p", "This study began as an undergraduate operating-systems project, ThermOS-VR, which "
      "proposed a scoring heuristic that places each task on the core with the best combination "
      "of temperature, core type and deadline urgency. An audit of the original prototype found "
      "that its comparison baselines were not equivalent: only some of them used DVFS, and one "
      "baseline contained a defect that could run a task on two cores in the same tick. We "
      "therefore rebuilt the evaluation around a single shared engine and asked a sharper "
      "question: *how do scheduling policy, DVFS and migration overhead jointly affect "
      "responsiveness and simulated thermal behaviour under AR/VR-inspired workloads?*"),
("p", "The work is a simulation study. No kernel was modified, no headset or phone was "
      "measured, and all temperatures are outputs of an uncalibrated first-order model. Within "
      "that scope, the paper makes the following contributions:"),
("ul", [
    "A verified tick-based simulator in which eight policies share identical workloads, thermal "
    "parameters, governor settings and metric definitions, together with tests, independent "
    "recomputation of every reported metric and checksum-based preservation of all outputs.",
    "Evidence that the original ThermOS-VR score is equivalent to FCFS once both use the same "
    "governor, and a correction of an invalid baseline from the earlier prototype.",
    "An evaluation of deadline-driven baselines (non-preemptive and preemptive EDF) and of TA-EDF, "
    "a thermal-aware EDF variant introduced here, with DVFS disabled and enabled.",
    "A 1,024-run sensitivity analysis showing that TA-EDF's parity with EDF depends on migrations "
    "being free.",
    "A transparent account of negative and null results, including a TA-EDF mechanism that never "
    "activated and a fairness property that does not hold on two cores.",
]),
("p", "{{sec:related}} reviews related work. {{sec:model}} describes the system model, "
      "{{sec:policies}} the policies and {{sec:method}} the methodology. {{sec:results}} "
      "presents the results, {{sec:discussion}} interprets them, {{sec:limits}} lists limitations "
      "and future work, and {{sec:conclusion}} concludes."),

# ---------------------------------------------------------------- II
("h1", "sec:related", "Related Work"),
("h2", "sec:rw-rt", "Deadline-Driven Scheduling"),
("p", "Liu and Layland analysed fixed-priority and deadline-driven scheduling of periodic tasks "
      "on one processor and showed that assigning priorities by the nearest deadline can use the "
      "processor fully, which is the basis of EDF [@liu1973]. When preemption is not allowed, "
      "feasibility analysis changes; Jeffay, Stanat and Martel studied non-preemptive scheduling "
      "of periodic and sporadic tasks and the role of EDF in that setting [@jeffay1991]. Dhall "
      "and Liu studied the scheduling of periodic time-critical tasks on multiprocessors and "
      "analysed the worst-case behaviour of assignment heuristics [@dhall1978]. Davis and Burns "
      "survey the partitioned, global and hybrid multiprocessor approaches that followed, "
      "including the reasons why global policies such as EDF lose the optimality they have on a "
      "single processor [@davis2011]."),
("p", "Linux exposes deadline scheduling as SCHED_DEADLINE, which combines EDF with the "
      "Constant Bandwidth Server (CBS) so that each task is isolated within a reserved budget "
      "[@abeni1998;@lelli2016]. The kernel documentation describes per-task runtime, deadline and "
      "period parameters and an admission test on total bandwidth [@kdoc_deadline]. Our EDF "
      "policies are much simpler: they order one-shot tasks by absolute deadline, have no "
      "bandwidth reservation and no admission control, and continue to run tasks after their "
      "deadlines pass."),
("h2", "sec:rw-fair", "Proportional-Share Scheduling and EEVDF"),
("p", "Earliest Eligible Virtual Deadline First (EEVDF) allocates processor time in proportion "
      "to client weights. Each client accumulates virtual time, is eligible only while it has "
      "not received more than its share, and the eligible client with the earliest virtual "
      "deadline runs next; for a single resource the deviation from ideal service is bounded by "
      "one quantum [@stoica1995]. Proportional fairness is harder to guarantee on several "
      "processors: Pfair scheduling formalises proportionate progress on multiprocessors "
      "[@baruah1996], and Chandra *et al.* showed that weights which cannot be honoured on a "
      "symmetric multiprocessor lead to unfairness unless they are readjusted [@chandra2000]. "
      "Linux adopted a version of EEVDF proposed in 2023 [@corbet2023]; its documentation states "
      "that the transition began in kernel 6.6 and describes lag, virtual deadlines, requested "
      "time slices and deferred dequeue of sleeping tasks [@kdoc_eevdf]. Our EEVDF-inspired "
      "policy reproduces the core selection rule but not these kernel mechanisms."),
("h2", "sec:rw-thermal", "Thermal Management and Thermal-Aware Scheduling"),
("p", "Brooks and Martonosi argued that dynamic thermal management lets a processor be designed "
      "for typical rather than worst-case power, with little performance loss in common workloads "
      "[@brooks2001]. Skadron *et al.* introduced temperature-aware microarchitecture and the "
      "HotSpot model, and later work presented HotSpot as a compact resistance–capacitance "
      "thermal modelling methodology for early design stages [@skadron2003;@huang2006]. Kong, "
      "Chung and Skadron survey thermal management techniques, including operating-system and "
      "compiler approaches [@kong2012]. Real-time DVFS was integrated with scheduling by Pillai "
      "and Shin, who showed that voltage scaling must respect deadline guarantees [@pillai2001]."),
("p", "Thermal-aware scheduling has been studied from several directions. Hung *et al.* proposed "
      "thermal-aware task allocation and scheduling for embedded systems [@hung2005]; Coskun, "
      "Rosing and Whisnant evaluated operating-system-level temperature-aware scheduling policies "
      "for multiprocessor systems-on-chip [@coskun2007]; and Chrobak *et al.* analysed "
      "temperature-aware scheduling algorithmically, including online competitiveness results "
      "[@chrobak2008]. More recent work combines prediction with DVFS: Pérez Rodríguez and Meumeu "
      "Yomsi propose a proactive scheduler for a single DVFS-capable core [@perez2021], Lee, Shin "
      "and Chwa schedule real-time tasks on integrated CPU–GPU platforms while balancing heat "
      "(RT-TAS) [@lee2019], and Dowling *et al.* drive a multi-core thermal-aware scheduler, "
      "POD-TAS, with a reduced-order learned thermal model and compare it with RT-TAS in a "
      "simulation pipeline [@dowling2025]. These studies use far more detailed thermal models "
      "than ours; our contribution is not a better thermal model but a controlled comparison of "
      "scheduling policies under one shared, simple model."),
("h2", "sec:rw-hetero", "Heterogeneous and Mobile Platforms"),
("p", "Single-ISA heterogeneous multi-core designs run each application on the core that best "
      "matches its performance and power needs [@kumar2003]. Linux describes such systems as "
      "having asymmetric CPU capacity [@kdoc_capacity], and its Energy Aware Scheduling (EAS) "
      "selects an energy-efficient CPU at task wake-up using an energy model; EAS requires an "
      "asymmetric topology, power cost tables and the schedutil governor [@kdoc_eas]. On "
      "phones, frequency control has been managed jointly for the CPU and GPU to reduce the "
      "power of 3D games [@pathania2014], and reinforcement learning has been used to trade UI "
      "smoothness against power on a commercial Android device [@dou2025]. Detailed smartphone "
      "thermal simulators produce chip and skin temperature maps [@xie2014]. Our simulator has "
      "two identical cores and no energy model, so it cannot evaluate capacity- or energy-aware "
      "placement; we state this limitation explicitly rather than approximating EAS."),
("h2", "sec:rw-xr", "AR/VR Systems and Evaluation Practice"),
("p", "ILLIXR provides an open end-to-end XR system for studying real pipelines and their "
      "resource demands [@huzaifa2021]; trace-driven workloads of this kind are a natural next "
      "step beyond our hand-specified task sets. On methodology, Jain's text covers simulation and "
      "performance analysis [@jain1991], while Georges *et al.* and Hoefler and Belli argue that "
      "performance claims require repeated measurements and statistically sound reporting "
      "[@georges2007;@hoefler2015]. Because our simulator is deterministic and each configuration "
      "was executed once, we report observed differences without significance claims. Finally, "
      "context switches have measurable indirect costs, mainly through cache interference "
      "[@li2007], which motivates our sensitivity study of migration and context-switch overheads."),

# ---------------------------------------------------------------- III
("h1", "sec:model", "System Model and Architecture"),
("p", "{{fig:arch}} shows the simulator. A workload is a set of one-shot tasks. At every tick "
      "the engine forms the ready set, asks the active policy for a task-to-core mapping, executes "
      "one tick on each core, updates each core's temperature, lets the DVFS governor choose the "
      "frequency for the next tick, records completions and logs one trace row per core. The same "
      "engine, thermal model, governor and metric code are used for every policy."),
("figure", "fig:arch"),
("h2", "sec:model-tasks", "Tasks, Cores and Time"),
("p", "Each task *i* has an arrival time *a_i*, a burst (work) *b_i*, an absolute deadline "
      "*d_i*, a priority and a workload intensity *w_i* (in percent). Time advances in abstract "
      "ticks; the tick has no defined wall-clock length, so no result is converted to "
      "milliseconds. The platform has two cores that the original prototype labelled "
      "\"Performance\" and \"Efficiency\". In the model the two cores are identical: they have the "
      "same frequency levels, the same speed and the same thermal parameters, and no heat flows "
      "between them. The labels therefore do not represent hardware heterogeneity."),
("p", "A core running at frequency *f* completes *f*/2.5 GHz work units per tick, so a task "
      "progresses one unit per tick at 2.5 GHz and 0.88 units at 2.2 GHz. Preemption and "
      "migration can occur only at tick boundaries. A task finishes at the end of the tick in "
      "which its remaining work reaches zero; if that happens partway through a throttled tick, "
      "the unused fraction of the tick is still counted as busy time and still generates heat. "
      "In the benchmark, 88 of the 384 task records finish partway through their final tick, "
      "with at most 0.96 units of unused capacity. This accounting rule is applied identically "
      "to every policy, but it slightly overstates busy time and heat."),
("h2", "sec:model-thermal", "Thermal Model"),
("p", "Each core's temperature *T* (in model degrees Celsius) evolves by a first-order "
      "heating-and-cooling update:"),
("eq", "eq:thermal",
 r"T_{k+1} = T_k + \alpha\,\frac{w}{100}\left(\frac{f}{f_{\mathrm{ref}}}\right)^{2} - \beta\,(T_k - T_{\mathrm{amb}})",
 "T(k+1) = T(k) + α·(w/100)·(f/f_ref)² − β·(T(k) − T_amb)"),
("p", "with α = 1, β = 0.02, *f_ref* = 2.5 GHz and ambient temperature *T_amb* = 25 °C; every "
      "core starts at 45 °C, and an idle core generates no heat (*w* = 0). Thermal states are "
      "COOL below 60 °C, WARM below 70 °C, HOT below 80 °C and CRITICAL at or above 80 °C. Under "
      "a constant load the temperature converges to"),
("eq", "eq:steady",
 r"T^{*} = T_{\mathrm{amb}} + \frac{\alpha}{\beta}\,\frac{w}{100}\left(\frac{f}{f_{\mathrm{ref}}}\right)^{2},",
 "T* = T_amb + (α/β)·(w/100)·(f/f_ref)²,"),
("p", "which is 75.0 °C for a fully loaded core at 2.5 GHz and 63.7 °C at 2.2 GHz. The model is "
      "linear in temperature and both cores are identical, a property that matters when "
      "interpreting placement effects ({{sec:discussion}}). It is a teaching-scale model: it is "
      "not calibrated against any processor, and its outputs are not physical temperatures, "
      "powers or energies."),
("h2", "sec:model-dvfs", "DVFS Governor"),
("p", "Two DVFS settings are evaluated for every policy. With DVFS *off*, both cores always run "
      "at 2.5 GHz. With the *hysteresis* governor, each core steps down one frequency level "
      "(2.5 → 2.2 → 1.8 → 1.4 GHz) when its temperature reaches 60, 70 or 80 °C respectively, and "
      "steps back up only after cooling to 58, 68 or 78 °C; at most one step is taken per tick. "
      "Because a fully loaded core settles at 63.7 °C at 2.2 GHz, only the 2.5 and 2.2 GHz levels "
      "occur on the tested workloads; the lower levels were exercised only in a stress test with "
      "a higher heat coefficient. {{tab:params}} summarises the parameters."),
("table", "tab:params"),

# ---------------------------------------------------------------- IV
("h1", "sec:policies", "Scheduling Policies"),
("p", "At each tick a policy receives the ready tasks (arrived, unfinished and not running) and "
      "the current cores, and returns the task for each core. A policy preempts a task by not "
      "mapping it. Unless stated otherwise, ties are broken by earlier arrival and then lower "
      "task identifier, and \"lowest free core\" means the free core with the smaller index. Late "
      "tasks are never dropped: every task runs to completion, which corresponds to a soft "
      "real-time interpretation. {{tab:policies}} summarises the eight policies."),
("table", "tab:policies"),
("h2", "sec:pol-classic", "Classical Baselines"),
("p", "*FCFS* orders ready tasks by arrival and runs each to completion on the lowest free core. "
      "*Priority* is identical except that it orders by static priority (a lower number means "
      "higher priority). *Round Robin* (RR) keeps a single first-in first-out queue with a "
      "quantum of one tick: at each boundary the tasks whose quantum expired re-enter the queue "
      "before newly arrived tasks, and idle cores take tasks from the head of the queue."),
("h2", "sec:pol-thermos", "ThermOS-VR"),
("p", "ThermOS-VR keeps FCFS order and non-preemptive execution, but chooses among idle, "
      "non-CRITICAL cores by maximising a score"),
("eq", "eq:score",
 r"S(i,c,t) = 1.5\,(100 - T_c) - \pi(c) + \kappa(i,c) + \delta(i,t),",
 "S(i,c,t) = 1.5·(100 − T_c) − π(c) + κ(i,c) + δ(i,t),"),
("p", "where π(*c*) is a penalty of 10 for a WARM core and 50 for a HOT core, κ(*i*,*c*) favours "
      "the \"Performance\" label for intensities of at least 70 % and the \"Efficiency\" label for "
      "intensities of at most 40 %, and δ(*i*,*t*) is 30 if the time to the deadline does not "
      "exceed the remaining work and 15 otherwise. The deadline term depends only on the task and "
      "the time, not on the core, so it adds the same constant to every candidate and cannot "
      "change the ranking. Because the two cores are physically identical and the task order is "
      "fixed by FCFS, the remaining terms can change *which* identical core receives a task but "
      "not when any task runs. We use a faithful port of the original code; it selects the same "
      "core as the original function in 2,000 randomised states."),
("h2", "sec:pol-edf", "EDF Variants"),
("p", "*Non-preemptive EDF (EDF-NP)* orders ready tasks by absolute deadline and runs each "
      "dispatched task to completion on the lowest free core. *Preemptive global EDF (EDF)* "
      "re-selects, at every tick boundary, the two tasks with the earliest deadlines among "
      "running and ready tasks; a selected task that is already running keeps its core, and a "
      "newly selected task takes the lowest free core, so EDF is thermally blind. Late tasks keep "
      "their original deadlines and therefore retain high priority, as in standard EDF."),
("h2", "sec:pol-taedf", "Thermal-Aware EDF (TA-EDF)"),
("p", "TA-EDF is the variant proposed in this work; it is not an established scheduler. It "
      "uses the same task order as EDF and adds two thermal rules based on the slack"),
("eq", "eq:slack", r"s_i(t) = d_i - t - r_i,", "s_i(t) = d_i − t − r_i,"),
("p", "where *r_i* is the remaining work. A task is *urgent* if *s_i* ≤ 2. An urgent task takes "
      "the free core with the highest current frequency (then the cooler one); any other task "
      "takes the coolest free core (then the higher frequency); remaining ties prefer the core "
      "the task last ran on. The second rule is a hold-back, or idle-insertion, rule: a task "
      "with *s_i* ≥ 10 is skipped for the current tick if its chosen core is at or above 59 °C, "
      "one degree below the governor's first threshold, so that the core can cool. A skipped "
      "task's slack falls by one per tick, so the delay is bounded. The parameters (2, 59 °C, 10) "
      "were fixed before the benchmark and were not tuned. With DVFS off both cores always run at "
      "the same frequency, so both placement rules reduce to choosing the coolest free core."),
("h2", "sec:pol-eevdf", "EEVDF-Inspired Weighted-Fair Policy"),
("p", "This policy models the defining EEVDF rules [@stoica1995] at tick granularity. Task "
      "priorities 1–5 are mapped, by our own assumption, to nice values −10, −5, 0, 5 and 10 and "
      "hence to weights 9548, 3121, 1024, 335 and 110. A task that runs for a tick advances its "
      "virtual runtime by 1024/*w_i*. The policy computes"),
("eq", "eq:eevdf",
 r"V = \frac{\sum_j w_j v_j}{\sum_j w_j}, \quad \ell_i = w_i (V - v_i), \quad \hat{d}_i = v_i + q\,\frac{1024}{w_i},",
 "V = Σ_j w_j·v_j / Σ_j w_j,   ℓ_i = w_i·(V − v_i),   vd_i = v_i + q·1024/w_i,"),
("p", "where *V* is the weighted average virtual runtime of runnable tasks, ℓ_i is the lag and "
      "the virtual deadline is renewed after each slice *q* = 1 tick. A task is eligible when "
      "its lag is non-negative, and the eligible tasks with the earliest virtual deadlines run; "
      "new tasks start with zero lag. The policy ignores real deadlines and temperatures. It "
      "differs from Linux EEVDF in important ways: it uses one global queue rather than per-CPU "
      "queues with load balancing, it does not model sleeping, lag decay or wake-up preemption, "
      "and, to keep both cores busy, it dispatches an ineligible task when fewer eligible tasks "
      "than cores exist. We therefore call it *EEVDF-inspired* and make no claim of "
      "Linux-equivalent fairness."),
("h2", "sec:pol-eas", "Mechanisms Not Evaluated"),
("p", "Energy Aware Scheduling was not implemented or benchmarked. The kernel documentation "
      "states that EAS does not support symmetric CPU topologies and requires an energy model "
      "and the schedutil governor [@kdoc_eas]; our two identical cores and the absence of a power "
      "model would reduce any EAS-style policy to an arbitrary choice. Likewise, none of the "
      "policies is SCHED_DEADLINE [@kdoc_deadline] or kernel EEVDF [@kdoc_eevdf]."),

# ---------------------------------------------------------------- V
("h1", "sec:method", "Experimental Methodology"),
("h2", "sec:method-workloads", "Workloads"),
("p", "Four workloads inherited from the original prototype are used without modification "
      "({{tab:workloads}}). Each contains six one-shot tasks named after AR/VR subsystems, with "
      "hand-specified arrivals, bursts, deadlines, priorities and intensities. They are "
      "AR/VR-*inspired*: they are not traces of real applications and they are not periodic "
      "frame tasks. Dividing the total work by two gives a lower bound on the makespan of any "
      "two-core schedule at full speed. Normal VR is feasible in aggregate, but Burst VR "
      "(total work 63, bound 31.5, deadlines 10–24), Sustained Thermal (245, 122.5, deadlines "
      "45–60) and HOT Thermal (405, 202.5, deadlines 75–100) cannot meet most deadlines under "
      "any policy. Deadline-miss counts therefore saturate, and we also report total tardiness, "
      "which continues to separate the policies."),
("table", "tab:workloads"),
("h2", "sec:method-design", "Experimental Design and Metrics"),
("p", "The main benchmark runs every combination of eight policies, four workloads and two DVFS "
      "settings once, giving 64 runs and 384 task records. Each run uses fresh task and core "
      "objects, the same initial temperature and the same metric code. Migration and "
      "context-switch costs are zero in this benchmark; their effect is studied separately. The "
      "metrics are defined identically for every policy. *Waiting time* counts every tick a task "
      "has arrived, is unfinished and is not running, including time after preemption. "
      "*Tardiness* is max(0, completion − deadline), summed over tasks, and a deadline is missed "
      "when the completion time exceeds it. *Peak* and *average temperature* are taken over all "
      "post-tick core samples. *HOT core-ticks* count samples at or above 70 °C, and *core-ticks "
      "≥ 60 °C* count samples at or above the governor's first threshold. *Throttled busy "
      "core-ticks* count busy samples executed below 2.5 GHz, *heat generated* sums the model's "
      "heat term, and a *migration* is counted whenever a task executes on a different core from "
      "the one it last executed on."),
("h2", "sec:method-overhead", "Overhead Sensitivity Experiment"),
("p", "The second experiment repeats all 64 configurations for every combination of a "
      "migration cost and a context-switch cost in {0, 0.1, 0.25, 0.5} simulated work units, one "
      "unit being one tick of work at 2.5 GHz, which yields 1,024 runs. A dispatch event occurs "
      "when a task runs in a tick but did not run on the same core in the previous tick. A "
      "first dispatch is free; a dispatch to a different core from the last one is charged the "
      "migration cost; a dispatch back to the same core after a gap is charged the "
      "context-switch cost. Each event is charged once, so a migration is never also charged as a "
      "context switch. The charge is added to the task's remaining work, so the core spends that "
      "capacity, and generates the corresponding heat, before the task progresses. The costs are "
      "hypothetical fractions of a tick; they are not calibrated to measured latencies, although "
      "real context switches do have measurable indirect costs [@li2007]."),
("h2", "sec:method-verify", "Corrections, Verification and Reproducibility"),
("p", "The earlier prototype's results were not reused as baselines. Its Thermal-DVFS baseline "
      "could assign a running task to a second core in the same tick, its DVFS logic never "
      "stepped below 2.2 GHz, its schedulers used different logging rules, and only two of its "
      "five schedulers used DVFS. In the new engine, the earlier \"Thermal-DVFS\" baseline is "
      "simply FCFS under the hysteresis governor, a runtime check rejects any mapping that places "
      "a task on two cores, and all policies share one logging rule. For FCFS, Priority, RR and "
      "ThermOS-VR, the engine reproduces the earlier prototype's per-task outcomes and per-tick "
      "temperatures exactly when configured with the same governor behaviour."),
("p", "{{tab:verify}} lists the verification performed. All checks were executed on the final "
      "code and outputs, and every number in this paper was recomputed from the result files by "
      "an independent script. The commands to reproduce the experiments are "
      "`python -B run_benchmark.py`, `python -B run_sensitivity.py` and `python -B "
      "plot_results.py`, followed by `python -B verify_outputs.py` and `python -B "
      "verify_sensitivity.py`; the runners refuse to overwrite existing outputs unless "
      "`--overwrite` is given. The software environment was Python 3.14.0, pandas 3.0.5, "
      "matplotlib 3.10.7 and NumPy 2.3.4 on Windows 11."),
("table", "tab:verify"),

# ---------------------------------------------------------------- VI
("h1", "sec:results", "Results"),
("p", "All values below come from single deterministic runs. Differences are reported as "
      "observed; no statistical significance is implied."),
("h2", "sec:res-thermos", "ThermOS-VR Versus FCFS"),
("p", "Under the same governor, ThermOS-VR and FCFS produced identical values for all 16 "
      "metrics in all eight workload and DVFS configurations (128 comparisons, none different). "
      "Per-core placement differed in Normal VR, where two tasks were placed on the opposite "
      "cores, but the cores are identical and the differences cancelled in every metric. The "
      "thermal improvement attributed to ThermOS-VR in the earlier prototype is therefore "
      "explained by DVFS: for FCFS on the HOT workload, enabling the governor lowered the "
      "simulated peak from 71.74 to 62.49 °C and the HOT core-ticks from 64 to 0, while the "
      "makespan grew from 205 to 226 ticks. On Sustained Thermal the peak fell from 67.61 to "
      "61.28 °C and the makespan grew from 125 to 135 ticks. Normal VR and Burst VR never reach "
      "60 °C, so the governor does not change them."),
("h2", "sec:res-resp", "Responsiveness"),
("p", "{{tab:resp}} and {{fig:wait}} report the responsiveness metrics with DVFS enabled. An EDF "
      "variant attained the minimum waiting time and the minimum total tardiness in all 16 "
      "combinations of DVFS setting, workload and metric, often with ties. In Normal VR, a "
      "waiting time of 2.83 ticks is shared by Priority, EDF-NP, EDF and TA-EDF, and a total "
      "tardiness of 2 ticks is shared by six policies. With DVFS enabled, TA-EDF had the lowest "
      "waiting time in Sustained Thermal (40.83 ticks versus 41.33 for EDF) and HOT Thermal "
      "(69.17 versus 69.50), while EDF had the lowest tardiness in HOT Thermal (368 versus 369). "
      "Across all eight configurations, EDF and TA-EDF never differed by more than 0.5 ticks of "
      "waiting time or 2 ticks of tardiness, in both directions; we therefore do not claim that "
      "either is more responsive."),
("table", "tab:resp"),
("figure", "fig:wait"),
("p", "Preemption mattered: EDF-NP improved on FCFS, Priority and ThermOS-VR only in Sustained "
      "and HOT Thermal, and tied them in Burst VR (4.33 ticks). Round Robin had the highest "
      "waiting time and the highest total tardiness in every configuration (for example, a "
      "tardiness of 697 ticks in HOT Thermal with DVFS enabled, against 368 for EDF), and the "
      "EEVDF-inspired policy had the second-highest waiting time everywhere. Both missed all six "
      "deadlines in Sustained and HOT Thermal, whereas every other policy missed four. "
      "{{fig:tard}} shows the corresponding tardiness values. With DVFS disabled the same pattern "
      "held ({{tab:thermoff}}): the EDF variants again had the lowest values and Round Robin and "
      "the EEVDF-inspired policy the highest waiting times. EDF and TA-EDF tied in Sustained "
      "Thermal (waiting 39.17 ticks, tardiness 182) and on tardiness in HOT Thermal (305), and EDF "
      "had the lower waiting time in HOT Thermal (64.17 versus 64.33 ticks)."),
("figure", "fig:tard"),
("h2", "sec:res-thermal", "Simulated Thermal Behaviour"),
("p", "With DVFS enabled ({{tab:thermon}}), no policy reached the HOT state in any workload. "
      "This is a consequence of the modelled governor and parameters (a loaded core settles near "
      "63.7 °C at 2.2 GHz) and says nothing about the thermal safety of real hardware. Core-ticks "
      "at or above 60 °C separated the policies more clearly ({{fig:ge60}}): in Sustained Thermal "
      "they ranged from 5 for Round Robin and 28 for TA-EDF to 108 for EDF, and in HOT Thermal "
      "from 49 for Round Robin and 257 for TA-EDF to 286 for EDF. Round Robin achieves its low "
      "values by interleaving light and heavy tasks, at the cost of the worst responsiveness "
      "reported above."),
("table", "tab:thermon"),
("figure", "fig:ge60"),
("p", "At zero overhead, TA-EDF's simulated peak temperature was below EDF's in all eight "
      "configurations ({{fig:peak}}), by between 0.08 °C (Burst VR) and 2.49 °C (Normal VR). The "
      "reduction came with more throttling in one case: in HOT Thermal with DVFS enabled, TA-EDF "
      "spent 321 busy core-ticks below 2.5 GHz against 294 for EDF, because it kept both cores "
      "near the 60 °C threshold."),
("figure", "fig:peak"),
("p", "With DVFS disabled ({{tab:thermoff}}), only the HOT workload entered the HOT state. HOT "
      "core-ticks were 18 for Round Robin, 26 for TA-EDF, 35 for EDF-NP, 64 for FCFS, Priority "
      "and ThermOS-VR, 65 for EDF and 104 for the EEVDF-inspired policy. Core-ticks at or above "
      "60 °C did not follow the same ordering: TA-EDF had more than EDF in Sustained (154 versus "
      "137) and HOT Thermal (304 versus 299). Total model heat was identical for every policy "
      "within each workload (18.20, 58.00, 205.00 and 359.25 model units for Normal, Burst, "
      "Sustained and HOT)."),
("table", "tab:thermoff"),
("h2", "sec:res-mech", "What TA-EDF Actually Did"),
("p", "TA-EDF migrated tasks frequently: 8, 41, 77 and 193 times in Normal, Burst, Sustained and "
      "HOT with DVFS enabled (8, 41, 64 and 114 with DVFS disabled), whereas EDF never migrated a "
      "task. Its hold-back rule, by contrast, never left a core idle in any of the 64 runs. In "
      "each DVFS setting, a core at or above 59 °C coexisted with a task of sufficient slack in 31 "
      "ticks (3 in Sustained and 28 in HOT). In 31 cases that task was offered the other, cooler "
      "core and ran there; in 9 cases earlier-deadline tasks had already filled both cores; and "
      "once (HOT, tick 32) the task was skipped but the next EDF candidate took the core "
      "immediately. In these workloads, by the time cores are warm most tasks have little or "
      "negative slack, so the condition for idling a core never arises. TA-EDF's observed "
      "behaviour is therefore effectively preemptive EDF with migration-based coolest-core "
      "placement; the idle-insertion rule remains untested."),
("p", "The per-core temperature traces of the HOT workload ({{fig:trace}}) show what this "
      "placement does. We summarise them by the mean absolute temperature difference between the "
      "two cores over the run, computed from the per-tick trace. With DVFS enabled it was "
      "3.22 °C for EDF and 1.43 °C for TA-EDF, so coolest-core placement reduced the imbalance "
      "that EDF's sticky placement creates by more than half; with DVFS disabled the values were "
      "5.58 and 3.01 °C. FCFS, however, kept the cores even closer (0.72 °C with DVFS enabled), "
      "plausibly because its non-preemptive order runs similar heavy tasks side by side. Thermal "
      "balance alone is therefore not a distinguishing property of TA-EDF."),
("figure", "fig:trace"),
("h2", "sec:res-sens", "Sensitivity to Migration and Context-Switch Costs"),
("p", "Because EDF never migrated, its results were almost unaffected by the overhead costs: its "
      "total tardiness changed by at most 2 ticks across the whole cost grid. TA-EDF behaved "
      "differently ({{tab:sens}}, {{fig:sens}}). With zero migration cost, TA-EDF and EDF differed "
      "by at most 5 ticks of tardiness whatever the context-switch cost (range −4 to +5). For "
      "every migration cost of at least 0.1 work units, however, TA-EDF had higher total "
      "tardiness and a longer makespan than EDF in all 96 matched configurations, with "
      "differences of +1 to +365 ticks in tardiness and +2 to +121 ticks in makespan. At "
      "migration costs of 0.25 and above it also missed three to four more deadlines than EDF in "
      "Burst VR, and at 0.5 with DVFS enabled one more in HOT Thermal."),
("table", "tab:sens"),
("figure", "fig:sens"),
("p", "The thermal side of the trade-off persisted in three of the four workloads: in Normal, "
      "Sustained and HOT, TA-EDF's simulated peak stayed 0.99–2.49 °C below EDF's at every cost. "
      "In Burst VR, once migrations cost anything, TA-EDF's peak was 0.70–3.93 °C *above* EDF's; "
      "we did not investigate the mechanism behind this reversal. The zero-overhead rows of this "
      "experiment reproduced the main benchmark exactly (64 runs × 16 metrics)."),
("h2", "sec:res-eevdf", "EEVDF-Inspired Policy on One and Two Cores"),
("p", "On a single core the EEVDF-inspired policy never dispatched an ineligible task, and the "
      "largest lag observed was between 0.73 and 0.94 slices, consistent with the one-quantum "
      "bound of the original algorithm [@stoica1995]. On two cores it dispatched ineligible tasks "
      "in 4, 15, 27 and 56 ticks of the Normal, Burst, Sustained and HOT workloads (DVFS enabled), "
      "and the largest lag reached 2.26, 3.55, 7.67 and 22.59 slices respectively. This "
      "behaviour follows from combining a global queue, a work-conserving rule and weight ratios "
      "of up to 87:1, under which a heavy task's fair share can exceed one core; it mirrors the "
      "infeasible-weight problem described for symmetric multiprocessors [@chandra2000]. The "
      "two-core results of this policy therefore carry no fairness guarantee."),

# ---------------------------------------------------------------- VII
("h1", "sec:discussion", "Discussion"),
("p", "*Why ThermOS-VR equals FCFS.* The score in {{eq:score}} can only choose between identical "
      "idle cores, and its deadline term is constant across them. With FCFS ordering and no "
      "preemption, the start and finish time of every task is fixed before any core is chosen. "
      "Because the cores are identical, swapping two tasks between them changes only which core "
      "carries which heat trace, and every aggregate metric is symmetric in the two cores. A "
      "thermal score can matter only when cores differ in temperature in a way that changes "
      "future speed, which in this model requires DVFS, and even then the FCFS order leaves "
      "little room for it to act."),
("p", "*Why DVFS dominates the thermal results.* The thermal update is linear and the cores are "
      "identical, so with a fixed frequency the total heat a workload produces is fixed by its "
      "work, and the average temperature can change only through the timing of that work. "
      "Placement can redistribute heat between cores, which changes the peak and the "
      "threshold-based counts, but it cannot reduce the total. Lowering the frequency reduces the "
      "heat per tick quadratically while reducing progress linearly, which is why the governor "
      "lowered peaks and removed HOT samples at the cost of longer makespans."),
("p", "*Why migration cost reverses the TA-EDF comparison.* TA-EDF lowers the peak by moving the "
      "earliest-deadline task to whichever core is cooler; on two busy cores this amounts to "
      "swapping tasks when their core temperatures cross, which is consistent with the high "
      "migration counts observed. When migration is free these swaps "
      "only even out the heat. When each swap costs work, the swaps lengthen every affected "
      "task, the additional work feeds back into slack and later decisions, and the policy loses "
      "the small responsiveness margin it had. The result suggests that, in a design like "
      "TA-EDF, thermal migration should be rate-limited or made sticky, for example by migrating "
      "only when the temperature difference exceeds a threshold; we have not evaluated such a "
      "variant."),
("p", "*Responsiveness versus simulated heat.* Round Robin and the EEVDF-inspired policy "
      "illustrate that a low threshold count is not a free improvement: both spread heavy work "
      "over time, which lowers peaks and threshold exposure in some workloads, but both have the "
      "longest waits and miss every deadline in the overloaded workloads. Among the policies "
      "that keep responsiveness competitive, the deadline-driven order of EDF provided the "
      "consistent gain, and the thermal refinements studied here offered at most a small "
      "simulated peak reduction whose cost depends on migration overhead."),
("p", "*Threats to validity.* Internal validity concerns whether the implementation does what "
      "is described; we addressed it with hand-derived unit tests, an independent reference "
      "implementation of EDF, exact reproduction of the earlier prototype for four policies, "
      "and recomputation of every metric from raw traces ({{tab:verify}}). Some quantities in "
      "this paper (the EEVDF lag values, the hold-back case analysis and the inter-core "
      "temperature difference) come from analysis scripts that read the simulator rather than "
      "from the benchmark CSV columns; those scripts are part of the paper's evidence package. "
      "Construct validity is limited by the metrics themselves: simulated degrees, model heat "
      "units and ticks are not physical quantities, and threshold counts depend on the chosen "
      "60 °C and 70 °C boundaries. External validity is limited by the two identical cores, the "
      "six-task synthetic workloads and the absence of periodic frame deadlines. Conclusion "
      "validity is limited because every configuration was run once: the reported differences "
      "are deterministic outcomes of this model, and several of them, such as peak differences "
      "of a few hundredths of a degree, are too small to carry weight [@hoefler2015]."),

# ---------------------------------------------------------------- VIII
("h1", "sec:limits", "Limitations and Future Work"),
("ul", [
    "*Simulation only.* No kernel was modified and no device was measured; temperatures, heat and "
    "throttling counts are outputs of an uncalibrated model, and no power, energy or battery "
    "result exists.",
    "*Identical cores.* The \"Performance\" and \"Efficiency\" labels do not model heterogeneous "
    "capacity, and there is no heat transfer between cores, so capacity- and energy-aware "
    "scheduling such as EAS could not be evaluated.",
    "*Workloads.* Four hand-specified workloads of six one-shot tasks are not representative of "
    "real AR/VR pipelines, contain no periodic frame deadlines, and are partly infeasible.",
    "*Determinism.* Each configuration was run once; with no randomised workloads or repeated "
    "trials, no confidence intervals or significance tests are possible.",
    "*Time model.* Decisions happen at one-tick granularity, the tick has no physical length, "
    "and partially used final ticks are counted as fully busy.",
    "*Overheads.* The main benchmark assumes free migrations and context switches; the "
    "sensitivity costs are hypothetical and charged only to the incoming task.",
    "*Policy fidelity.* The EEVDF-inspired policy omits per-CPU queues, load balancing and "
    "sleep handling, and the TA-EDF hold-back rule was never exercised.",
]),
("p", "Future work should introduce periodic frame-task workloads with feasible deadlines, "
      "seeded random task sets with repeated runs and confidence intervals, asymmetric cores with "
      "a power model so that capacity- and energy-aware policies can be compared, thermal "
      "coupling between cores, trace-driven workloads from an open XR system such as ILLIXR "
      "[@huzaifa2021], a sticky variant of TA-EDF, and finally validation on real hardware."),

# ---------------------------------------------------------------- IX
("h1", "sec:conclusion", "Conclusion"),
("p", "We re-evaluated a thermal-aware scheduling heuristic for AR/VR-inspired workloads in a "
      "shared, verified simulator and compared it with classical, deadline-driven and "
      "weighted-fair baselines. Within this model, three conclusions are supported. First, the "
      "original ThermOS-VR score behaves exactly like FCFS once both use the same governor, so "
      "its earlier thermal benefit came from DVFS. Second, deadline-driven ordering gave the "
      "lowest or tied-lowest waiting time and tardiness throughout. Third, TA-EDF's "
      "coolest-core placement lowered the simulated peak relative to EDF, but only through "
      "frequent migrations, and once those migrations cost as little as 0.1 work units it was "
      "less responsive than EDF in every matched configuration. These findings concern a "
      "deterministic model with identical cores; testing them on heterogeneous, measured "
      "hardware remains future work."),
]

# ------------------------------------------------------------------ figures
FIG_ROOT_V2 = "06_Figures/v2_modern_baselines"
FIGURES = {
    "fig:arch": dict(path="07_Report/thermos_vr_ieee_paper/figures/fig_architecture.png",
        wide=False, width_in=3.3,
        caption="Simulator architecture and per-tick order. The same engine, thermal model, DVFS "
                "governor and metrics are used for all eight policies; the overhead model is used "
                "only in the sensitivity experiment."),
    "fig:wait": dict(path=f"{FIG_ROOT_V2}/hysteresis_waiting_time.png", wide=True, width_in=6.9,
        caption="Average waiting time (ticks), DVFS enabled, one deterministic run per policy and "
                "workload. FCFS and ThermOS-VR are identical by construction; ties occur in Normal VR."),
    "fig:tard": dict(path=f"{FIG_ROOT_V2}/hysteresis_total_tardiness.png", wide=True, width_in=6.9,
        caption="Total tardiness (ticks), DVFS enabled. Tasks are not dropped after missing a "
                "deadline; Burst, Sustained and HOT are partly infeasible on two cores."),
    "fig:ge60": dict(path=f"{FIG_ROOT_V2}/hysteresis_core_ticks_above_60c.png", wide=True, width_in=6.9,
        caption="Core-ticks at or above the 60 °C model threshold, DVFS enabled. Values are "
                "simulated by the simplified thermal model; Normal and Burst never reach 60 °C."),
    "fig:peak": dict(path=f"{FIG_ROOT_V2}/hysteresis_peak_temperature.png", wide=True, width_in=6.9,
        caption="Peak simulated temperature (model °C), DVFS enabled. Dot plot because the axis does "
                "not start at zero; differences are small and come from single deterministic runs."),
    "fig:trace": dict(path=f"{FIG_ROOT_V2}/hysteresis_hot_temperature_trace.png", wide=True,
        width_in=6.4,
        caption="Per-core simulated temperature over time (model °C), HOT workload, DVFS enabled, "
                "for FCFS, ThermOS-VR, EDF and TA-EDF. The FCFS and ThermOS-VR panels are identical "
                "by construction; the dashed line is the governor's first threshold."),
    "fig:sens": dict(path="07_Report/thermos_vr_ieee_paper/figures/fig_sensitivity_tardiness.png",
        wide=False, width_in=3.4,
        caption="TA-EDF minus EDF total tardiness versus migration cost (context-switch cost 0), "
                "matched on workload and DVFS setting. Positive values mean TA-EDF is later. "
                "Costs are hypothetical simulated work units, not measured latencies."),
}
