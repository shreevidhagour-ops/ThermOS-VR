import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)

from core import Core
from workloads import create_vr_workload


def main():

    # Create a core
    core = Core(core_id=1, core_type="Performance")

    # Create AR/VR workload
    processes = create_vr_workload()

    # Select Frame Rendering
    process = processes[0]

    print("=== Core Thermal Integration Test ===\n")

    print("Initial Core State:")
    print(core)

    # Assign process
    core.assign_process(process)

    print("\n--- Frame Rendering Running ---")

    for time in range(1, 11):

        core.update_temperature()

        print(
            f"Time: {time}s | "
            f"Temperature: {core.temperature:.2f}°C | "
            f"State: {core.get_thermal_state()}"
        )

    # Release process
    core.release_process()

    print("\n--- Core Idle ---")

    for time in range(11, 21):

        core.update_temperature()

        print(
            f"Time: {time}s | "
            f"Temperature: {core.temperature:.2f}°C | "
            f"State: {core.get_thermal_state()}"
        )


if __name__ == "__main__":
    main()
