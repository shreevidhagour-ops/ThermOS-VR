import sys
import os

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day2_thermal_model"
    )
)

from process import Process
from core import Core
from scheduler import ThermOSVRScheduler


def create_stress_workload():

    processes = [
        Process(
            pid=1,
            name="Heavy VR Rendering",
            arrival_time=0,
            burst_time=30,
            priority=1,
            workload_intensity=100,
            task_type="Rendering",
            deadline=40
        ),

        Process(
            pid=2,
            name="VR Physics",
            arrival_time=0,
            burst_time=25,
            priority=2,
            workload_intensity=100,
            task_type="Physics",
            deadline=40
        ),

        Process(
            pid=3,
            name="High Load Tracking",
            arrival_time=0,
            burst_time=20,
            priority=3,
            workload_intensity=95,
            task_type="Tracking",
            deadline=45
        )
    ]

    return processes


def main():

    processes = create_stress_workload()

    # Start both cores at elevated temperatures
    core1 = Core(
        core_id=1,
        core_type="Performance"
    )

    core2 = Core(
        core_id=2,
        core_type="Efficiency"
    )

    core1.temperature = 78.0
    core2.temperature = 78.0

    scheduler = ThermOSVRScheduler(
        processes,
        [core1, core2]
    )

    print("=== ThermOS-VR Thermal Stress Test ===\n")

    print("Initial Core States:")

    print(core1)
    print(core2)

    print("\n--- Running High-Intensity VR Workload ---")

    execution_log = scheduler.run_simulation()

    print("\n--- Thermal Timeline ---")

    for entry in execution_log:

        if entry["thermal_state"] in ["HOT", "CRITICAL"]:

            print(
                f"Time: {entry['time']}s | "
                f"Core: {entry['core']} | "
                f"Process: {entry['process']} | "
                f"Temperature: {entry['temperature']:.2f}°C | "
                f"State: {entry['thermal_state']}"
            )

    print("\n=== Thermal Protection Metrics ===")

    print(
        f"Thermal Violations: "
        f"{scheduler.thermal_violations}"
    )

    print(
        f"Throttling Events: "
        f"{scheduler.throttling_events}"
    )


if __name__ == "__main__":
    main()
