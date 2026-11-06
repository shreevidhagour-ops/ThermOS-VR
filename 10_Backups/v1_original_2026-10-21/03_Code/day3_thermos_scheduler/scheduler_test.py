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

from process import Process
from core import Core
from scheduler import ThermOSVRScheduler


def create_test_workload():

    processes = [

        Process(
            pid=1,
            name="Frame Rendering",
            arrival_time=0,
            burst_time=8,
            priority=1,
            workload_intensity=90,
            task_type="Rendering",
            deadline=10
        ),

        Process(
            pid=2,
            name="Motion Tracking",
            arrival_time=1,
            burst_time=4,
            priority=2,
            workload_intensity=70,
            task_type="Tracking",
            deadline=8
        ),

        Process(
            pid=3,
            name="Physics Engine",
            arrival_time=2,
            burst_time=6,
            priority=3,
            workload_intensity=80,
            task_type="Physics",
            deadline=12
        ),

        Process(
            pid=4,
            name="Sensor Processing",
            arrival_time=3,
            burst_time=3,
            priority=2,
            workload_intensity=60,
            task_type="Sensor",
            deadline=10
        ),

        Process(
            pid=5,
            name="Audio",
            arrival_time=4,
            burst_time=2,
            priority=4,
            workload_intensity=30,
            task_type="Audio",
            deadline=12
        ),

        Process(
            pid=6,
            name="Background",
            arrival_time=5,
            burst_time=5,
            priority=5,
            workload_intensity=20,
            task_type="Background",
            deadline=20
        )
    ]

    return processes


def main():

    # Create workload
    processes = create_test_workload()

    # Create two heterogeneous cores
    core1 = Core(
        core_id=1,
        core_type="Performance"
    )

    core2 = Core(
        core_id=2,
        core_type="Efficiency"
    )

    # Start cores at different temperatures
    core1.temperature = 65.0
    core2.temperature = 45.0

    # Create ThermOS-VR scheduler
    scheduler = ThermOSVRScheduler(
        processes,
        [core1, core2]
    )

    print("=== ThermOS-VR Scheduler Test ===\n")

    # -------------------------------------------------
    # INITIAL CORE STATES
    # -------------------------------------------------

    print("Initial Core States:")

    print(core1)
    print(core2)

    # -------------------------------------------------
    # RUN SCHEDULER
    # -------------------------------------------------

    print("\n--- Scheduling Decisions ---")

    execution_log = scheduler.run_simulation()

    # -------------------------------------------------
    # THERMAL TIMELINE
    # -------------------------------------------------

    print("\n--- Thermal Timeline ---")

    for entry in execution_log:

        print(
            f"Time: {entry['time']}s | "
            f"Core: {entry['core']} | "
            f"Process: {entry['process']} | "
            f"Temperature: {entry['temperature']:.2f}°C | "
            f"Frequency: {entry['frequency']:.2f} GHz | "
            f"State: {entry['thermal_state']}"
        )

    # -------------------------------------------------
    # THERMAL PROTECTION METRICS
    # -------------------------------------------------

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
