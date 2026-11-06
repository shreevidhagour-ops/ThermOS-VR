class ThermalModel:
    def __init__(
        self,
        ambient_temperature=25.0,
        initial_temperature=45.0,
        heat_coefficient=1.0,
        cooling_coefficient=0.02,
        reference_frequency=2.5
    ):
        self.ambient_temperature = ambient_temperature
        self.initial_temperature = initial_temperature
        self.heat_coefficient = heat_coefficient
        self.cooling_coefficient = cooling_coefficient
        self.reference_frequency = reference_frequency

    def calculate_heat(self, workload_intensity, frequency):
        workload_factor = workload_intensity / 100.0
        frequency_factor = frequency / self.reference_frequency

        heat = (
            self.heat_coefficient
            * workload_factor
            * (frequency_factor ** 2)
        )

        return heat

    def calculate_cooling(self, temperature):
        cooling = (
            self.cooling_coefficient
            * (temperature - self.ambient_temperature)
        )

        return max(cooling, 0.0)

    def update_temperature(
        self,
        temperature,
        workload_intensity,
        frequency
    ):
        heat = self.calculate_heat(
            workload_intensity,
            frequency
        )

        cooling = self.calculate_cooling(temperature)

        new_temperature = temperature + heat - cooling

        return new_temperature

    def get_thermal_state(self, temperature):
        if temperature < 60:
            return "COOL"
        elif temperature < 70:
            return "WARM"
        elif temperature < 80:
            return "HOT"
        else:
            return "CRITICAL"
