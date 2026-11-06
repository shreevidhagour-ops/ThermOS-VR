"""
Working replacement for day1_basic_scheduler/main.py (bug B9).

The original imports a `scheduler` module that does not exist in day1. The FCFS
scheduler it needs is in day1_basic_scheduler/fcfs_basic.py.
"""

import os
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "day1_basic_scheduler",
    ),
)

from fcfs_basic import FCFSScheduler  # noqa: E402
from workloads import create_vr_workload  # noqa: E402


def main():
    processes = create_vr_workload()
    execution_order = FCFSScheduler(processes).schedule()

    print("\n=== ThermOS-VR Day 1: FCFS Baseline ===\n")
    print("Execution Order:")

    for process in execution_order:
        print(
            f"{process.name}: "
            f"Start={process.start_time}, "
            f"Completion={process.completion_time}, "
            f"Waiting={process.waiting_time}, "
            f"Turnaround={process.turnaround_time}, "
            f"Deadline Missed={process.deadline_missed}"
        )

    average_waiting_time = sum(p.waiting_time for p in processes) / len(processes)
    average_turnaround_time = sum(p.turnaround_time for p in processes) / len(processes)
    deadline_misses = sum(p.deadline_missed for p in processes)

    print("\n=== Baseline Metrics ===")
    print(f"Average Waiting Time: {average_waiting_time:.2f}")
    print(f"Average Turnaround Time: {average_turnaround_time:.2f}")
    print(f"Deadline Misses: {deadline_misses}")


if __name__ == "__main__":
    main()
