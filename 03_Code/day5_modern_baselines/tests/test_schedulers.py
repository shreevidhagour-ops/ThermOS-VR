"""
Small, hand-verifiable task sets for the v2 policies and engine.
Expected values are derived by hand in each docstring.
"""

import unittest

from testutil import task, run, by_pid, executed_sequence, create_cores
from sim_engine import Simulator, SchedulingError, NoDVFSGovernor
from metrics_v2 import compute_metrics
from policies import (
    FCFSPolicy,
    RoundRobinPolicy,
    EDFNonPreemptivePolicy,
    GlobalEDFPolicy,
    ThermalAwareEDFPolicy,
    EEVDFInspiredPolicy,
)


def three_task_set():
    # A(arr 0, burst 3, dl 10), B(arr 1, burst 2, dl 4), C(arr 2, burst 1, dl 5)
    return [task(1, 0, 3, 10), task(2, 1, 2, 4), task(3, 2, 1, 5)]


class EngineTests(unittest.TestCase):

    def test_fcfs_waiting_and_utilization_one_core(self):
        """1 core, A(0,2) B(0,2): A runs 0-2, B runs 2-4.
        Waiting A=0, B=2. Utilization 4/4 = 100 %."""
        sim, trace = run(FCFSPolicy(), [task(1, 0, 2, 9), task(2, 0, 2, 9)], 1)
        p = by_pid(sim.processes)
        self.assertEqual((p[1].completion_time, p[2].completion_time), (2, 4))
        self.assertEqual((p[1].waiting_time, p[2].waiting_time), (0, 2))
        m = compute_metrics(sim.processes, trace, 1)
        self.assertEqual(m["Core-time Utilization (%)"], 100.0)
        self.assertEqual(len(trace), 4)  # one row per core per tick

    def test_utilization_two_cores_one_task(self):
        """2 cores, one task of burst 2: busy 2 of 2*2 core-ticks = 50 %."""
        sim, trace = run(FCFSPolicy(), [task(1, 0, 2, 9)], 2)
        m = compute_metrics(sim.processes, trace, 2)
        self.assertEqual(m["Core-time Utilization (%)"], 50.0)

    def test_engine_rejects_double_assignment(self):
        """Bug B1 regression: one task on two cores must be refused."""

        class BadPolicy:
            def schedule(self, t, ready, cores):
                return {c.core_id: ready[0] if ready else None for c in cores}

        cores = create_cores()
        sim = Simulator([task(1, 0, 3, 9)], cores, BadPolicy(), NoDVFSGovernor())
        with self.assertRaises(SchedulingError):
            sim.run()

    def test_dvfs_slows_execution(self):
        """1 core starting at 61 °C, burst 2, w=100, hysteresis governor.
        Tick 0 runs at 2.5 GHz (work 1.0); T -> 61.28, governor -> 2.2.
        Ticks 1-2 run at 2.2 GHz (work 0.88 each; T stays ~61.3 > 58).
        Remaining 1 - 0.88 = 0.12 after tick 1, done after tick 2 -> C=3."""
        sim, trace = run(FCFSPolicy(), [task(1, 0, 2, 9, intensity=100)], 1,
                         governor="hysteresis", initial_temperature=61.0)
        self.assertEqual(sim.processes[0].completion_time, 3)
        self.assertEqual([r["frequency_used"] for r in trace], [2.5, 2.2, 2.2])
        m = compute_metrics(sim.processes, trace, 1)
        self.assertEqual(m["Throttled Busy Core-ticks"], 2)


class EDFTests(unittest.TestCase):

    def test_non_preemptive_edf_hand_example(self):
        """1 core. t0: only A -> A runs 0-3 (non-preemptive).
        t3: B(dl 4) before C(dl 5) -> B runs 3-5, C runs 5-6.
        Completions A3 B5 C6; misses B (5>4), C (6>5) = 2.
        Waiting A0, B2 (t1,t2), C3 (t2,t3,t4)."""
        sim, _ = run(EDFNonPreemptivePolicy(), three_task_set(), 1)
        p = by_pid(sim.processes)
        self.assertEqual([p[i].completion_time for i in (1, 2, 3)], [3, 5, 6])
        self.assertEqual([p[i].waiting_time for i in (1, 2, 3)], [0, 2, 3])
        self.assertEqual(sum(x.deadline_missed for x in sim.processes), 2)

    def test_preemptive_edf_hand_example(self):
        """1 core. t0 A runs. t1 B arrives (dl 4 < 10): preempts A, runs
        t1-t2, done at 3. t3: C(dl 5) before A(dl 10): C runs t3, done at 4.
        A runs t4-t5, done at 6. Misses 0. Waiting A3, B0, C1.
        Sequence on the core: A B B C A A."""
        sim, trace = run(GlobalEDFPolicy(), three_task_set(), 1)
        p = by_pid(sim.processes)
        self.assertEqual(executed_sequence(trace), [1, 2, 2, 3, 1, 1])
        self.assertEqual([p[i].completion_time for i in (1, 2, 3)], [6, 3, 4])
        self.assertEqual([p[i].waiting_time for i in (1, 2, 3)], [3, 0, 1])
        self.assertEqual([p[i].response_time for i in (1, 2, 3)], [0, 0, 1])
        self.assertEqual(sum(x.deadline_missed for x in sim.processes), 0)
        self.assertEqual(p[1].preemptions, 1)

    def test_tie_break_lower_pid(self):
        """Equal deadline and arrival: lower PID first."""
        sim, trace = run(GlobalEDFPolicy(), [task(2, 0, 1, 5), task(1, 0, 1, 5)], 1)
        self.assertEqual(executed_sequence(trace), [1, 2])

    def test_tie_break_earlier_arrival(self):
        """Blocker R(pid 9) runs t0-t1 (dl 1, misses). At t2 P(pid 5, arr 0)
        and Q(pid 4, arr 1) share dl 8: earlier arrival P runs first,
        despite its higher PID."""
        tasks = [task(9, 0, 2, 1), task(5, 0, 1, 8), task(4, 1, 1, 8)]
        sim, trace = run(EDFNonPreemptivePolicy(), tasks, 1)
        self.assertEqual(executed_sequence(trace), [9, 9, 5, 4])

    def test_global_edf_two_cores_no_needless_migration(self):
        """2 cores. t0: A(dl20) -> core1, B(dl21) -> core2.
        t1: C(dl 2) arrives; latest deadline B is preempted; C takes core 2;
        A stays on core 1. t2: B resumes on the free core 2 (no migration).
        Completions: A4, C2, B5."""
        tasks = [task(1, 0, 4, 20), task(2, 0, 4, 21), task(3, 1, 1, 2)]
        sim, trace = run(GlobalEDFPolicy(), tasks, 2)
        p = by_pid(sim.processes)
        self.assertEqual(executed_sequence(trace, 1), [1, 1, 1, 1, ""])
        self.assertEqual(executed_sequence(trace, 2), [2, 3, 2, 2, 2])
        self.assertEqual([p[i].completion_time for i in (1, 2, 3)], [4, 5, 2])
        self.assertEqual((p[1].preemptions, p[2].preemptions), (0, 1))
        self.assertEqual(sum(x.migrations for x in sim.processes), 0)

    def test_late_task_continues_and_counts_tardiness(self):
        """A(arr 0, burst 5, dl 2) is not dropped: completes at 5,
        misses, tardiness 3."""
        sim, trace = run(GlobalEDFPolicy(), [task(1, 0, 5, 2)], 1)
        m = compute_metrics(sim.processes, trace, 1)
        self.assertEqual(sim.processes[0].completion_time, 5)
        self.assertEqual(m["Deadline Misses"], 1)
        self.assertEqual(m["Total Tardiness"], 3)

    def test_idle_core_until_arrival(self):
        """Task arriving at t=3 starts at 3; the core idles t0-t2."""
        sim, trace = run(GlobalEDFPolicy(), [task(1, 3, 1, 9)], 1)
        self.assertEqual(executed_sequence(trace), ["", "", "", 1])
        self.assertEqual(sim.processes[0].waiting_time, 0)


class ThermalAwareEDFTests(unittest.TestCase):

    def cores(self, t1, f1, t2, f2):
        cores = create_cores()
        cores[0].temperature, cores[0].frequency = t1, f1
        cores[1].temperature, cores[1].frequency = t2, f2
        return cores

    def test_non_urgent_task_takes_coolest_core(self):
        """Core1 55 °C @2.5, core2 50 °C @2.2. Task slack = 30-0-3 = 27
        (non-urgent, below guard) -> coolest core 2."""
        policy = ThermalAwareEDFPolicy()
        t = task(1, 0, 3, 30)
        t.last_core_id = None
        mapping = policy.schedule(0, [t], self.cores(55, 2.5, 50, 2.2))
        self.assertIs(mapping[2], t)
        self.assertIsNone(mapping[1])

    def test_urgent_task_takes_fastest_core(self):
        """Same cores. Task slack = 3-0-3 = 0 <= 2 (urgent) -> fastest core 1."""
        policy = ThermalAwareEDFPolicy()
        t = task(1, 0, 3, 3)
        t.last_core_id = None
        mapping = policy.schedule(0, [t], self.cores(55, 2.5, 50, 2.2))
        self.assertIs(mapping[1], t)

    def test_idle_insertion_only_for_large_slack(self):
        """Both cores at 59.5 °C (>= guard 59). Task with slack 27 is held
        back; task with slack 5 (< defer_slack 10) is dispatched."""
        policy = ThermalAwareEDFPolicy()
        relaxed = task(1, 0, 3, 30)
        tight = task(2, 0, 3, 8)
        for x in (relaxed, tight):
            x.last_core_id = None
        mapping = policy.schedule(0, [relaxed], self.cores(59.5, 2.5, 59.5, 2.5))
        self.assertEqual(list(mapping.values()), [None, None])
        mapping = policy.schedule(0, [tight], self.cores(59.5, 2.5, 59.5, 2.5))
        self.assertIn(tight, mapping.values())

    def test_idle_insertion_is_bounded(self):
        """1 core held at 65 °C (cooling 0, w 0, so the temperature never
        changes). Task(arr 0, burst 2, dl 20): slack = 18 - t, held while
        >= 10, i.e. t = 0..8. Dispatched at t=9, completes at 11 <= 20.
        Waiting 9."""
        thermal = {"initial_temperature": 65.0, "cooling_coefficient": 0.0}
        sim, trace = run(ThermalAwareEDFPolicy(), [task(1, 0, 2, 20, intensity=0)],
                         1, thermal=thermal)
        p = sim.processes[0]
        self.assertEqual(p.start_time, 9)
        self.assertEqual(p.completion_time, 11)
        self.assertEqual(p.waiting_time, 9)
        self.assertFalse(p.deadline_missed)

    def test_matches_global_edf_when_cool_and_identical(self):
        """Below the guard temperature and with identical cores, TA-EDF must
        produce the same completion times as G-EDF."""
        a, _ = run(GlobalEDFPolicy(), three_task_set(), 1)
        b, _ = run(ThermalAwareEDFPolicy(), three_task_set(), 1)
        self.assertEqual([x.completion_time for x in a.processes],
                         [x.completion_time for x in b.processes])


class EEVDFTests(unittest.TestCase):

    def test_equal_weights_alternate(self):
        """1 core, A and B (priority 3, burst 3, arr 0).
        t0: v=0, vd=1 for both -> tie -> lower PID A.
        t1: vA=1 > V=0.5 -> A ineligible -> B.
        t2: vA=vB=1, vd tie -> A ... sequence A B A B A B; A done 5, B done 6."""
        tasks = [task(1, 0, 3, 99), task(2, 0, 3, 99)]
        sim, trace = run(EEVDFInspiredPolicy(), tasks, 1)
        self.assertEqual(executed_sequence(trace), [1, 2, 1, 2, 1, 2])
        p = by_pid(sim.processes)
        self.assertEqual((p[1].completion_time, p[2].completion_time), (5, 6))

    def test_weighted_share(self):
        """Priority 2 (weight 3121) vs priority 3 (weight 1024) on 1 core.
        Expected CPU share of A = 3121 / 4145 = 75.3 % -> ~30 of 40 ticks."""
        tasks = [task(1, 0, 100, 999, priority=2), task(2, 0, 100, 999, priority=3)]
        sim, trace = run(EEVDFInspiredPolicy(), tasks, 1)
        first_40 = executed_sequence(trace)[:40]
        self.assertTrue(29 <= first_40.count(1) <= 31, first_40.count(1))

    def test_one_core_equal_weight_vruntime_spread_within_one_slice(self):
        """ONE core, three equal-weight tasks: the spread of virtual runtimes
        never exceeds one slice (1 tick). This is a single-core property
        only; it is not a two-core fairness guarantee (see the test below)."""
        policy = EEVDFInspiredPolicy()
        tasks = [task(i, 0, 20, 999) for i in (1, 2, 3)]
        cores = create_cores()[:1]
        sim = Simulator(tasks, cores, policy, NoDVFSGovernor())
        original = policy.schedule
        spreads = []

        def spy(t, ready, cores_):
            mapping = original(t, ready, cores_)
            live = [p for p in tasks if p.completion_time is None]
            if len(live) > 1:
                vs = [policy.v[p.pid] for p in live]
                spreads.append(max(vs) - min(vs))
            return mapping

        policy.schedule = spy
        sim.run()
        self.assertLessEqual(max(spreads), 1.0 + 1e-9)

    def test_two_core_limitation_is_documented_not_bounded(self):
        """Documents a KNOWN LIMITATION of the two-core global-queue model on
        the Burst VR workload. It asserts what the policy does guarantee:
        an eligible task is never left waiting while an ineligible task runs,
        and no core idles while a task is runnable. It also records, without
        asserting any bound, that ineligible tasks ARE dispatched and that
        lag exceeds one slice, so EEVDF's lag bound does not hold on 2 cores."""
        import workloads as W
        from policies import NICE_0_WEIGHT

        policy = EEVDFInspiredPolicy()
        original = policy.schedule
        stats = {"ineligible_dispatched": 0, "max_lag": 0.0}

        def spy(t, ready, cores_):
            mapping = original(t, ready, cores_)
            runnable = ready + [c.current_process for c in cores_ if c.current_process]
            chosen = [x for x in mapping.values() if x is not None]
            chosen_ids = {id(x) for x in chosen}
            eligible = lambda p: policy.v[p.pid] <= policy.V + 1e-12
            if any(not eligible(x) for x in chosen):
                self.assertFalse(
                    any(eligible(p) and id(p) not in chosen_ids for p in runnable),
                    f"t={t}: eligible task waiting while an ineligible task runs")
            self.assertEqual(len(chosen), min(len(cores_), len(runnable)))
            stats["ineligible_dispatched"] += sum(not eligible(x) for x in chosen)
            for p in runnable:
                lag = policy.weight(p) * (policy.V - policy.v[p.pid]) / NICE_0_WEIGHT
                stats["max_lag"] = max(stats["max_lag"], abs(lag))
            return mapping

        policy.schedule = spy
        Simulator(W.create_burst_vr_workload(), create_cores(), policy,
                  NoDVFSGovernor()).run()

        # Observed limitation (values are recorded, not a guarantee).
        self.assertGreater(stats["ineligible_dispatched"], 0)
        self.assertGreater(stats["max_lag"], 1.0)
        print(f"\n  [documented limitation] Burst VR, 2 cores: "
              f"{stats['ineligible_dispatched']} ineligible dispatches, "
              f"max |lag| = {stats['max_lag']:.2f} slices")

    def test_ignores_deadlines(self):
        """EEVDF does not use deadlines: urgent B (dl 2) does not preempt
        equally weighted A at t0 (A has lower PID)."""
        sim, trace = run(EEVDFInspiredPolicy(), [task(1, 0, 2, 50), task(2, 0, 2, 2)], 1)
        self.assertEqual(executed_sequence(trace)[0], 1)


class RoundRobinTests(unittest.TestCase):

    def test_quantum_one_alternates(self):
        sim, trace = run(RoundRobinPolicy(), [task(1, 0, 2, 9), task(2, 0, 2, 9)], 1)
        self.assertEqual(executed_sequence(trace), [1, 2, 1, 2])


if __name__ == "__main__":
    unittest.main()
