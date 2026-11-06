from thermal_model import ThermalModel


def main():

    thermal_model = ThermalModel(
        ambient_temperature=25.0,
        initial_temperature=45.0,
        heat_coefficient=1.0,
        cooling_coefficient=0.02,
        reference_frequency=2.5
    )

    temperature = 45.0

    print("=== Thermal Ramp Test ===")
    print("Workload: 100%")
    print("Frequency: 2.5 GHz")
    print("Initial Temperature: 45.0°C")
    print()

    for time in range(1, 61):

        temperature = thermal_model.update_temperature(
            temperature,
            workload_intensity=100,
            frequency=2.5
        )

        state = thermal_model.get_thermal_state(
            temperature
        )

        print(
            f"Time: {time:2d}s | "
            f"Temperature: {temperature:6.2f}°C | "
            f"State: {state}"
        )


if __name__ == "__main__":
    main()
