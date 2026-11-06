class ThermalDVFSScheduler:
    """
    FCFS-style scheduler with thermal-aware DVFS.

    This scheduler is used as an intermediate baseline
    to isolate the effect of frequency scaling from
    thermal-aware task selection.
    """

    def __init__(self, processes, cores):
        self.processes = processes
        self.cores = cores

        self.current_time = 0
        self.execution_log = []

        self.thermal_violations = 0
        self.throttling_events = 0

        # Tracks when a process starts waiting in the ready queue
        self.waiting_start = {}

    def update_frequency(self, core):
        """
        Apply the same hysteresis-based DVFS policy
        used by ThermOS-VR.
        """

        temperature = core.temperature

        # 2.5 GHz -> 2.2 GHz
        if core.frequency == 2.5:
            if temperature >= 60:
                core.frequency = 2.2

        # 2.2 GHz -> 2.5 GHz
        elif core.frequency == 2.2:
            if temperature <= 58:
                core.frequency = 2.5

        # 1.8 GHz -> 2.2 GHz
        elif core.frequency == 1.8:
            if temperature <= 68:
                core.frequency = 2.2

        # 1.4 GHz -> 1.8 GHz
        elif core.frequency == 1.4:
            if temperature <= 78:
                core.frequency = 1.8

    def get_ready_processes(self):
        """
        Return processes that have arrived and
        still have remaining execution time.
        """

        return [
            process
            for process in self.processes
            if (
                process.arrival_time <= self.current_time
                and process.remaining_time > 0
            )
        ]

    def run_simulation(self):
        """
        Run FCFS scheduling with thermal-aware DVFS.
        """

        self.current_time = 0
        self.execution_log = []
        self.waiting_start = {}

        while True:

            # --------------------------------------------------
            # 1. Get ready processes
            # --------------------------------------------------

            ready_processes = self.get_ready_processes()

            # Record when each process starts waiting
            for process in ready_processes:
                if process not in self.waiting_start:
                    self.waiting_start[process] = self.current_time

            # --------------------------------------------------
            # 2. Assign waiting processes to idle cores
            # --------------------------------------------------

            for core in self.cores:

                if core.current_process is None:

                    if ready_processes:

                        # FCFS selection
                        ready_processes.sort(
                            key=lambda p: (
                                p.arrival_time,
                                p.pid
                            )
                        )

                        process = ready_processes[0]

                        # Record first execution time
                        if process.start_time is None:
                            process.start_time = self.current_time

                        # Add actual ready-queue waiting time
                        process.waiting_time += (
                            self.current_time
                            - self.waiting_start.pop(process)
                        )

                        core.assign_process(process)

                        ready_processes.remove(process)

            # --------------------------------------------------
            # 3. Execute one simulation time step
            # --------------------------------------------------

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    # Execute work according to current frequency
                    process.remaining_time -= (
                        self._execution_amount(core)
                    )

                    # Prevent negative remaining time
                    if process.remaining_time < 0:
                        process.remaining_time = 0

                # Update temperature after execution
                core.update_temperature()

                # Apply thermal DVFS
                self.update_frequency(core)

            # --------------------------------------------------
            # 4. Log current system state
            # --------------------------------------------------

            for core in self.cores:

                process_name = (
                    core.current_process.name
                    if core.current_process is not None
                    else "Idle"
                )

                self.execution_log.append({
                    "time": self.current_time,
                    "core": core.core_id,
                    "process": process_name,
                    "temperature": core.temperature,
                    "frequency": core.frequency,
                    "thermal_state": core.get_thermal_state(),
                    "utilization": core.utilization
                })

            # --------------------------------------------------
            # 5. Check completed processes
            # --------------------------------------------------

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    if process.remaining_time <= 0:

                        process.completion_time = (
                            self.current_time + 1
                        )

                        process.turnaround_time = (
                            process.completion_time
                            - process.arrival_time
                        )

                        # Check deadline miss
                        if (
                            process.completion_time
                            > process.deadline
                        ):
                            process.deadline_missed = True

                        core.release_process()

            # --------------------------------------------------
            # 6. Stop when all processes are complete
            # --------------------------------------------------

            all_complete = all(
                process.remaining_time <= 0
                for process in self.processes
            )

            if all_complete:
                break

            # Move to next simulation time step
            self.current_time += 1

        return self.execution_log

    def _execution_amount(self, core):
        """
        Convert simulated CPU frequency into execution progress.

        Higher frequency allows slightly more work
        to be completed per simulation time step.
        """

        return core.frequency / 2.5
