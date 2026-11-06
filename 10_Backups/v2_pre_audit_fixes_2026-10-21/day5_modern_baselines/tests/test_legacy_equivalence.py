"""
The v2 engine must reproduce the v1 schedulers' task outcomes and
per-tick temperatures on all four benchmark workloads. The v1 code is
imported and run read-only (nothing is written to disk).
"""

import contextlib
import io
import random
import unittest

import testutil  # noqa: F401  (sets sys.path)
from testutil import run, create_cores

import workloads as W
from simulation_engine import SimulationEngine as V1Engine
from baseline_schedulers import (
    FCFSScheduler, PriorityScheduler, RoundRobinScheduler,
)
from scheduler import ThermOSVRScheduler
from core import Core

from policies import (
    FCFSPolicy, PriorityPolicy, RoundRobinPolicy, ThermOSVRv1Policy,
)
from metrics_v2 import compute_metrics

WORKLOADS = {
    "Normal VR": W.create_vr_workload,
    "Burst VR": W.create_burst_vr_workload,
    "Sustained Thermal": W.create_sustained_thermal_workload,
    "HOT Thermal": W.create_hot_thermal_workload,
}

# v1 scheduler -> (v2 policy, governor reproducing v1 frequency behaviour)
PAIRS = [
    (FCFSScheduler, FCFSPolicy, "off"),
    (PriorityScheduler, PriorityPolicy, "off"),
    (RoundRobinScheduler, RoundRobinPolicy, "off"),
    (ThermOSVRScheduler, ThermOSVRv1Policy, "legacy"),
]


def run_v1(scheduler_class, workload):
    processes = workload()
    cores = [Core(1, "Performance"), Core(2, "Efficiency")]
    engine = V1Engine(processes, cores, scheduler_class(processes, cores))
    with contextlib.redirect_stdout(io.StringIO()):
        log = engine.run()
    return engine.get_processes(), log


def outcomes(processes):
    return {
        p.pid: (p.start_time, p.completion_time, p.waiting_time,
                p.turnaround_time, p.deadline_missed)
        for p in processes
    }


class LegacyEquivalenceTests(unittest.TestCase):

    def test_v2_reproduces_v1_task_outcomes_and_temperatures(self):
        for v1_class, v2_class, governor in PAIRS:
            for name, workload in WORKLOADS.items():
                with self.subTest(policy=v2_class.name, workload=name):
                    v1_procs, v1_log = run_v1(v1_class, workload)
                    sim, trace = run(v2_class(), workload(), governor=governor)

                    self.assertEqual(outcomes(v1_procs), outcomes(sim.processes))

                    v1_temps = {
                        (r["time"], r["core"]): r["temperature"]
                        for r in v1_log if r["time"] >= 1
                    }
                    v2_temps = {
                        (r["time"], r["core"]): r["temperature"] for r in trace
                    }
                    self.assertEqual(set(v1_temps), set(v2_temps))
                    for key, value in v2_temps.items():
                        self.assertAlmostEqual(v1_temps[key], value, places=9)

    def test_thermos_v1_equals_fcfs_with_same_dvfs(self):
        """Finding B8: under the same DVFS governor, ThermOS-VR v1 and FCFS
        give identical task outcomes and identical values for every
        aggregate metric. Per-core placement can differ (Normal VR: tasks 5
        and 6 swap cores), but the cores are identical, so the differences
        cancel out in every metric."""
        for governor in ("legacy", "hysteresis"):
            for name, workload in WORKLOADS.items():
                with self.subTest(governor=governor, workload=name):
                    a, ta = run(ThermOSVRv1Policy(), workload(), governor=governor)
                    b, tb = run(FCFSPolicy(), workload(), governor=governor)
                    self.assertEqual(outcomes(a.processes), outcomes(b.processes))
                    self.assertEqual(compute_metrics(a.processes, ta, 2),
                                     compute_metrics(b.processes, tb, 2))

    def test_corrected_governor_equals_legacy_on_benchmark_workloads(self):
        """B3: the multi-level fix changes nothing on the four workloads,
        because 1.8 / 1.4 GHz are never needed under default parameters."""
        for name, workload in WORKLOADS.items():
            with self.subTest(workload=name):
                _, ta = run(FCFSPolicy(), workload(), governor="legacy")
                _, tb = run(FCFSPolicy(), workload(), governor="hysteresis")
                self.assertEqual([r["temperature"] for r in ta],
                                 [r["temperature"] for r in tb])

    def test_thermos_v1_port_matches_original_scores(self):
        """The v2 port selects the same core as the original select_core()
        for 2000 random core states and tasks."""
        rng = random.Random(7)
        original = ThermOSVRScheduler([], [])
        port = ThermOSVRv1Policy()

        for _ in range(2000):
            cores = create_cores()
            for c in cores:
                c.temperature = rng.uniform(40, 85)
            t = rng.randint(0, 200)
            p = W.create_hot_thermal_workload()[0]
            p.workload_intensity = rng.choice([20, 35, 40, 55, 70, 90, 100])
            p.deadline = rng.randint(0, 250)
            p.remaining_time = rng.uniform(0, 80)
            original.cores = cores

            with contextlib.redirect_stdout(io.StringIO()):
                expected = original.select_core(p, t)

            self.assertIs(port.choose_core(p, cores, t), expected)


if __name__ == "__main__":
    unittest.main()
