import sys
import os
import copy

# Add Day 1 code folder
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)

# Add Day 2 thermal model folder
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day2_thermal_model"
    )
)

from core import Core
from thermal_model import ThermalModel


class SimulationEngine:

    def __init__(
        self,
        processes,
        cores,
        scheduler
    ):
        """
        Common simulation environment used to
        evaluate different scheduling algorithms.

        Every scheduler receives the same:
        - workload
        - core configuration
        - initial temperatures
        - thermal model
        """

        # Deep copy so that one experiment does not
        # modify the processes/cores used by another.
        self.processes = copy.deepcopy(processes)
        self.cores = copy.deepcopy(cores)

        # Scheduler object
        self.scheduler = scheduler

        # Simulation parameters
        self.current_time = 0
        self.time_step = 1

        # Execution history
        self.execution_log = []

    def reset_processes(self):
        """
        Reset runtime values of all processes.
        """

        for process in self.processes:

            process.start_time = None
            process.completion_time = None
            process.waiting_time = 0
            process.turnaround_time = 0
            process.remaining_time = process.burst_time
            process.executed_work = 0.0
            process.deadline_missed = False

    def reset_cores(self):
        """
        Reset runtime state of all cores.
        """

        for core in self.cores:

            core.current_process = None
            core.utilization = 0.0

            # Restore the thermal model using the same
            # thermal parameters for every experiment
            core.temperature = 45.0
            core.frequency = 2.5

            core.thermal_model = ThermalModel(
                ambient_temperature=25.0,
                initial_temperature=45.0,
                heat_coefficient=1.0,
                cooling_coefficient=0.02,
                reference_frequency=2.5
            )
    def log_state(self):
        """
        Record the current state of every core.
        """

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

    def run(self):
        """
        Run the selected scheduler using the
        common experimental environment.
        """

        # Reset simulation
        self.current_time = 0
        self.execution_log = []

        self.reset_processes()
        self.reset_cores()

        # Connect scheduler to this experiment's
        # independent process/core objects.
        self.scheduler.processes = self.processes
        self.scheduler.cores = self.cores

        # Reset scheduler-specific metrics
        if hasattr(self.scheduler, "thermal_violations"):
            self.scheduler.thermal_violations = 0

        if hasattr(self.scheduler, "throttling_events"):
            self.scheduler.throttling_events = 0

        # Run the scheduler
        self.execution_log = self.scheduler.run_simulation()

        return self.execution_log

    def get_processes(self):
        """
        Return the processes after simulation.
        """

        return self.processes

    def get_cores(self):
        """
        Return the cores after simulation.
        """

        return self.cores
