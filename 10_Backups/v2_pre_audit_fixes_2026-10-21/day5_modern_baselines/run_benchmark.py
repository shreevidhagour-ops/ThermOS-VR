"""
ThermOS-VR v2 benchmark.

Runs every policy in policies.BENCHMARK_POLICIES on the four original
workloads under two DVFS settings ("off" and the corrected
"hysteresis" governor), using the unified engine.

Outputs (v1 files are never touched):
    05_Results/v2_modern_baselines/benchmark_results.csv   one row per run
    05_Results/v2_modern_baselines/task_results.csv        one row per task per run
    05_Results/v2_modern_baselines/tick_trace.csv          one row per core per tick per run
    05_Results/v2_modern_baselines/metric_definitions.csv
    05_Results/v2_modern_baselines/run_metadata.json
"""

import csv
import datetime
import hashlib
import json
import os
import platform
import sys

from sim_engine import Simulator, create_cores, GOVERNORS, DEFAULT_THERMAL_PARAMETERS
from policies import BENCHMARK_POLICIES
from metrics_v2 import compute_metrics, METRIC_DEFINITIONS

import workloads as W


HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUTPUT_DIR = os.path.join(PROJECT, "05_Results", "v2_modern_baselines")
V1_RESULTS = os.path.join(PROJECT, "05_Results", "experiment_results.csv")

WORKLOADS = [
    ("Normal VR Workload", W.create_vr_workload),
    ("Burst VR Workload", W.create_burst_vr_workload),
    ("Sustained Thermal Workload", W.create_sustained_thermal_workload),
    ("HOT Thermal Workload", W.create_hot_thermal_workload),
]

DVFS_SETTINGS = ["off", "hysteresis"]

SOURCE_FILES = [
    os.path.join(HERE, name)
    for name in ("sim_engine.py", "policies.py", "metrics_v2.py", "run_benchmark.py")
] + [
    os.path.join(HERE, "..", "day1_basic_scheduler", name)
    for name in ("process.py", "core.py", "workloads.py")
] + [
    os.path.join(HERE, "..", "day2_thermal_model", "thermal_model.py"),
]


def sha256(path):
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_one(policy_class, governor_name, workload_function):
    processes = workload_function()
    cores = create_cores()
    simulator = Simulator(
        processes, cores, policy_class(), GOVERNORS[governor_name]()
    )
    trace = simulator.run()
    return simulator.processes, trace, compute_metrics(processes, trace, len(cores))


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    v1_hash_before = sha256(V1_RESULTS)

    summary_rows, task_rows, trace_rows = [], [], []
    run_id = 0

    for governor in DVFS_SETTINGS:
        for workload_name, workload_function in WORKLOADS:
            for policy_class in BENCHMARK_POLICIES:
                run_id += 1
                processes, trace, metrics = run_one(
                    policy_class, governor, workload_function
                )
                label = {
                    "Run ID": run_id,
                    "Policy": policy_class.name,
                    "Preemptive": policy_class.preemptive,
                    "DVFS": governor,
                    "Workload": workload_name,
                }
                summary_rows.append({**label, **metrics})

                for p in processes:
                    task_rows.append({
                        **label,
                        "PID": p.pid,
                        "Task": p.name,
                        "Arrival": p.arrival_time,
                        "Burst": p.burst_time,
                        "Priority": p.priority,
                        "Intensity": p.workload_intensity,
                        "Deadline": p.deadline,
                        "Start": p.start_time,
                        "Completion": p.completion_time,
                        "Waiting": p.waiting_time,
                        "Turnaround": p.turnaround_time,
                        "Response": p.response_time,
                        "Deadline Missed": p.deadline_missed,
                        "Busy Ticks": p.busy_ticks,
                        "Executed Work": round(p.executed_work, 9),
                        "Preemptions": p.preemptions,
                        "Migrations": p.migrations,
                    })

                for row in trace:
                    trace_rows.append({"Run ID": run_id, **row})

                print(
                    f"[{run_id:2d}] {governor:10s} {workload_name:27s} "
                    f"{policy_class.name:15s} makespan={metrics['Makespan']:4d} "
                    f"wait={metrics['Average Waiting Time']:7.2f} "
                    f"miss={metrics['Deadline Misses']} "
                    f"peak={metrics['Peak Temperature']:.2f}"
                )

    write_csv(os.path.join(OUTPUT_DIR, "benchmark_results.csv"), summary_rows)
    write_csv(os.path.join(OUTPUT_DIR, "task_results.csv"), task_rows)
    write_csv(os.path.join(OUTPUT_DIR, "tick_trace.csv"), trace_rows)
    write_csv(
        os.path.join(OUTPUT_DIR, "metric_definitions.csv"),
        [{"Metric": k, "Definition": v} for k, v in METRIC_DEFINITIONS.items()],
    )

    if sha256(V1_RESULTS) != v1_hash_before:
        raise RuntimeError("v1 results file changed during the benchmark")

    metadata = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "python": sys.version,
        "platform": platform.platform(),
        "runs": run_id,
        "policies": [p.name for p in BENCHMARK_POLICIES],
        "dvfs_settings": DVFS_SETTINGS,
        "workloads": [name for name, _ in WORKLOADS],
        "thermal_parameters": DEFAULT_THERMAL_PARAMETERS,
        "cores": "2 (labels Performance/Efficiency; physically identical)",
        "source_sha256": {
            os.path.relpath(path, PROJECT): sha256(path) for path in SOURCE_FILES
        },
        "v1_results_sha256_unchanged": v1_hash_before,
    }

    with open(os.path.join(OUTPUT_DIR, "run_metadata.json"), "w",
              encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"\n{run_id} runs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
