import sys
import os

# Add Day 1 code folder to Python path
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)

# Add Day 2 thermal model folder to Python path
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day2_thermal_model"
    )
)

from core import Core
from scheduler import ThermOSVRScheduler


def main():

    # Create a scheduler with one test core
    core = Core(
        core_id=1,
        core_type="Performance"
    )

    scheduler = ThermOSVRScheduler(
        [],
        [core]
    )

    print("=== ThermOS-VR DVFS Test ===\n")

    # Test different thermal states
    test_temperatures = [
        50.0,
        65.0,
        75.0,
        85.0
    ]

    for temperature in test_temperatures:

        core.temperature = temperature

        # Update frequency according to thermal state
        scheduler.update_frequency(core)

        print(
            f"Temperature: {core.temperature:.2f}°C | "
            f"Thermal State: {core.get_thermal_state()} | "
            f"Frequency: {core.frequency:.2f} GHz"
        )


if __name__ == "__main__":
    main()
