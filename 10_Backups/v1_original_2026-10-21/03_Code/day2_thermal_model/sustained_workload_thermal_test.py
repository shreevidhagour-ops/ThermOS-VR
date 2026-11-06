import sys
import os

# Add Day 1 workload folder
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)

from thermal_model import ThermalModel
from workloads import create_sustained_thermal_workload


def main():

    processes = create_sustained_thermal_workload()

    thermal_model = ThermalModel(
        ambient_temperature=25.0,
        initial_temperature=45.0,
        heat_coefficient=1.0,
        cooling_coefficient=0.02,
        reference_frequency=2.5
    )

    temperature = 45.0

    print("=== Sustained Thermal Workload Test ===")
    print("Initial Temperature: 45.0°C")
    print()

    # Use the highest sustained workload as a thermal
    # upper-pressure sanity check.
    workload_intensity = 100
    frequency = 2.5

    first_warm = None
    first_hot = None
    first_critical = None

    for time in range(1, 121):

        temperature = thermal_model.update_temperature(
            temperature,
            workload_intensity,
            frequency
        )

        state = thermal_model.get_thermal_state(
            temperature
        )

        if state == "WARM" and first_warm is None:
            first_warm = time

        if state == "HOT" and first_hot is None:
            first_hot = time

        if state == "CRITICAL" and first_critical is None:
            first_critical = time

        print(
            f"Time: {time:3d}s | "
            f"Temperature: {temperature:6.2f}°C | "
            f"State: {state}"
        )

    print("\n=== Thermal Threshold Summary ===")

    print(
        f"First WARM state: "
        f"{first_warm if first_warm is not None else 'Not reached'}"
    )

    print(
        f"First HOT state: "
        f"{first_hot if first_hot is not None else 'Not reached'}"
    )

    print(
        f"First CRITICAL state: "
        f"{first_critical if first_critical is not None else 'Not reached'}"
    )


if __name__ == "__main__":
    main()
