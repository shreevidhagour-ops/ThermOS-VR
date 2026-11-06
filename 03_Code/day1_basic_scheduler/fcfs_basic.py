class FCFSScheduler:
    def __init__(self, processes):
        self.processes = processes
        self.execution_order = []

    def schedule(self):
        # Sort processes according to arrival time
        sorted_processes = sorted(
            self.processes,
            key=lambda process: process.arrival_time
        )

        current_time = 0

        for process in sorted_processes:

            # If the CPU is idle before the process arrives
            if current_time < process.arrival_time:
                current_time = process.arrival_time

            # Record start time
            process.start_time = current_time

            # Waiting time
            process.waiting_time = (
                process.start_time - process.arrival_time
            )

            # Execute process
            current_time += process.burst_time

            # Record completion time
            process.completion_time = current_time

            # Turnaround time
            process.turnaround_time = (
                process.completion_time - process.arrival_time
            )

            # Deadline miss detection
            process.deadline_missed = (
                process.completion_time > process.deadline
            )

            # Store execution order
            self.execution_order.append(process)

        return self.execution_order
