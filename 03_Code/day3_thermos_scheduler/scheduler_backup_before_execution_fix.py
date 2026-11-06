class ThermOSVRScheduler:
    def update_frequency(self, core):
        """
        Adjust simulated CPU frequency based on
        the current thermal state of the core.

        Hysteresis is used around the COOL/WARM boundary
        to prevent rapid frequency switching.
        """

        temperature = core.temperature

        # COOL → WARM:
        # Reduce frequency when temperature reaches 60°C.
        if core.frequency == 2.5:

            if temperature >= 60:
                core.frequency = 2.2

        # WARM → COOL:
        # Restore the higher frequency only after cooling
        # sufficiently below the transition threshold.
        elif core.frequency == 2.2:

            if temperature <= 58:
                core.frequency = 2.5

        # HOT → WARM:
        # If temperature falls below 68°C, increase
        # frequency from the HOT level.
        elif core.frequency == 1.8:

            if temperature <= 68:
                core.frequency = 2.2

        # CRITICAL → HOT:
        # If temperature falls below 78°C, increase
        # frequency from the critical throttling level.
        elif core.frequency == 1.4:

            if temperature <= 78:
                core.frequency = 1.8
    def __init__(self, processes, cores):
        self.processes = processes
        self.cores = cores
        self.execution_log = []

        # Thermal protection metrics
        self.thermal_violations = 0
        self.throttling_events = 0

    def select_core(self, process, current_time):
        """
        Select the most suitable available core.
        """

        available_cores = [
            core for core in self.cores
            if (
                core.current_process is None
                and core.get_thermal_state() != "CRITICAL"
            )
        ]

        if not available_cores:
            return None

        best_core = None
        best_score = float("-inf")

        for core in available_cores:

            thermal_score = (100 - core.temperature) * 1.5

            if core.get_thermal_state() == "HOT":
                thermal_score -= 50

            elif core.get_thermal_state() == "WARM":
                thermal_score -= 10

            # Core-type suitability
            if process.workload_intensity >= 70:
                if core.core_type == "Performance":
                    core_type_score = 20
                else:
                    core_type_score = 10

            elif process.workload_intensity <= 40:
                if core.core_type == "Efficiency":
                    core_type_score = 20
                else:
                    core_type_score = 10

            else:
                core_type_score = 15

            # Deadline urgency
            remaining_time = process.deadline - current_time

            if remaining_time <= process.remaining_time:
                deadline_score = 30
            else:
                deadline_score = 15

            # Combined score
            score = (
                thermal_score
                + core_type_score
                + deadline_score
            )

            print(
                f"Process: {process.name} | "
                f"Core {core.core_id} | "
                f"Temperature: {core.temperature:.2f}°C | "
                f"Score: {score:.2f}"
            )

            if score > best_score:
                best_score = score
                best_core = core

        return best_core

    def schedule(self):
        """
        Basic thermal-aware multicore scheduling.
        """

        sorted_processes = sorted(
            self.processes,
            key=lambda process: process.arrival_time
        )

        current_time = 0

        for process in sorted_processes:

            if current_time < process.arrival_time:
                current_time = process.arrival_time

            selected_core = self.select_core(
                process,
                current_time
            )

            if selected_core is None:
                continue

            selected_core.assign_process(process)

            self.execution_log.append({
                "time": current_time,
                "process": process.name,
                "core": selected_core.core_id,
                "temperature": selected_core.temperature
            })

        return self.execution_log

    def run_simulation(self):
        """
        Run the thermal-aware scheduling simulation
        using a discrete one-second time step.
        """

        current_time = 0
        completed_processes = []

        # Reset execution log
        self.execution_log = []

        # Record initial state
        for core in self.cores:
            self.execution_log.append({
                "time": current_time,
                "core": core.core_id,
                "process": "Idle",
                "temperature": core.temperature,
                "thermal_state": core.get_thermal_state(),
                "frequency": core.frequency
            })

        # Main simulation loop
        while len(completed_processes) < len(self.processes):

            # =================================
            # STEP 1: Schedule arrived tasks
            # =================================

            ready_processes = [
                process
                for process in self.processes
                if (
                    process.arrival_time <= current_time
                    and process.remaining_time > 0
                    and process not in completed_processes
                    and not any(
                        core.current_process == process
                        for core in self.cores
                    )
                )
            ]

            for process in ready_processes:

                selected_core = self.select_core(
                    process,
                    current_time
                )

                if selected_core is None:
                    continue

                if process.start_time is None:
                    process.start_time = current_time

                    process.waiting_time = (
                        current_time
                        - process.arrival_time
                    )

                selected_core.assign_process(process)

            # =================================
            # STEP 2: Execute for one second
            # =================================

            for core in self.cores:

                previous_state = core.get_thermal_state()

                if core.current_process is not None:

                    process = core.current_process

                    process.remaining_time -= 1

                    core.update_temperature()

                else:

                    core.update_temperature()

                current_state = core.get_thermal_state()

                # Count thermal violations when a core
                # enters HOT or CRITICAL
                if (
                    current_state in ["HOT", "CRITICAL"]
                    and previous_state not in ["HOT", "CRITICAL"]
                ):
                    self.thermal_violations += 1

                # Update simulated frequency based on
                # the new thermal state
                self.update_frequency(core)

            # =================================
            # STEP 3: Advance simulation time
            # =================================

            current_time += 1

            # =================================
            # THERMAL PROTECTION
            # =================================

            for core in self.cores:

                if core.current_process is None:
                    continue

                thermal_state = core.get_thermal_state()

                if thermal_state == "CRITICAL":

                    print(
                        f"THERMAL PROTECTION: "
                        f"Core {core.core_id} reached CRITICAL "
                        f"temperature ({core.temperature:.2f}°C)"
                    )

                    self.throttling_events += 1

                    # Pause the current task.
                    # The task remains unfinished and will be
                    # scheduled again later.
                    core.release_process()

            # =================================
            # STEP 4: Complete finished tasks
            # =================================

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    if process.remaining_time <= 0:

                        process.completion_time = current_time

                        process.turnaround_time = (
                            process.completion_time
                            - process.arrival_time
                        )

                        process.deadline_missed = (
                            process.completion_time
                            > process.deadline
                        )

                        completed_processes.append(process)

                        core.release_process()

            # =================================
            # STEP 5: Log current state
            # =================================

            for core in self.cores:

                self.execution_log.append({
                    "time": current_time,
                    "core": core.core_id,
                    "process": (
                        core.current_process.name
                        if core.current_process is not None
                        else "Idle"
                    ),
                    "temperature": core.temperature,
                    "thermal_state": core.get_thermal_state(),
                    "frequency": core.frequency
                })

        return self.execution_log
