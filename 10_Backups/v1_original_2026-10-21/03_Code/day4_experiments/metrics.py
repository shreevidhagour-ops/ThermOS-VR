class MetricsCalculator:

    def __init__(self, processes, execution_log):
        self.processes = processes
        self.execution_log = execution_log

    def average_waiting_time(self):
        if not self.processes:
            return 0.0

        return sum(
            p.waiting_time for p in self.processes
        ) / len(self.processes)

    def average_turnaround_time(self):
        if not self.processes:
            return 0.0

        return sum(
            p.turnaround_time for p in self.processes
        ) / len(self.processes)

    def deadline_misses(self):
        return sum(
            1 for p in self.processes
            if getattr(p, "deadline_missed", False)
        )

    def average_temperature(self):
        temperatures = [
            entry["temperature"]
            for entry in self.execution_log
            if "temperature" in entry
        ]

        if not temperatures:
            return 0.0

        return sum(temperatures) / len(temperatures)

    def peak_temperature(self):
        temperatures = [
            entry["temperature"]
            for entry in self.execution_log
            if "temperature" in entry
        ]

        if not temperatures:
            return 0.0

        return max(temperatures)

    def thermal_exposure_samples(self):
        """
        Count the number of core-time samples spent in
        HOT or CRITICAL thermal states.
        """

        return sum(
            1
            for entry in self.execution_log
            if entry.get("thermal_state") in ["HOT", "CRITICAL"]
        )

    def cpu_utilization(self):
        if not self.execution_log:
            return 0.0

        busy_samples = 0
        total_samples = len(self.execution_log)

        for entry in self.execution_log:
            if entry.get("process") != "Idle":
                busy_samples += 1

        return (
            busy_samples / total_samples
        ) * 100.0

    def calculate_all(self):
        return {
            "average_waiting_time":
                self.average_waiting_time(),

            "average_turnaround_time":
                self.average_turnaround_time(),

            "deadline_misses":
                self.deadline_misses(),

            "average_temperature":
                self.average_temperature(),

            "peak_temperature":
                self.peak_temperature(),

            "thermal_exposure_samples":
                self.thermal_exposure_samples(),

            "average_cpu_utilization":
                self.cpu_utilization()
        }
