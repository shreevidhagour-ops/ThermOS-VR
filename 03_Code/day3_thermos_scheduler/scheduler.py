class ThermOSVRScheduler:

    def update_frequency(self, core):
        """
        Adjust simulated CPU frequency based on
        the current thermal state of the core.

        Hysteresis is used around the COOL/WARM boundary
        to prevent rapid frequency switching.
        """

        temperature = core.temperature

        # COOL -> WARM
        # Reduce frequency when temperature reaches 60°C.
        if core.frequency == 2.5:

            if temperature >= 60:
                core.frequency = 2.2

        # WARM -> COOL
        # Restore higher frequency only after cooling
        # sufficiently below the transition threshold.
        elif core.frequency == 2.2:

            if temperature <= 58:
                core.frequency = 2.5

        # HOT -> WARM
        # Increase frequency when temperature falls
        # sufficiently below the HOT threshold.
        elif core.frequency == 1.8:

            if temperature <= 68:
                core.frequency = 2.2

        # CRITICAL -> HOT
        # Increase frequency when temperature falls
        # sufficiently below the CRITICAL threshold.
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
        Select the most suitable available core
        using thermal state, core type, and deadline urgency.
        """

        available_cores = [
            core
            for core in self.cores
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

            # -----------------------------------------
            # Thermal score
            # -----------------------------------------

            thermal_score = (
                (100 - core.temperature) * 1.5
            )

            if core.get_thermal_state() == "HOT":
                thermal_score -= 50

            elif core.get_thermal_state() == "WARM":
                thermal_score -= 10

            # -----------------------------------------
            # Core-type suitability
            # -----------------------------------------

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

            # -----------------------------------------
            # Deadline urgency
            # -----------------------------------------

            remaining_time = (
                process.deadline - current_time
            )

            if remaining_time <= process.remaining_time:
                deadline_score = 30
            else:
                deadline_score = 15

            # -----------------------------------------
            # Combined score
            # -----------------------------------------

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

        This method is retained for compatibility.
        The experimental runner uses run_simulation().
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

        Frequency-dependent execution is used so that
        simulated DVFS produces both thermal and
        performance effects.
        """

        current_time = 0
        completed_processes = []
        waiting_start = {}

        # Reset execution log
        self.execution_log = []

        # Reset thermal counters
        self.thermal_violations = 0
        self.throttling_events = 0

        # =========================================
        # INITIAL STATE
        # =========================================

        for core in self.cores:

            self.execution_log.append({
                "time": current_time,
                "core": core.core_id,
                "process": "Idle",
                "temperature": core.temperature,
                "frequency": core.frequency,
                "thermal_state": core.get_thermal_state(),
                "utilization": 0.0
            })

        # =========================================
        # MAIN SIMULATION LOOP
        # =========================================

        while len(completed_processes) < len(self.processes):

            # =========================================
            # STEP 1: Schedule arrived tasks
            # =========================================

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

            # FCFS-like ordering among ready tasks
            ready_processes.sort(
                key=lambda process: (
                    process.arrival_time,
                    process.pid
                )
            )

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

            # =========================================
            # STEP 2: Execute for one second
            # =========================================

            for core in self.cores:

                # Record thermal state BEFORE execution
                previous_state = (
                    core.get_thermal_state()
                )

                if core.current_process is not None:

                    process = core.current_process

                    # ---------------------------------
                    # Frequency-dependent execution
                    # ---------------------------------
                    #
                    # Reference frequency = 2.5 GHz
                    #
                    # 2.5 GHz -> 1.00 work unit
                    # 2.2 GHz -> 0.88 work unit
                    # 1.8 GHz -> 0.72 work unit
                    # 1.4 GHz -> 0.56 work unit
                    #

                    execution_amount = (
                        core.frequency / 2.5
                    )

                    process.remaining_time -= execution_amount
                    process.executed_work += execution_amount

                    # Avoid tiny floating-point residues.
                    if process.remaining_time < 0.000001:
                        process.remaining_time = 0

                # Update thermal state after execution
                core.update_temperature()

                current_state = (
                    core.get_thermal_state()
                )

                # -----------------------------------------
                # Count transitions into HOT / CRITICAL
                # -----------------------------------------

                if (
                    current_state in ["HOT", "CRITICAL"]
                    and previous_state
                    not in ["HOT", "CRITICAL"]
                ):
                    self.thermal_violations += 1

                # -----------------------------------------
                # Apply thermal-aware DVFS
                # -----------------------------------------

                self.update_frequency(core)

            # =========================================
            # STEP 3: Advance simulation time
            # =========================================

            current_time += 1

            # =========================================
            # STEP 4: Check completed processes
            # =========================================
            #
            # Completion is checked BEFORE thermal
            # protection so that a task which finishes
            # during this timestep is recorded correctly.
            #

            for core in self.cores:

                if core.current_process is None:
                    continue

                process = core.current_process

                if process.remaining_time <= 0:

                    process.completion_time = (
                        current_time
                    )

                    process.turnaround_time = (
                        process.completion_time
                        - process.arrival_time
                    )

                    process.deadline_missed = (
                        process.completion_time
                        > process.deadline
                    )

                    completed_processes.append(
                        process
                    )

                    core.release_process()

            # =========================================
            # STEP 5: Thermal protection
            # =========================================

            for core in self.cores:

                if core.current_process is None:
                    continue

                thermal_state = (
                    core.get_thermal_state()
                )

                if thermal_state == "CRITICAL":

                    print(
                        f"THERMAL PROTECTION: "
                        f"Core {core.core_id} reached "
                        f"CRITICAL temperature "
                        f"({core.temperature:.2f}°C)"
                    )

                    self.throttling_events += 1

                    # Pause the task and record the beginning
                    # of its next ready-queue waiting interval.
                    waiting_start[core.current_process] = current_time

                    core.release_process()

            # =========================================
            # STEP 6: Log current state
            # =========================================

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
                    "frequency": core.frequency,
                    "thermal_state": (
                        core.get_thermal_state()
                    ),
                    "utilization": (
                        core.utilization
                        if core.current_process is not None
                        else 0.0
                    )
                })

        return self.execution_log
