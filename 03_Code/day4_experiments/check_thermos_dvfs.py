from experiment_runner import run_scheduler
from scheduler import ThermOSVRScheduler


def main():

    scheduler, execution_log, metrics = run_scheduler(
        "ThermOS-VR",
        ThermOSVRScheduler
    )

    print("\n=== ThermOS-VR DVFS Transitions ===")

    previous_frequency = {}

    for entry in execution_log:
        core = entry["core"]
        frequency = entry["frequency"]

        if core not in previous_frequency:
            previous_frequency[core] = frequency

            print(
                f"Time: {entry['time']:3d}s | "
                f"Core: {core} | "
                f"Temperature: {entry['temperature']:.2f}°C | "
                f"Thermal State: {entry['thermal_state']} | "
                f"Frequency: {frequency:.2f} GHz"
            )

        elif frequency != previous_frequency[core]:
            print(
                f"Time: {entry['time']:3d}s | "
                f"Core: {core} | "
                f"Temperature: {entry['temperature']:.2f}°C | "
                f"Thermal State: {entry['thermal_state']} | "
                f"Frequency: {frequency:.2f} GHz"
            )

            previous_frequency[core] = frequency


if __name__ == "__main__":
    main()
