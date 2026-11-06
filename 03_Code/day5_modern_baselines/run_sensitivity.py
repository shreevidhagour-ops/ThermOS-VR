"""
Migration / context-switch overhead sensitivity experiment.

Full factorial: migration cost x context-switch cost in {0, 0.1, 0.25, 0.5}
simulated work units, for every benchmark policy, the four original
workloads and both DVFS settings (16 x 8 x 4 x 2 = 1024 runs).
The overhead model is defined in overhead_engine.py.

Writes only to 05_Results/v2_sensitivity/ and refuses to replace existing
files unless --overwrite is given. The original 64-run benchmark is not
touched; its zero-overhead rows are re-derived here and cross-checked by
verify_sensitivity.py.
"""

import csv
import datetime
import gzip
import hashlib
import json
import os
import platform
import sys

from sim_engine import create_cores, GOVERNORS, DEFAULT_THERMAL_PARAMETERS
from overhead_engine import OverheadSimulator
from policies import BENCHMARK_POLICIES
from metrics_v2 import compute_metrics
from run_benchmark import WORKLOADS, DVFS_SETTINGS, PROJECT, HERE
from output_guard import parse_overwrite_flag, ensure_writable, environment_versions

OUTPUT_DIR = os.path.join(PROJECT, "05_Results", "v2_sensitivity")
COSTS = [0.0, 0.1, 0.25, 0.5]

OVERHEAD_MODEL = (
    "A dispatch event occurs when a task runs in tick t but did not run on the "
    "same core in tick t-1. First dispatch: no charge. Migration (last ran on a "
    "different core): migration_cost. Resume (last ran on the same core, not in "
    "the previous tick): context_switch_cost. Each event is charged once; a "
    "migration is never also charged as a context switch. The charge is added to "
    "the task's remaining work at dispatch, so the core spends that capacity "
    "busy (heating at the task's intensity) before the task progresses."
)


def run_one(policy_class, governor, workload_function, migration_cost,
            context_switch_cost):
    processes = workload_function()
    cores = create_cores()
    simulator = OverheadSimulator(
        processes, cores, policy_class(), GOVERNORS[governor](),
        migration_cost=migration_cost, context_switch_cost=context_switch_cost,
    )
    trace = simulator.run()
    return processes, trace, compute_metrics(processes, trace, len(cores))


def sha256(path):
    with open(path, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()


def main(overwrite=False):
    ensure_writable(OUTPUT_DIR, overwrite)

    summary, task_rows, trace_rows = [], [], []
    run_id = 0

    for migration_cost in COSTS:
        for context_switch_cost in COSTS:
            for governor in DVFS_SETTINGS:
                for workload_name, workload_function in WORKLOADS:
                    for policy_class in BENCHMARK_POLICIES:
                        run_id += 1
                        processes, trace, metrics = run_one(
                            policy_class, governor, workload_function,
                            migration_cost, context_switch_cost,
                        )
                        label = {
                            "Run ID": run_id,
                            "Migration Cost": migration_cost,
                            "Context Switch Cost": context_switch_cost,
                            "Policy": policy_class.name,
                            "Preemptive": policy_class.preemptive,
                            "DVFS": governor,
                            "Workload": workload_name,
                        }
                        summary.append({
                            **label,
                            **metrics,
                            "Migration Events Charged": sum(p.migration_events for p in processes),
                            "Resume Events Charged": sum(p.resume_events for p in processes),
                            "Total Overhead Work": sum(p.overhead_work for p in processes),
                        })
                        for p in processes:
                            task_rows.append({
                                **label,
                                "PID": p.pid, "Arrival": p.arrival_time,
                                "Burst": p.burst_time, "Deadline": p.deadline,
                                "Start": p.start_time, "Completion": p.completion_time,
                                "Waiting": p.waiting_time,
                                "Deadline Missed": p.deadline_missed,
                                "Busy Ticks": p.busy_ticks,
                                "Executed Work": round(p.executed_work, 9),
                                "Overhead Work": round(p.overhead_work, 9),
                                "Migration Events": p.migration_events,
                                "Resume Events": p.resume_events,
                                "Preemptions": p.preemptions,
                                "Migrations": p.migrations,
                            })
                        for row in trace:
                            trace_rows.append({
                                "Run ID": run_id, "time": row["time"],
                                "core": row["core"], "pid": row["pid"],
                                "busy": row["busy"],
                                "frequency_used": row["frequency_used"],
                                "temperature": row["temperature"],
                                "thermal_state": row["thermal_state"],
                            })

    def write(name, rows, opener=open):
        with opener(os.path.join(OUTPUT_DIR, name), "wt", newline="",
                    encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write("sensitivity_results.csv", summary)
    write("sensitivity_task_results.csv", task_rows)
    write("sensitivity_tick_trace.csv.gz", trace_rows, opener=gzip.open)

    sources = ["sim_engine.py", "overhead_engine.py", "policies.py",
               "metrics_v2.py", "run_benchmark.py", "run_sensitivity.py",
               "output_guard.py"]
    metadata = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "environment": environment_versions(),
        "runs": run_id,
        "migration_costs": COSTS,
        "context_switch_costs": COSTS,
        "cost_unit": "simulated work units (1.0 = one tick of work at 2.5 GHz)",
        "overhead_model": OVERHEAD_MODEL,
        "policies": [p.name for p in BENCHMARK_POLICIES],
        "dvfs_settings": DVFS_SETTINGS,
        "workloads": [name for name, _ in WORKLOADS],
        "thermal_parameters": DEFAULT_THERMAL_PARAMETERS,
        "source_sha256": {name: sha256(os.path.join(HERE, name)) for name in sources},
        "command": " ".join([os.path.basename(sys.executable)] + sys.argv),
        "platform": platform.platform(),
    }
    with open(os.path.join(OUTPUT_DIR, "sensitivity_metadata.json"), "w",
              encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"{run_id} runs written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main(parse_overwrite_flag("Run the overhead sensitivity experiment."))
