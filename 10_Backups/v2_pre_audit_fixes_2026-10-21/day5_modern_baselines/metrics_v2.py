"""
Metric definitions for ThermOS-VR v2. Every policy is measured from the
same task records and the same per-tick trace (one row per core per tick,
covering ticks 1..makespan; the t=0 initial state is not a sample).
"""

from sim_engine import REFERENCE_FREQUENCY

HOT_STATES = ("HOT", "CRITICAL")
WARM_THRESHOLD = 60.0  # COOL/WARM boundary and first DVFS throttle point

# Column name -> one-line definition (exported alongside the CSV).
METRIC_DEFINITIONS = {
    "Average Waiting Time": "Mean over tasks of ticks spent arrived, unfinished and not running (includes time after preemption).",
    "Average Turnaround Time": "Mean over tasks of completion time - arrival time.",
    "Average Completion Time": "Mean over tasks of absolute completion time.",
    "Average Response Time": "Mean over tasks of first dispatch time - arrival time.",
    "Makespan": "Completion time of the last task (simulation length).",
    "Deadline Misses": "Number of tasks with completion time > absolute deadline.",
    "Total Tardiness": "Sum over tasks of max(0, completion time - deadline).",
    "Average Temperature": "Mean simulated temperature over all core-ticks 1..makespan (°C).",
    "Peak Temperature": "Maximum simulated temperature over all core-ticks (°C).",
    "Thermal Exposure (HOT core-ticks)": "Number of core-ticks ending in HOT or CRITICAL state (>= 70 °C).",
    "Core-ticks >= 60C": "Number of core-ticks ending at or above 60 °C (WARM or hotter).",
    "Throttled Busy Core-ticks": "Busy core-ticks executed below 2.5 GHz.",
    "Heat Generated (model units)": "Sum of the thermal model heat term (w/100)*(f/2.5)^2 over all core-ticks; a relative thermal-load proxy, not joules.",
    "Core-time Utilization (%)": "Busy core-ticks / (cores * makespan) * 100.",
    "Preemptions": "Times a running, unfinished task lost its core without moving to another core.",
    "Migrations": "Times a task resumed on a different core than it last ran on.",
}


def compute_metrics(processes, trace, num_cores):
    n = len(processes)
    makespan = max(p.completion_time for p in processes)
    temperatures = [row["temperature"] for row in trace]
    busy_rows = [row for row in trace if row["busy"]]

    return {
        "Average Waiting Time": sum(p.waiting_time for p in processes) / n,
        "Average Turnaround Time": sum(p.turnaround_time for p in processes) / n,
        "Average Completion Time": sum(p.completion_time for p in processes) / n,
        "Average Response Time": sum(p.response_time for p in processes) / n,
        "Makespan": makespan,
        "Deadline Misses": sum(1 for p in processes if p.deadline_missed),
        "Total Tardiness": sum(max(0, p.completion_time - p.deadline) for p in processes),
        "Average Temperature": sum(temperatures) / len(temperatures),
        "Peak Temperature": max(temperatures),
        "Thermal Exposure (HOT core-ticks)": sum(1 for r in trace if r["thermal_state"] in HOT_STATES),
        "Core-ticks >= 60C": sum(1 for r in trace if r["temperature"] >= WARM_THRESHOLD),
        "Throttled Busy Core-ticks": sum(1 for r in busy_rows if r["frequency_used"] < REFERENCE_FREQUENCY),
        "Heat Generated (model units)": sum(r["heat"] for r in trace),
        "Core-time Utilization (%)": len(busy_rows) / (num_cores * makespan) * 100.0,
        "Preemptions": sum(p.preemptions for p in processes),
        "Migrations": sum(p.migrations for p in processes),
    }
