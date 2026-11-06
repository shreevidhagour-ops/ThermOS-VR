"""
Overhead model (overhead_engine.py): hand-verified charging rules, and
equivalence with the unmodified engine when both costs are zero.
"""

import unittest

from testutil import task, by_pid, executed_sequence, create_cores
from sim_engine import Simulator, NoDVFSGovernor, GOVERNORS
from overhead_engine import OverheadSimulator
from metrics_v2 import compute_metrics
from policies import BENCHMARK_POLICIES, GlobalEDFPolicy
import workloads as W


class ScriptedPolicy:
    """Places the single task on a scripted core per tick (None = wait)."""

    def __init__(self, script):
        self.script = script

    def schedule(self, t, ready, cores):
        runnable = ready + [c.current_process for c in cores if c.current_process]
        core_id = self.script.get(t)
        return {c.core_id: (runnable[0] if runnable and c.core_id == core_id else None)
                for c in cores}


def run_overhead(policy, processes, cores=2, mig=0.0, cs=0.0):
    sim = OverheadSimulator(processes, create_cores()[:cores], policy,
                            NoDVFSGovernor(), migration_cost=mig,
                            context_switch_cost=cs)
    return sim, sim.run()


class OverheadChargingTests(unittest.TestCase):

    def test_resume_after_preemption_charged_once(self):
        """1 core, G-EDF, A(0,3,dl10) B(1,2,dl4) C(2,1,dl5), cs = 0.5.
        t0 A (first dispatch, free). t1 B preempts A (B first, free).
        t3 C first dispatch (free). t4 A resumes on the same core: +0.5,
        so A has 2.5 units left -> runs t4, t5, t6 -> completes at 7.
        One resume event; no migrations."""
        tasks = [task(1, 0, 3, 10), task(2, 1, 2, 4), task(3, 2, 1, 5)]
        sim, trace = run_overhead(GlobalEDFPolicy(), tasks, cores=1, cs=0.5)
        p = by_pid(sim.processes)
        self.assertEqual(executed_sequence(trace), [1, 2, 2, 3, 1, 1, 1])
        self.assertEqual(p[1].completion_time, 7)
        self.assertEqual((p[1].resume_events, p[1].migration_events), (1, 0))
        self.assertAlmostEqual(sum(x.overhead_work for x in sim.processes), 0.5)
        self.assertEqual((p[2].overhead_work, p[3].overhead_work), (0.0, 0.0))

    def test_continuous_migration_charged(self):
        """Task burst 2 alternates core 1 (t0), core 2 (t1), core 1 (t2);
        mig = 0.25. t0: 2 -> 1. t1: migration +0.25 -> 1.25 -> 0.25.
        t2: migration +0.25 -> 0.5 -> done at 3. Two migration events."""
        policy = ScriptedPolicy({0: 1, 1: 2, 2: 1})
        sim, trace = run_overhead(policy, [task(1, 0, 2, 9)], mig=0.25, cs=0.5)
        p = sim.processes[0]
        self.assertEqual(p.completion_time, 3)
        self.assertEqual((p.migration_events, p.resume_events), (2, 0))
        self.assertAlmostEqual(p.overhead_work, 0.5)

    def test_migration_after_gap_not_double_charged(self):
        """Core 1 at t0, waits at t1, core 2 at t2 and t3; mig = 0.25, cs = 0.5.
        t2 is a migration AND a resume after a gap: charged ONLY as a
        migration (+0.25). Remaining: 1 -> 1.25 -> 0.25 -> done at 4."""
        policy = ScriptedPolicy({0: 1, 2: 2, 3: 2})
        sim, trace = run_overhead(policy, [task(1, 0, 2, 9)], mig=0.25, cs=0.5)
        p = sim.processes[0]
        self.assertEqual(executed_sequence(trace, 1), [1, "", "", ""])
        self.assertEqual(executed_sequence(trace, 2), ["", "", 1, 1])
        self.assertEqual(p.completion_time, 4)
        self.assertEqual((p.migration_events, p.resume_events), (1, 0))
        self.assertAlmostEqual(p.overhead_work, 0.25)
        self.assertEqual(p.waiting_time, 1)

    def test_first_dispatch_and_continuation_free(self):
        """Non-preemptive run on one core: no events, no overhead."""
        sim, _ = run_overhead(GlobalEDFPolicy(), [task(1, 0, 3, 9)], cores=1,
                              mig=0.5, cs=0.5)
        p = sim.processes[0]
        self.assertEqual((p.completion_time, p.overhead_work), (3, 0.0))


class ZeroOverheadEquivalenceTests(unittest.TestCase):

    def test_zero_cost_equals_unmodified_engine(self):
        """All 8 policies x 4 workloads x 2 DVFS settings: identical metrics
        and identical per-tick traces."""
        workloads = [W.create_vr_workload, W.create_burst_vr_workload,
                     W.create_sustained_thermal_workload,
                     W.create_hot_thermal_workload]
        for governor in ("off", "hysteresis"):
            for workload in workloads:
                for policy_class in BENCHMARK_POLICIES:
                    with self.subTest(governor=governor, policy=policy_class.name,
                                      workload=workload.__name__):
                        a = Simulator(workload(), create_cores(), policy_class(),
                                      GOVERNORS[governor]())
                        b = OverheadSimulator(workload(), create_cores(),
                                              policy_class(), GOVERNORS[governor]())
                        ta, tb = a.run(), b.run()
                        self.assertEqual(ta, tb)
                        self.assertEqual(compute_metrics(a.processes, ta, 2),
                                         compute_metrics(b.processes, tb, 2))


if __name__ == "__main__":
    unittest.main()
