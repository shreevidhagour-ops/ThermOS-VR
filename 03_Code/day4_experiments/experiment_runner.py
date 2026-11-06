import csv
import os
import sys
import os

from simulation_engine import SimulationEngine
from metrics import MetricsCalculator


# Add Day 1 workload folder
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day1_basic_scheduler"
    )
)


# Add Day 3 scheduler folder
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "day3_thermos_scheduler"
    )
)


from workloads import (
    create_vr_workload,
    create_thermal_stress_workload,
    create_burst_vr_workload,
    create_sustained_thermal_workload,
    create_hot_thermal_workload,
    create_heterogeneous_thermal_workload,
    create_thermal_imbalance_workload
)

from core import Core

from baseline_schedulers import (
    FCFSScheduler,
    PriorityScheduler,
    RoundRobinScheduler
)

from scheduler import ThermOSVRScheduler
from thermal_dvfs_scheduler import ThermalDVFSScheduler


def create_cores():

    core1 = Core(
        core_id=1,
        core_type="Performance"
    )

    core2 = Core(
        core_id=2,
        core_type="Efficiency"
    )

    # Same starting temperature for every experiment
    core1.temperature = 45.0
    core2.temperature = 45.0

    return [core1, core2]


def run_scheduler(name, scheduler_class, workload_function):

    print("\n" + "=" * 60)
    print(f"Running: {name}")
    print("=" * 60)

    # Create a fresh workload
    processes = workload_function()

    # Create fresh cores
    cores = create_cores()

    # Create scheduler
    scheduler = scheduler_class(
        processes,
        cores
    )

    # Create common simulation environment
    engine = SimulationEngine(
        processes,
        cores,
        scheduler
    )

    # Run experiment
    execution_log = engine.run()

    print(f"Simulation completed: {name}")

    simulation_time = execution_log[-1]["time"]

    print(
        f"Simulation time: "
        f"{simulation_time} seconds"
    )

    # Calculate performance and thermal metrics
    metrics_calculator = MetricsCalculator(
        engine.get_processes(),
        execution_log
    )

    metrics = metrics_calculator.calculate_all()

    print("\n--- Metrics ---")

    print(
        f"Average Waiting Time: "
        f"{metrics['average_waiting_time']:.2f}"
    )

    print(
        f"Average Turnaround Time: "
        f"{metrics['average_turnaround_time']:.2f}"
    )

    print(
        f"Deadline Misses: "
        f"{metrics['deadline_misses']}"
    )

    print(
        f"Average Temperature: "
        f"{metrics['average_temperature']:.2f}°C"
    )

    print(
        f"Peak Temperature: "
        f"{metrics['peak_temperature']:.2f}°C"
    )

    print(
        f"Thermal Exposure Samples: "
        f"{metrics['thermal_exposure_samples']}"
    )

    print(
        f"Average CPU Utilization: "
        f"{metrics['average_cpu_utilization']:.2f}"
    )

    # ============================================================
    # SAVE RESULTS TO CSV
    # ============================================================

    results_directory = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "05_Results"
    )

    os.makedirs(
        results_directory,
        exist_ok=True
    )

    results_file = os.path.join(
        results_directory,
        "experiment_results.csv"
    )

    file_exists = os.path.isfile(results_file)

    with open(
        results_file,
        mode="a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Write header only when file is new
        if not file_exists:

            writer.writerow([
                "Experiment",
                "Scheduler",
                "Workload",
                "Simulation Time",
                "Average Waiting Time",
                "Average Turnaround Time",
                "Deadline Misses",
                "Average Temperature",
                "Peak Temperature",
                "Thermal Exposure Samples",
                "Average CPU Utilization"
            ])

        # Extract scheduler and workload names
        scheduler_name = name.split(" - ")[0]
        workload_name = name.split(" - ", 1)[1]

        writer.writerow([
            name,
            scheduler_name,
            workload_name,
            simulation_time,
            metrics["average_waiting_time"],
            metrics["average_turnaround_time"],
            metrics["deadline_misses"],
            metrics["average_temperature"],
            metrics["peak_temperature"],
            metrics["thermal_exposure_samples"],
            metrics["average_cpu_utilization"]
        ])

    print(
        f"Results saved to: {results_file}"
    )

    return scheduler, execution_log, metrics

def main():

    # ============================================================
    # RESET PREVIOUS EXPERIMENT RESULTS
    # ============================================================

    results_directory = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "05_Results"
    )

    os.makedirs(
        results_directory,
        exist_ok=True
    )

    results_file = os.path.join(
        results_directory,
        "experiment_results.csv"
    )

    if os.path.exists(results_file):
        os.remove(results_file)

    print("\n=== ThermOS-VR Experimental Runner ===")
    print("Previous experiment results cleared.")

    # ============================================================
    # 1. NORMAL VR WORKLOAD
    # ============================================================

    run_scheduler(
        "FCFS - Normal VR Workload",
        FCFSScheduler,
        create_vr_workload
    )

    run_scheduler(
        "Priority - Normal VR Workload",
        PriorityScheduler,
        create_vr_workload
    )

    run_scheduler(
        "Round Robin - Normal VR Workload",
        RoundRobinScheduler,
        create_vr_workload
    )

    run_scheduler(
        "Thermal-DVFS - Normal VR Workload",
        ThermalDVFSScheduler,
        create_vr_workload
    )

    run_scheduler(
        "ThermOS-VR - Normal VR Workload",
        ThermOSVRScheduler,
        create_vr_workload
    )


    # ============================================================
    # 2. BURST VR WORKLOAD
    # ============================================================

    run_scheduler(
        "FCFS - Burst VR Workload",
        FCFSScheduler,
        create_burst_vr_workload
    )

    run_scheduler(
        "Priority - Burst VR Workload",
        PriorityScheduler,
        create_burst_vr_workload
    )

    run_scheduler(
        "Round Robin - Burst VR Workload",
        RoundRobinScheduler,
        create_burst_vr_workload
    )

    run_scheduler(
        "Thermal-DVFS - Burst VR Workload",
        ThermalDVFSScheduler,
        create_burst_vr_workload
    )

    run_scheduler(
        "ThermOS-VR - Burst VR Workload",
        ThermOSVRScheduler,
        create_burst_vr_workload
    )


    # ============================================================
    # 3. SUSTAINED THERMAL WORKLOAD
    # ============================================================

    run_scheduler(
        "FCFS - Sustained Thermal Workload",
        FCFSScheduler,
        create_sustained_thermal_workload
    )

    run_scheduler(
        "Priority - Sustained Thermal Workload",
        PriorityScheduler,
        create_sustained_thermal_workload
    )

    run_scheduler(
        "Round Robin - Sustained Thermal Workload",
        RoundRobinScheduler,
        create_sustained_thermal_workload
    )

    run_scheduler(
        "Thermal-DVFS - Sustained Thermal Workload",
        ThermalDVFSScheduler,
        create_sustained_thermal_workload
    )

    run_scheduler(
        "ThermOS-VR - Sustained Thermal Workload",
        ThermOSVRScheduler,
        create_sustained_thermal_workload
    )


    # ============================================================
    # 4. HOT THERMAL WORKLOAD
    # ============================================================

    run_scheduler(
        "FCFS - HOT Thermal Workload",
        FCFSScheduler,
        create_hot_thermal_workload
    )

    run_scheduler(
        "Priority - HOT Thermal Workload",
        PriorityScheduler,
        create_hot_thermal_workload
    )

    run_scheduler(
        "Round Robin - HOT Thermal Workload",
        RoundRobinScheduler,
        create_hot_thermal_workload
    )

    run_scheduler(
        "Thermal-DVFS - HOT Thermal Workload",
        ThermalDVFSScheduler,
        create_hot_thermal_workload
    )

    run_scheduler(
        "ThermOS-VR - HOT Thermal Workload",
        ThermOSVRScheduler,
        create_hot_thermal_workload
    )


    # ============================================================
    # COMPLETED
    # ============================================================

    print("\n" + "=" * 60)
    print("ALL MAIN EXPERIMENTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
