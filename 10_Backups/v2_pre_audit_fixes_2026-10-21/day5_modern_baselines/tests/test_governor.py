"""
DVFS governor verification: transition table, the v1 bug (B2) and
reachability of every frequency level (B3).
"""

import unittest

from testutil import task, run, create_cores
from sim_engine import HysteresisDVFSGovernor, LegacyHysteresisGovernor
from policies import FCFSPolicy


def step(governor, frequency, temperature):
    core = create_cores()[0]
    core.frequency, core.temperature = frequency, temperature
    governor.update(core)
    return core.frequency


def frequencies_reached(governor, thermal=None, ticks=600):
    sim, trace = run(FCFSPolicy(), [task(1, 0, ticks, 10**6, intensity=100)],
                     1, governor=governor, thermal=thermal)
    seen = sorted({r["frequency_used"] for r in trace}, reverse=True)
    return seen, max(r["temperature"] for r in trace)


class GovernorTransitionTests(unittest.TestCase):

    def test_corrected_transition_table(self):
        g = HysteresisDVFSGovernor()
        cases = [
            (2.5, 59.99, 2.5), (2.5, 60.0, 2.2),
            (2.2, 69.99, 2.2), (2.2, 70.0, 1.8), (2.2, 58.0, 2.5), (2.2, 58.01, 2.2),
            (1.8, 79.99, 1.8), (1.8, 80.0, 1.4), (1.8, 68.0, 2.2), (1.8, 68.01, 1.8),
            (1.4, 78.01, 1.4), (1.4, 78.0, 1.8),
        ]
        for f, temp, expected in cases:
            with self.subTest(f=f, temp=temp):
                self.assertEqual(step(g, f, temp), expected)

    def test_one_step_per_tick(self):
        """At 95 °C and 2.5 GHz the governor moves one level only."""
        self.assertEqual(step(HysteresisDVFSGovernor(), 2.5, 95.0), 2.2)

    def test_legacy_bug_b2_never_goes_below_2_2(self):
        """v1 logic stays at 2.2 GHz even at 75 °C or 90 °C."""
        g = LegacyHysteresisGovernor()
        self.assertEqual(step(g, 2.2, 75.0), 2.2)
        self.assertEqual(step(g, 2.2, 90.0), 2.2)


class ReachabilityTests(unittest.TestCase):

    def test_steady_state_temperatures(self):
        """T* = ambient + heat / cooling = 25 + (f/2.5)^2 / 0.02 at 100 % load."""
        expected = {2.5: 75.0, 2.2: 63.72, 1.8: 50.92, 1.4: 40.68}
        for f, value in expected.items():
            self.assertAlmostEqual(25 + (f / 2.5) ** 2 / 0.02, value, places=2)

    def test_default_parameters_only_reach_2_5_and_2_2(self):
        """B3: with the v1 thermal parameters, even the corrected governor
        never needs 1.8 / 1.4 GHz: at 2.2 GHz the core settles at 63.7 °C < 70 °C."""
        seen, peak = frequencies_reached("hysteresis")
        self.assertEqual(seen, [2.5, 2.2])
        self.assertLess(peak, 70.0)

    def test_stress_parameters_reach_all_four_levels(self):
        """With heat_coefficient = 2.5 (stress test only):
        T*(2.2) = 121.8 °C -> 1.8; T*(1.8) = 89.8 °C -> 1.4;
        T*(1.4) = 64.2 °C -> back to 1.8. All four levels occur."""
        seen, peak = frequencies_reached("hysteresis", {"heat_coefficient": 2.5})
        self.assertEqual(seen, [2.5, 2.2, 1.8, 1.4])
        self.assertLess(peak, 82.0)

    def test_stress_parameters_legacy_governor_overheats(self):
        """Same stress parameters with the v1 logic: stuck at 2.2 GHz, so the
        core climbs past 80 °C (CRITICAL)."""
        seen, peak = frequencies_reached("legacy", {"heat_coefficient": 2.5})
        self.assertEqual(seen, [2.5, 2.2])
        self.assertGreater(peak, 80.0)


if __name__ == "__main__":
    unittest.main()
