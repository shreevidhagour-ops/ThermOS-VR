import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DAY1_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "day1_basic_scheduler")
)

DAY2_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "day2_thermal_model")
)

for path in [DAY1_DIR, DAY2_DIR]:
    if path not in sys.path:
        sys.path.append(path)

from workloads import create_sustained_thermal_workload
from core import Core


def apply_hysteresis_dvfs(core):
    """
    Thermal-aware DVFS with hysteresis.

    2.50 GHz -> 2.20 GHz when temperature reaches 60°C.
    2.20 GHz -> 2.50 GHz only when temperature falls to 58°C.
    """

    if core.frequency == 2.50 and core.temperature >= 60:
        core.frequency = 2.20

    elif core.frequency == 2.20 and core.temperature <= 58:
        core.frequency = 2.50


def main():

    processes = create_sustained_thermal_workload()

    core = Core(1, "Performance")

    # Use the first sustained high-intensity workload
    process = processes[0]

    core.assign_process(process)

    print("\n=== Hysteresis DVFS Test ===")

    previous_frequency = core.frequency

    for time in range(125):

        # Apply DVFS before execution
        apply_hysteresis_dvfs(core)

        # Execute one second
        core.update_temperature()

        # Apply DVFS after temperature update
        apply_hysteresis_dvfs(core)

        if core.frequency != previous_frequency:

            print(
                f"Time: {time + 1:3d}s | "
                f"Temperature: {core.temperature:.2f}°C | "
                f"Thermal State: {core.get_thermal_state()} | "
                f"Frequency: {core.frequency:.2f} GHz"
            )

            previous_frequency = core.frequency

    print("\nFinal State:")
    print(
        f"Temperature: {core.temperature:.2f}°C | "
        f"Thermal State: {core.get_thermal_state()} | "
        f"Frequency: {core.frequency:.2f} GHz"
    )


if __name__ == "__main__":
    main()
