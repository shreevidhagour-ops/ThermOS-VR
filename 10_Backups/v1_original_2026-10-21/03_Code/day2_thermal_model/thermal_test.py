from thermal_model import ThermalModel


def main():
    thermal_model = ThermalModel()

    temperature = thermal_model.initial_temperature
    workload_intensity = 90
    frequency = 2.5

    print("=== Thermal Heating and Cooling Test ===")
    print(f"Initial Temperature: {temperature:.2f}°C")

    # Phase 1: High workload
    print("\n--- Phase 1: High Workload ---")

    for time in range(1, 11):
        temperature = thermal_model.update_temperature(
            temperature,
            workload_intensity,
            frequency
        )

        state = thermal_model.get_thermal_state(temperature)

        print(
            f"Time: {time}s | "
            f"Temperature: {temperature:.2f}°C | "
            f"State: {state}"
        )

    # Phase 2: Idle
    print("\n--- Phase 2: Core Idle ---")

    for time in range(11, 21):
        temperature = thermal_model.update_temperature(
            temperature,
            workload_intensity=0,
            frequency=0
        )

        state = thermal_model.get_thermal_state(temperature)

        print(
            f"Time: {time}s | "
            f"Temperature: {temperature:.2f}°C | "
            f"State: {state}"
        )


if __name__ == "__main__":
    main()
