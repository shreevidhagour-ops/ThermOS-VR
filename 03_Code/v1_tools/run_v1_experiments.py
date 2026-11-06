"""
Safe replacement for day4_experiments/experiment_runner.py (bug B11).

Runs the same 20 v1 experiments in the same order and writes the same CSV
format, but only to the file named by --output. It deletes nothing, refuses to
replace an existing file without --overwrite, and never writes to the frozen
05_Results/experiment_results.csv.

The Thermal-DVFS rows reproduce a known v1 bug (B1) and are not a valid baseline.
"""

import argparse
import contextlib
import csv
import io
import os
import sys

from v1_common import FROZEN_RESULTS, SCHEDULERS, WORKLOADS, run_experiment

HEADER = [
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
    "Average CPU Utilization",
]


def build_rows():
    rows = []
    for workload in WORKLOADS:
        for scheduler in SCHEDULERS:
            # v1 schedulers print per-tick progress
            with contextlib.redirect_stdout(io.StringIO()):
                execution_log, metrics = run_experiment(scheduler, workload)
            rows.append([
                f"{scheduler} - {workload}",
                scheduler,
                workload,
                execution_log[-1]["time"],
                metrics["average_waiting_time"],
                metrics["average_turnaround_time"],
                metrics["deadline_misses"],
                metrics["average_temperature"],
                metrics["peak_temperature"],
                metrics["thermal_exposure_samples"],
                metrics["average_cpu_utilization"],
            ])
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--output", required=True, help="CSV file to write")
    parser.add_argument(
        "--overwrite", action="store_true",
        help="allow replacing an existing output file (never the frozen results)",
    )
    args = parser.parse_args()

    output = os.path.abspath(args.output)

    if os.path.normcase(output) == os.path.normcase(os.path.abspath(FROZEN_RESULTS)):
        print(f"REFUSING TO WRITE: {output} is frozen evidence.", file=sys.stderr)
        return 2

    if os.path.exists(output) and not args.overwrite:
        print(
            f"REFUSING TO WRITE: {output} already exists. Nothing was changed.\n"
            f"Re-run with --overwrite to replace it.",
            file=sys.stderr,
        )
        return 2

    rows = build_rows()

    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"{len(rows)} experiments written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
