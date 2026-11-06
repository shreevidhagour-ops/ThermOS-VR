"""
Shared setup for the working replacements of the broken v1 scripts.

The v1 files are frozen by the project's SHA-256 manifests, so they stay
unchanged. Importing experiment_runner is safe: it only deletes the results
file from its main(), which is never called here.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(HERE)
PROJECT = os.path.dirname(CODE_DIR)
FROZEN_RESULTS = os.path.join(PROJECT, "05_Results", "experiment_results.csv")

sys.path.insert(0, os.path.join(CODE_DIR, "day4_experiments"))

import experiment_runner as runner  # noqa: E402

WORKLOADS = {
    "Normal VR Workload": runner.create_vr_workload,
    "Burst VR Workload": runner.create_burst_vr_workload,
    "Sustained Thermal Workload": runner.create_sustained_thermal_workload,
    "HOT Thermal Workload": runner.create_hot_thermal_workload,
}

SCHEDULERS = {
    "FCFS": runner.FCFSScheduler,
    "Priority": runner.PriorityScheduler,
    "Round Robin": runner.RoundRobinScheduler,
    "Thermal-DVFS": runner.ThermalDVFSScheduler,
    "ThermOS-VR": runner.ThermOSVRScheduler,
}


def run_experiment(scheduler_name, workload_name):
    """Run one v1 experiment and return (execution_log, metrics). Writes no files."""
    processes = WORKLOADS[workload_name]()
    cores = runner.create_cores()
    scheduler = SCHEDULERS[scheduler_name](processes, cores)
    engine = runner.SimulationEngine(processes, cores, scheduler)
    execution_log = engine.run()
    metrics = runner.MetricsCalculator(
        engine.get_processes(), execution_log
    ).calculate_all()
    return execution_log, metrics
