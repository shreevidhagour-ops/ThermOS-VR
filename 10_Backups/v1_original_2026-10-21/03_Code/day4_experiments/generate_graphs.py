import os
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

base_directory = os.path.dirname(__file__)

results_file = os.path.join(
    base_directory,
    "..",
    "..",
    "05_Results",
    "experiment_results.csv"
)

figures_directory = os.path.join(
    base_directory,
    "..",
    "..",
    "06_Figures"
)

os.makedirs(figures_directory, exist_ok=True)


# ============================================================
# LOAD RESULTS
# ============================================================

data = pd.read_csv(results_file)

print("Results loaded successfully.")
print(data)


# ============================================================
# FUNCTION TO CREATE A GRAPH
# ============================================================

def create_graph(workload_name, metric, ylabel, filename):

    workload_data = data[
        data["Workload"] == workload_name
    ]

    schedulers = workload_data["Scheduler"]
    values = workload_data[metric]

    plt.figure(figsize=(10, 6))

    plt.bar(
        schedulers,
        values
    )

    plt.xlabel("Scheduling Algorithm")
    plt.ylabel(ylabel)

    plt.title(
        f"{ylabel} - {workload_name}"
    )

    plt.xticks(
        rotation=25,
        ha="right"
    )

    plt.tight_layout()

    output_path = os.path.join(
        figures_directory,
        filename
    )

    plt.savefig(
        output_path,
        dpi=300
    )

    plt.close()

    print(f"Saved: {output_path}")


# ============================================================
# 1. AVERAGE TEMPERATURE
# ============================================================

create_graph(
    "HOT Thermal Workload",
    "Average Temperature",
    "Average Temperature (°C)",
    "hot_average_temperature.png"
)


# ============================================================
# 2. PEAK TEMPERATURE
# ============================================================

create_graph(
    "HOT Thermal Workload",
    "Peak Temperature",
    "Peak Temperature (°C)",
    "hot_peak_temperature.png"
)


# ============================================================
# 3. AVERAGE WAITING TIME
# ============================================================

create_graph(
    "HOT Thermal Workload",
    "Average Waiting Time",
    "Average Waiting Time (s)",
    "hot_waiting_time.png"
)


print("\n=== GRAPH GENERATION COMPLETED ===")
