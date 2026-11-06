"""Run from 03_Code/v1_tools/: python -B -m unittest test_v1_tools -v"""

import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

from check_thermos_dvfs import frequency_transitions
from v1_common import FROZEN_RESULTS, HERE


def run_script(*args):
    return subprocess.run(
        [sys.executable, "-B", *args],
        cwd=HERE, capture_output=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def file_bytes(path):
    with open(path, "rb") as file:
        return file.read()


class SafeRunnerTest(unittest.TestCase):
    def setUp(self):
        self.frozen_hash = hashlib.sha256(file_bytes(FROZEN_RESULTS)).hexdigest()
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.output = os.path.join(directory.name, "results.csv")

    def tearDown(self):
        self.assertEqual(
            hashlib.sha256(file_bytes(FROZEN_RESULTS)).hexdigest(), self.frozen_hash
        )

    def test_reproduces_frozen_results_byte_for_byte(self):
        result = run_script("run_v1_experiments.py", "--output", self.output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(file_bytes(self.output), file_bytes(FROZEN_RESULTS))

    def test_refuses_existing_file_without_overwrite(self):
        with open(self.output, "w") as file:
            file.write("keep me")
        result = run_script("run_v1_experiments.py", "--output", self.output)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(file_bytes(self.output), b"keep me")

    def test_overwrite_replaces_existing_file(self):
        with open(self.output, "w") as file:
            file.write("old")
        result = run_script(
            "run_v1_experiments.py", "--output", self.output, "--overwrite"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(file_bytes(self.output), file_bytes(FROZEN_RESULTS))

    def test_refuses_frozen_results_even_with_overwrite(self):
        result = run_script(
            "run_v1_experiments.py", "--output", FROZEN_RESULTS, "--overwrite"
        )
        self.assertEqual(result.returncode, 2)


class ReplacementScriptsTest(unittest.TestCase):
    def test_day1_fcfs_runs(self):
        result = run_script("run_day1_fcfs.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Average Waiting Time:", result.stdout)

    def test_dvfs_check_runs_on_a_workload_that_throttles(self):
        result = run_script(
            "check_thermos_dvfs.py", "--workload", "HOT Thermal Workload"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Frequency: 2.50 GHz", result.stdout)
        self.assertIn("Frequency: 2.20 GHz", result.stdout)

    def test_transitions_report_first_sample_and_changes_only(self):
        log = [
            {"core": 1, "frequency": 2.5},
            {"core": 2, "frequency": 2.5},
            {"core": 1, "frequency": 2.5},
            {"core": 1, "frequency": 2.2},
            {"core": 1, "frequency": 2.2},
            {"core": 1, "frequency": 2.5},
        ]
        self.assertEqual(
            frequency_transitions(log), [log[0], log[1], log[3], log[5]]
        )


if __name__ == "__main__":
    unittest.main()
