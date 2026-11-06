class FCFSScheduler:
    """
    First-Come, First-Served scheduler.

    Non-preemptive baseline.
    """

    def __init__(self, processes, cores):
        self.processes = processes
        self.cores = cores

        self.execution_log = []

        self.thermal_violations = 0
        self.throttling_events = 0

    def select_core(self):
        """
        Select the first available core.
        """

        for core in self.cores:

            if core.current_process is None:
                return core

        return None

    def run_simulation(self):

        current_time = 0
        completed_processes = []

        self.execution_log = []

        # Initial state
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

        while len(completed_processes) < len(self.processes):

            # -----------------------------------------
            # Schedule arrived processes
            # -----------------------------------------

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

            # FCFS order
            ready_processes.sort(
                key=lambda process: process.arrival_time
            )

            for process in ready_processes:

                selected_core = self.select_core()

                if selected_core is None:
                    break

                if process.start_time is None:

                    process.start_time = current_time

                    process.waiting_time = (
                        current_time
                        - process.arrival_time
                    )

                selected_core.assign_process(process)

            # -----------------------------------------
            # Execute for one second
            # -----------------------------------------

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    process.remaining_time -= 1

                    core.update_temperature()

                else:

                    core.update_temperature()

            # -----------------------------------------
            # Advance time
            # -----------------------------------------

            current_time += 1

            # -----------------------------------------
            # Complete processes
            # -----------------------------------------

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

            # -----------------------------------------
            # Log current state
            # -----------------------------------------

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
                    "thermal_state": core.get_thermal_state(),
                    "utilization": (
                        core.utilization
                        if core.current_process is not None
                        else 0.0
                    )
                })

        return self.execution_log


class PriorityScheduler:
    """
    Non-preemptive priority scheduler.

    Lower priority number = higher priority.
    """

    def __init__(self, processes, cores):
        self.processes = processes
        self.cores = cores

        self.execution_log = []

        self.thermal_violations = 0
        self.throttling_events = 0

    def select_core(self):

        for core in self.cores:

            if core.current_process is None:
                return core

        return None

    def run_simulation(self):

        current_time = 0
        completed_processes = []

        self.execution_log = []

        # Initial state
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
        while len(completed_processes) < len(self.processes):

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

            # Highest priority first
            ready_processes.sort(
                key=lambda process: (
                    process.priority,
                    process.arrival_time
                )
            )

            for process in ready_processes:

                selected_core = self.select_core()

                if selected_core is None:
                    break

                if process.start_time is None:

                    process.start_time = current_time

                    process.waiting_time = (
                        current_time
                        - process.arrival_time
                    )

                selected_core.assign_process(process)

            # Execute
            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    process.remaining_time -= 1

                    core.update_temperature()

                else:

                    core.update_temperature()

            current_time += 1

            # Complete
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

            # Log
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
                    "thermal_state": core.get_thermal_state(),
                    "utilization": (
                        core.utilization
                        if core.current_process is not None
                        else 0.0
                    )
                })
        return self.execution_log


class RoundRobinScheduler:
    """
    Round Robin scheduler.

    Uses a one-second time quantum.
    """

    def __init__(
        self,
        processes,
        cores,
        time_quantum=1
    ):
        self.processes = processes
        self.cores = cores

        self.time_quantum = time_quantum

        self.execution_log = []

        self.thermal_violations = 0
        self.throttling_events = 0

    def run_simulation(self):

        current_time = 0
        completed_processes = []

        ready_queue = []

        self.execution_log = []

        waiting_start = {}

        # ==================================================
        # MAIN SIMULATION LOOP
        # ==================================================

        while len(completed_processes) < len(self.processes):

            # ==================================================
            # STEP 1: Add newly arrived processes
            # ==================================================

            for process in self.processes:

                if (
                    process.arrival_time <= current_time
                    and process.remaining_time > 0
                    and process not in completed_processes
                    and process not in ready_queue
                    and not any(
                        core.current_process == process
                        for core in self.cores
                    )
                ):

                    ready_queue.append(process)

                    if process not in waiting_start:
                        waiting_start[process] = current_time

            # ==================================================
            # STEP 2: Assign processes to idle cores
            # ==================================================

            for core in self.cores:

                if (
                    core.current_process is None
                    and ready_queue
                ):

                    process = ready_queue.pop(0)

                    # Add time spent waiting in the ready queue
                    if process in waiting_start:

                        process.waiting_time += (
                            current_time
                            - waiting_start[process]
                        )

                        del waiting_start[process]

                    # Record first response time
                    if process.start_time is None:
                        process.start_time = current_time

                    core.assign_process(process)

            # ==================================================
            # STEP 3: Execute one second
            # ==================================================

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    process.remaining_time -= self.time_quantum

                    core.update_temperature()

                else:

                    core.update_temperature()

            # ==================================================
            # STEP 4: Advance simulation time
            # ==================================================

            current_time += self.time_quantum

                        # ==================================================
            # STEP 5: Record POST-EXECUTION state
            #
            # The temperature has already been updated and
            # simulation time has advanced.
            #
            # We capture the process that executed this quantum
            # BEFORE releasing it from the core.
            # ==================================================

            post_execution_states = []

            for core in self.cores:

                if core.current_process is not None:

                    process = core.current_process

                    post_execution_states.append({
                        "time": current_time,
                        "core": core.core_id,
                        "process": process.name,
                        "temperature": core.temperature,
                        "frequency": core.frequency,
                        "thermal_state": core.get_thermal_state(),
                        "utilization": core.utilization
                    })

                else:

                    post_execution_states.append({
                        "time": current_time,
                        "core": core.core_id,
                        "process": "Idle",
                        "temperature": core.temperature,
                        "frequency": core.frequency,
                        "thermal_state": core.get_thermal_state(),
                        "utilization": 0.0
                    })

            # Add the captured post-execution states to the log
            self.execution_log.extend(post_execution_states)

            # ==================================================
            # STEP 6: Check process completion / quantum expiry
            # ==================================================

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

                    else:

                        # Quantum expired.
                        # Put process back into the ready queue.

                        ready_queue.append(process)

                        waiting_start[process] = current_time

                        core.release_process()

        return self.execution_log
