import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day2_thermal_model"
    )
)

from thermal_model import ThermalModel


class Core:
    def __init__(self, core_id, core_type="Performance"):
        self.core_id = core_id
        self.core_type = core_type

        # Initial thermal and performance state
        self.temperature = 45.0
        self.frequency = 2.5
        self.utilization = 0.0

        # Thermal model associated with this core
        self.thermal_model = ThermalModel(
            initial_temperature=self.temperature
        )

        # Task currently running on this core
        self.current_process = None

    def assign_process(self, process):
        self.current_process = process
        self.utilization = process.workload_intensity

    def release_process(self):
        self.current_process = None
        self.utilization = 0.0

    def update_temperature(self):
        if self.current_process is not None:
            workload = self.current_process.workload_intensity
            frequency = self.frequency
        else:
            workload = 0
            frequency = 0

        self.temperature = self.thermal_model.update_temperature(
            self.temperature,
            workload,
            frequency
        )

    def get_thermal_state(self):
        return self.thermal_model.get_thermal_state(
            self.temperature
        )

    def __str__(self):
        process_name = (
            self.current_process.name
            if self.current_process is not None
            else "Idle"
        )

        return (
            f"Core {self.core_id} | "
            f"Type: {self.core_type} | "
            f"Temperature: {self.temperature:.2f}°C | "
            f"Frequency: {self.frequency:.2f} GHz | "
            f"Task: {process_name} | "
            f"Thermal State: {self.get_thermal_state()}"
        )
