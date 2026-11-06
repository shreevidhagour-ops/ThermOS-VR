import pandas as pd
import matplotlib.pyplot as plt
import os


# ============================================================
# PATHS
# ============================================================

base_directory = os.path.join(
    os.path.dirname(__file__),
    "..",
    ".."
)

results_file = os.path.join(
    base_directory,
    "05_Results",
    "experiment_results.csv"
)

figures_directory = os.path.join(
    base_directory,
    "06_Figures"
)

os.makedirs(
    figures_directory,
    exist_ok=True
)


# ============================================================
# LOAD RESULTS
# ============================================================

df = pd.read_csv(results_file)

print("\nResults loaded successfully.")
print(f"Number of experiments: {len(df)}")


# ============================================================
# SCHEDULER ORDER
# ============================================================

scheduler_order = [
    "FCFS",
    "Priority",
    "Round Robin",
    "Thermal-DVFS",
    "ThermOS-VR"
]


# ============================================================
# FUNCTION TO CREATE A GRAPH
# ============================================================

def create_graph(
    workload,
    metric,
    ylabel,
    filename,
    title
):

    data = df[
        df["Workload"] == workload
    ].copy()

    data["Scheduler"] = pd.Categorical(
        data["Scheduler"],
        categories=scheduler_order,
        ordered=True
    )

    data = data.sort_values("Scheduler")

    plt.figure(figsize=(10, 6))

    plt.bar(
        data["Scheduler"],
        data[metric]
    )

    plt.xlabel("Scheduler")
    plt.ylabel(ylabel)
    plt.title(title)

    plt.xticks(
        rotation=20
    )

    plt.tight_layout()

    output_file = os.path.join(
        figures_directory,
        filename
    )

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )


# ============================================================
# GENERATE FIGURES
# ============================================================

workloads = [
    "Normal VR Workload",
    "Burst VR Workload",
    "Sustained Thermal Workload",
    "HOT Thermal Workload"
]


for workload in workloads:

    safe_name = workload.lower().replace(
        " ",
        "_"
    )

    # --------------------------------------------------------
    # Average Temperature
    # --------------------------------------------------------

    create_graph(
        workload,
        "Average Temperature",
        "Average Temperature (°C)",
        f"{safe_name}_average_temperature.png",
        f"Average Temperature - {workload}"
    )

    # --------------------------------------------------------
    # Peak Temperature
    # --------------------------------------------------------

    create_graph(
        workload,
        "Peak Temperature",
        "Peak Temperature (°C)",
        f"{safe_name}_peak_temperature.png",
        f"Peak Temperature - {workload}"
    )

    # --------------------------------------------------------
    # Thermal Exposure
    # --------------------------------------------------------

    create_graph(
        workload,
        "Thermal Exposure Samples",
        "Thermal Exposure Samples",
        f"{safe_name}_thermal_exposure.png",
        f"Thermal Exposure - {workload}"
    )

    # --------------------------------------------------------
    # Deadline Misses
    # --------------------------------------------------------

    create_graph(
        workload,
        "Deadline Misses",
        "Deadline Misses",
        f"{safe_name}_deadline_misses.png",
        f"Deadline Misses - {workload}"
    )

    # --------------------------------------------------------
    # Average Waiting Time
    # --------------------------------------------------------

    create_graph(
        workload,
        "Average Waiting Time",
        "Average Waiting Time (s)",
        f"{safe_name}_waiting_time.png",
        f"Average Waiting Time - {workload}"
    )


# ============================================================
# COMPLETED
# ============================================================

print("\n" + "=" * 60)
print("ALL FIGURES GENERATED SUCCESSFULLY")
print("=" * 60)
