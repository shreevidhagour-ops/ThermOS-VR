class Process:
    def __init__(
        self,
        pid,
        name,
        arrival_time,
        burst_time,
        priority,
        workload_intensity,
        task_type,
        deadline
    ):
        self.pid = pid
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.workload_intensity = workload_intensity
        self.task_type = task_type
        self.deadline = deadline

        # Runtime values
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.remaining_time = burst_time
        self.executed_work = 0.0
        self.deadline_missed = False

    def __str__(self):
        return (
            f"{self.pid} - {self.name} "
            f"(Arrival: {self.arrival_time}, "
            f"Burst: {self.burst_time}, "
            f"Priority: {self.priority})"
        )
