"""
Scheduling-overhead extension of the v2 engine (sensitivity experiments only).

sim_engine.Simulator is NOT modified; with both costs set to 0 this class
behaves exactly like it (tested in tests/test_overhead.py and checked
against the original benchmark by verify_sensitivity.py).

Overhead model
--------------
A *dispatch event* happens when a task runs in tick t but did not run on
the same core in tick t-1. Every dispatch event is classified exactly once:

    first dispatch   the task has never run before          -> no charge
    migration        the task last ran on a different core  -> migration_cost
    resume           the task last ran on this same core,
                     but not in the previous tick           -> context_switch_cost

A migration is never also charged as a context switch (no double charge).
A task that keeps running on the same core is never charged.

The charge is added to the task's remaining work at the moment of dispatch,
so the core spends that capacity on overhead before the task makes
progress. The core counts as busy and heats at the task's workload
intensity while doing so.
"""

from sim_engine import Simulator


class OverheadSimulator(Simulator):

    def __init__(self, processes, cores, policy, governor,
                 migration_cost=0.0, context_switch_cost=0.0, max_time=10000):
        super().__init__(processes, cores, policy, governor, max_time=max_time)
        self.migration_cost = migration_cost
        self.context_switch_cost = context_switch_cost

    def _reset_processes(self):
        super()._reset_processes()
        for process in self.processes:
            process.migration_events = 0
            process.resume_events = 0
            process.overhead_work = 0.0

    def _apply(self, mapping, t):
        ran_last_tick_on = {
            id(core.current_process): core.core_id
            for core in self.cores
            if core.current_process is not None
        }
        last_core = {id(p): p.last_core_id for p in self.processes}
        never_ran = {id(p) for p in self.processes if p.busy_ticks == 0}

        super()._apply(mapping, t)

        for core_id, task in mapping.items():
            if task is None:
                continue
            if ran_last_tick_on.get(id(task)) == core_id:
                continue                       # kept running on its core
            if id(task) in never_ran:
                continue                       # first dispatch: not charged

            if last_core[id(task)] != core_id:
                cost = self.migration_cost
                task.migration_events += 1
            else:
                cost = self.context_switch_cost
                task.resume_events += 1

            task.remaining_time += cost
            task.overhead_work += cost
