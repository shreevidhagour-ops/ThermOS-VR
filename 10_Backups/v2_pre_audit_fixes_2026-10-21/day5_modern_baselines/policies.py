"""
Scheduling policies for the ThermOS-VR v2 unified engine.

Every policy implements

    schedule(t, ready, cores) -> {core_id: task or None}

where `ready` holds arrived, unfinished tasks that are NOT currently on
a core, in workload (PID) order. The returned mapping is the full
assignment for the tick [t, t+1). A policy preempts a running task by
not mapping it to any core.

Deadlines are absolute times. A task "misses" its deadline when its
completion time is greater than its deadline. No policy drops late
tasks: every task runs to completion so that all metrics are defined
for every task (soft real-time interpretation).
"""

from collections import deque

from sim_engine import REFERENCE_FREQUENCY


# ============================================================
# SHARED HELPERS
# ============================================================

def current_mapping(cores):
    return {core.core_id: core.current_process for core in cores}


def lowest_id_core(task, candidate_cores, t):
    """Thermally blind core choice: lowest core ID."""
    return min(candidate_cores, key=lambda core: core.core_id)


def edf_key(task):
    """EDF order: earliest absolute deadline, then earliest arrival, then lowest PID."""
    return (task.deadline, task.arrival_time, task.pid)


def dispatch_non_preemptive(t, ready, cores, order_key, choose_core,
                            stop_when_no_core=True):
    """
    Running tasks keep their cores until they finish. Idle cores are
    filled from the ready tasks in `order_key` order.
    """
    mapping = current_mapping(cores)

    for task in sorted(ready, key=order_key):
        idle = [c for c in cores if mapping[c.core_id] is None]

        if not idle:
            break

        core = choose_core(task, idle, t)

        if core is None:
            if stop_when_no_core:
                break
            continue

        mapping[core.core_id] = task

    return mapping


def dispatch_preemptive(t, ready, cores, order_key, choose_core):
    """
    Global preemptive dispatch at tick boundaries: the m best tasks
    (m = number of cores) among running + ready tasks run. A selected
    task that is already running stays on its core (no needless
    migration); other selected tasks take freed cores.
    """
    running = [c.current_process for c in cores if c.current_process]
    selected = sorted(ready + running, key=order_key)[:len(cores)]
    selected_ids = {id(task) for task in selected}

    mapping = {
        core.core_id: (
            core.current_process
            if core.current_process is not None
            and id(core.current_process) in selected_ids
            else None
        )
        for core in cores
    }

    placed = {id(task) for task in mapping.values() if task is not None}

    for task in selected:
        if id(task) in placed:
            continue

        free = [c for c in cores if mapping[c.core_id] is None]
        core = choose_core(task, free, t)
        mapping[core.core_id] = task
        placed.add(id(task))

    return mapping


# ============================================================
# TRADITIONAL BASELINES (same semantics as v1)
# ============================================================

class FCFSPolicy:
    """Non-preemptive FCFS. Order: (arrival, PID). Core: lowest idle ID."""

    name = "FCFS"
    preemptive = False

    def schedule(self, t, ready, cores):
        return dispatch_non_preemptive(
            t, ready, cores,
            order_key=lambda p: (p.arrival_time, p.pid),
            choose_core=lowest_id_core,
        )


class PriorityPolicy:
    """Non-preemptive priority. Lower number = higher priority.
    Order: (priority, arrival, PID). Core: lowest idle ID."""

    name = "Priority"
    preemptive = False

    def schedule(self, t, ready, cores):
        return dispatch_non_preemptive(
            t, ready, cores,
            order_key=lambda p: (p.priority, p.arrival_time, p.pid),
            choose_core=lowest_id_core,
        )


class RoundRobinPolicy:
    """
    Round Robin, quantum = 1 tick, single global FIFO queue (as in v1).

    At each tick boundary, tasks whose quantum expired are appended to
    the queue (in core-ID order), then newly arrived tasks are appended
    (in PID order), then idle cores take tasks from the queue head in
    core-ID order.
    """

    name = "Round Robin"
    preemptive = True

    def reset(self, processes, cores):
        self.queue = deque()

    def schedule(self, t, ready, cores):
        for core in cores:
            if core.current_process is not None:
                self.queue.append(core.current_process)

        queued = {id(task) for task in self.queue}

        for task in ready:
            if id(task) not in queued:
                self.queue.append(task)

        mapping = {}

        for core in sorted(cores, key=lambda c: c.core_id):
            mapping[core.core_id] = (
                self.queue.popleft() if self.queue else None
            )

        return mapping


class ThermOSVRv1Policy:
    """
    Faithful port of ThermOSVRScheduler (day3_thermos_scheduler/scheduler.py).

    Order: FCFS (arrival, PID), non-preemptive.
    Core: highest score among idle, non-CRITICAL cores, where
        score = thermal_score + core_type_score + deadline_score.
    Ties go to the first core in core-list order (strict '>').
    Running tasks on a CRITICAL core are evicted (unreachable with the
    default thermal parameters).

    The deadline score is identical for every candidate core (bug B4), so
    it never changes the choice. It is kept for fidelity.
    """

    name = "ThermOS-VR"
    preemptive = False

    @staticmethod
    def score(task, core, t):
        thermal_score = (100 - core.temperature) * 1.5
        state = core.get_thermal_state()

        if state == "HOT":
            thermal_score -= 50
        elif state == "WARM":
            thermal_score -= 10

        if task.workload_intensity >= 70:
            core_type_score = 20 if core.core_type == "Performance" else 10
        elif task.workload_intensity <= 40:
            core_type_score = 20 if core.core_type == "Efficiency" else 10
        else:
            core_type_score = 15

        if task.deadline - t <= task.remaining_time:
            deadline_score = 30
        else:
            deadline_score = 15

        return thermal_score + core_type_score + deadline_score

    def choose_core(self, task, idle_cores, t):
        eligible = [
            c for c in idle_cores if c.get_thermal_state() != "CRITICAL"
        ]

        best_core, best_score = None, float("-inf")

        for core in eligible:
            s = self.score(task, core, t)
            if s > best_score:
                best_core, best_score = core, s

        return best_core

    def schedule(self, t, ready, cores):
        # Thermal protection: evict tasks from CRITICAL cores.
        evicted = []

        for core in cores:
            if (
                core.current_process is not None
                and core.get_thermal_state() == "CRITICAL"
            ):
                evicted.append(core.current_process)
                core.release_process()

        candidates = list(ready) + evicted

        return dispatch_non_preemptive(
            t, candidates, cores,
            order_key=lambda p: (p.arrival_time, p.pid),
            choose_core=self.choose_core,
            stop_when_no_core=False,
        )


# ============================================================
# EDF
# ============================================================

class EDFNonPreemptivePolicy:
    """
    Non-preemptive global EDF.

    Order: (absolute deadline, arrival, PID). A dispatched task runs to
    completion. Core: lowest idle core ID (thermally blind).
    """

    name = "EDF-NP"
    preemptive = False

    def schedule(self, t, ready, cores):
        return dispatch_non_preemptive(
            t, ready, cores,
            order_key=edf_key,
            choose_core=lowest_id_core,
        )


class GlobalEDFPolicy:
    """
    Preemptive global EDF (G-EDF).

    At every tick boundary the m tasks with the earliest absolute
    deadlines among running and ready tasks run (m = number of cores).
    Ties: earlier arrival, then lower PID. A task that keeps its slot
    stays on its core; newly selected tasks take the lowest free core
    ID (thermally blind). Preemption happens only at tick boundaries.
    Late tasks keep their original deadline and continue to run.
    """

    name = "EDF"
    preemptive = True

    def schedule(self, t, ready, cores):
        return dispatch_preemptive(
            t, ready, cores,
            order_key=edf_key,
            choose_core=lowest_id_core,
        )


class ThermalAwareEDFPolicy:
    """
    Thermal-aware EDF (TA-EDF), our own proposed policy. It is not an
    established or Linux scheduler.

    Task order is identical to G-EDF. Two thermal mechanisms are added:

    1. Deadline-aware core selection. Laxity
           slack = deadline - t - remaining_work
       is the number of ticks the task can still wait if it runs at the
       reference speed. A task is URGENT if slack <= urgency_slack.
         - Urgent task:     core with the highest current frequency
                            (fastest progress), then the coolest core.
         - Non-urgent task: coolest core, then the highest frequency.
       Further ties: the task's current core (avoids migration), then
       the lowest core ID.

    2. Thermal idle insertion. A core at or above guard_temperature
       (1 °C below the DVFS throttle threshold of 60 °C) accepts only
       tasks with slack < defer_slack. Tasks with more slack are held
       back, so the core can cool before DVFS reduces its frequency.
       Because a held task's slack falls by one per tick, the delay is
       bounded: it is dispatched at the latest when its slack drops
       below defer_slack.

    The policy considers candidates in EDF order until all cores are
    filled, skipping held-back tasks.
    """

    name = "TA-EDF"
    preemptive = True

    def __init__(self, urgency_slack=2.0, guard_temperature=59.0,
                 defer_slack=10.0):
        if defer_slack <= urgency_slack:
            raise ValueError("defer_slack must exceed urgency_slack")
        self.urgency_slack = urgency_slack
        self.guard_temperature = guard_temperature
        self.defer_slack = defer_slack

    @staticmethod
    def slack(task, t):
        return task.deadline - t - task.remaining_time

    def choose_core(self, task, free_cores, t):
        current = task.last_core_id

        if self.slack(task, t) <= self.urgency_slack:
            key = lambda c: (-c.frequency, c.temperature,
                             c.core_id != current, c.core_id)
        else:
            key = lambda c: (c.temperature, -c.frequency,
                             c.core_id != current, c.core_id)

        return min(free_cores, key=key)

    def schedule(self, t, ready, cores):
        running = [c.current_process for c in cores if c.current_process]
        candidates = sorted(ready + running, key=edf_key)

        mapping = {core.core_id: None for core in cores}

        for task in candidates:
            free = [c for c in cores if mapping[c.core_id] is None]

            if not free:
                break

            core = self.choose_core(task, free, t)

            # A deferrable task is never urgent, so `core` is already the
            # coolest free core: if it is above the guard, all are.
            if (
                core.temperature >= self.guard_temperature
                and self.slack(task, t) >= self.defer_slack
            ):
                continue  # held back this tick (thermal idle insertion)

            mapping[core.core_id] = task

        return mapping


# ============================================================
# EEVDF-INSPIRED
# ============================================================

# Subset of the Linux sched_prio_to_weight table (kernel/sched/core.c).
NICE_TO_WEIGHT = {-10: 9548, -5: 3121, 0: 1024, 5: 335, 10: 110}
NICE_0_WEIGHT = 1024

# Workload priority (1 = highest ... 5 = lowest) -> nice value.
PRIORITY_TO_NICE = {1: -10, 2: -5, 3: 0, 4: 5, 5: 10}


class EEVDFInspiredPolicy:
    """
    EEVDF-inspired weighted fair scheduler (simplified). This is NOT the
    Linux kernel implementation.

    Modeled concepts (after Stoica & Abdel-Wahab 1995 and Linux >= 6.6):
      - weight w from priority via the nice-to-weight table
      - virtual runtime v, advanced by executed wall time * 1024 / w
      - V = weighted average virtual runtime of all runnable tasks
      - lag = w * (V - v); a task is ELIGIBLE when lag >= 0 (v <= V)
      - virtual deadline vd = v + base_slice * 1024 / w, renewed each
        time a request (slice) is consumed
      - pick: eligible tasks in (vd, arrival, PID) order
      - new tasks are placed at v = V (zero lag)

    Simplifications:
      - one global runqueue shared by both cores (Linux uses per-CPU
        runqueues plus load balancing)
      - base_slice = 1 tick; re-pick at every tick boundary
      - if fewer eligible tasks than cores, the remaining cores take the
        earliest-vd ineligible tasks (work-conserving)
      - no sleep/wakeup, so no lag decay or wakeup preemption is modeled
      - task deadlines and temperatures are NOT used
      - core choice: keep a running task on its core, else lowest free ID
    """

    name = "EEVDF-inspired"
    preemptive = True

    def __init__(self, base_slice=1.0):
        self.base_slice = base_slice

    def reset(self, processes, cores):
        self.v = {}
        self.vd = {}
        self.slice_used = {}
        self.V = 0.0

    @staticmethod
    def weight(task):
        return NICE_TO_WEIGHT[PRIORITY_TO_NICE[task.priority]]

    def _new_request(self, task):
        self.vd[task.pid] = (
            self.v[task.pid]
            + self.base_slice * NICE_0_WEIGHT / self.weight(task)
        )
        self.slice_used[task.pid] = 0.0

    def average_vruntime(self, runnable):
        total_weight = sum(self.weight(p) for p in runnable)
        return sum(
            self.weight(p) * self.v[p.pid] for p in runnable
        ) / total_weight

    def schedule(self, t, ready, cores):
        # Charge tasks that ran during the previous tick.
        for core in cores:
            task = core.current_process
            if task is not None:
                self.v[task.pid] += NICE_0_WEIGHT / self.weight(task)
                self.slice_used[task.pid] += 1.0

        running = [c.current_process for c in cores if c.current_process]
        runnable = ready + running

        if not runnable:
            return current_mapping(cores)

        # Place newly arrived tasks at zero lag.
        known = [p for p in runnable if p.pid in self.v]
        if known:
            self.V = self.average_vruntime(known)

        for task in runnable:
            if task.pid not in self.v:
                self.v[task.pid] = self.V
                self._new_request(task)

        for task in runnable:
            if self.slice_used[task.pid] >= self.base_slice - 1e-12:
                self._new_request(task)

        self.V = self.average_vruntime(runnable)

        def pick_key(p):
            eligible = self.v[p.pid] <= self.V + 1e-12
            return (not eligible, self.vd[p.pid], p.arrival_time, p.pid)

        return dispatch_preemptive(
            t, ready, cores,
            order_key=pick_key,
            choose_core=lowest_id_core,
        )


# ============================================================
# REGISTRY
# ============================================================

BENCHMARK_POLICIES = [
    FCFSPolicy,
    PriorityPolicy,
    RoundRobinPolicy,
    ThermOSVRv1Policy,
    EDFNonPreemptivePolicy,
    GlobalEDFPolicy,
    ThermalAwareEDFPolicy,
    EEVDFInspiredPolicy,
]
