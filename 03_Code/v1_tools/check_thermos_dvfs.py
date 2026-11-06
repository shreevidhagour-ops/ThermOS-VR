"""
Working replacement for day4_experiments/check_thermos_dvfs.py (bug B10).

Prints each core's starting frequency and every frequency change for ThermOS-VR
on one workload. The original called run_scheduler() without a workload; even
with one, that function appends to the frozen results CSV. This version writes
no files.
"""

import argparse
import contextlib
import io

from v1_common import WORKLOADS, run_experiment


def frequency_transitions(execution_log):
    """Return the log entries where a core's frequency is first seen or changes."""
    transitions = []
    previous_frequency = {}

    for entry in execution_log:
        core = entry["core"]
        if previous_frequency.get(core) != entry["frequency"]:
            transitions.append(entry)
            previous_frequency[core] = entry["frequency"]

    return transitions


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument(
        "--workload", choices=list(WORKLOADS), default="Normal VR Workload",
    )
    args = parser.parse_args()

    # v1 schedulers print per-tick progress
    with contextlib.redirect_stdout(io.StringIO()):
        execution_log, _ = run_experiment("ThermOS-VR", args.workload)

    print(f"\n=== ThermOS-VR DVFS Transitions: {args.workload} ===")

    for entry in frequency_transitions(execution_log):
        print(
            f"Time: {entry['time']:3d}s | "
            f"Core: {entry['core']} | "
            f"Temperature: {entry['temperature']:.2f}°C | "
            f"Thermal State: {entry['thermal_state']} | "
            f"Frequency: {entry['frequency']:.2f} GHz"
        )


if __name__ == "__main__":
    main()
