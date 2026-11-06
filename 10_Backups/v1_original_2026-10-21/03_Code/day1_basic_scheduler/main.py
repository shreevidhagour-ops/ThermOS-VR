from workloads import create_vr_workload
from scheduler import FCFSScheduler


def main():
    # Create AR/VR workload
    processes = create_vr_workload()

    # Create FCFS scheduler
    scheduler = FCFSScheduler(processes)

    # Run scheduling
    execution_order = scheduler.schedule()

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

    # Calculate average metrics
    average_waiting_time = sum(
        process.waiting_time for process in processes
    ) / len(processes)

    average_turnaround_time = sum(
        process.turnaround_time for process in processes
    ) / len(processes)

    deadline_misses = sum(
        process.deadline_missed for process in processes
    )

    print("\n=== Baseline Metrics ===")
    print(f"Average Waiting Time: {average_waiting_time:.2f}")
    print(f"Average Turnaround Time: {average_turnaround_time:.2f}")
    print(f"Deadline Misses: {deadline_misses}")


if __name__ == "__main__":
    main()
