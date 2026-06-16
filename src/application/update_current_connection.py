"""Contains functions to calculate the updated energy dto's for the scenario's with and without EnergyPod."""

from src.application.load_balancing import LoadBalancingOrchestrator
from src.application.small_consumer_connection import small_consumer_connection_ranges
from src.domain.connection_power import ConnectionFits
from src.domain.energy_dto import (
    EnergyDTOLargeConsumer,
    EnergyDTOLargeConsumerCLC,
    EnergyDTOSmallConsumer,
    EnergyDTOUpdate,
)


class UpdateCurrentConnection:
    """Updates the current connection based on load balancing of the vehicle energy demand."""

    def __init__(self, energy_dto: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC) -> None:
        """Initializes the UpdateCurrentConnection class."""
        self.energy_dto = energy_dto

    def map_small_connection_increase_to_new_connection(
        self, energy_dto: EnergyDTOSmallConsumer, connection_update: float
    ) -> EnergyDTOSmallConsumer | EnergyDTOLargeConsumer:
        """Maps the connection increase to the correct connection category."""
        current_connection_power = energy_dto.calculate_contracted_capacity()
        updated_connection_power = (current_connection_power + connection_update) * 1.15

        for connection_range in small_consumer_connection_ranges():
            if (updated_connection_power >= connection_range.min_connection_power) and (
                updated_connection_power <= connection_range.max_connection_power
            ):
                energy_dto.update_connection_category(connection_range.connection_type.value)
                return energy_dto

        return EnergyDTOLargeConsumer(
            vehicle_info=energy_dto.vehicle_info,
            arrival_time=energy_dto.arrival_time,
            departure_time=energy_dto.departure_time,
            baseload=energy_dto.baseload,
            zip_code=energy_dto.zip_code,
            battery_capacity=energy_dto.battery_capacity,
            charge_point_power=energy_dto.charge_point_power,
            contract_capacity=round(updated_connection_power / 1000, 4),
            connection_capacity=round(updated_connection_power / 1000, 4),
        )

    def increase_current_connection(
        self,
        energy_dto: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC,
        connection_update: float = 0.0,
    ) -> EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC:
        """Increases the current connection."""
        energy_dto_day = energy_dto.model_copy(deep=True)

        if isinstance(energy_dto_day, EnergyDTOSmallConsumer):
            return self.map_small_connection_increase_to_new_connection(
                energy_dto_day.model_copy(deep=True), connection_update
            )
        if isinstance(energy_dto_day, EnergyDTOLargeConsumer):
            ep_dto = energy_dto_day.model_copy(deep=True)
            ep_dto.update_contracted_capacity(connection_update)
            return ep_dto

        return energy_dto_day

    def fit_energy_pod(
        self,
        energy_dto: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC,
    ) -> tuple[bool, float]:
        """Determines if the current connection power is sufficient in combination with an EnergyPod.

        Returns true if EnergyPod fits within the current connection power and false otherwise.
        Also returns a float representing the potential increase/decrease for the current connection power.
        """
        load_balancing_init = LoadBalancingOrchestrator(energy_dto)

        # Forecast the battery charging behaviour
        load_balancing_init.calculate_battery_charging()

        # Calculate the connection update
        connection_update = load_balancing_init.calculate_size_connection_update()

        return connection_update <= 0, connection_update

    def power_shortage(self, connection_update: float) -> EnergyDTOUpdate:
        """Determines whether to increase the connection power of the energy DTO's in case of a power shortage.

        For the EnergyPod scenario, it first checks whether the power shortage can be supplemented with a battery,
        without increasing the connection power.
        """
        fits_with_energy_pod, connection_update_ep = self.fit_energy_pod(self.energy_dto.model_copy(deep=True))

        if not fits_with_energy_pod:
            with_ep_dto = self.increase_current_connection(self.energy_dto, connection_update=connection_update_ep)
        else:
            with_ep_dto = self.energy_dto

        without_ep_dto = self.increase_current_connection(self.energy_dto, connection_update=connection_update)

        return EnergyDTOUpdate(
            connection_fits=ConnectionFits.SHORTAGE, without_ep_dto=without_ep_dto, with_ep_dto=with_ep_dto
        )

    def power_abundance(self, connection_update: float) -> EnergyDTOUpdate:
        """Determines whether to decrease the connection power of the energy DTO's in case of a power abundance."""
        without_ep_dto = self.energy_dto.model_copy(deep=True)
        if isinstance(self.energy_dto, EnergyDTOSmallConsumer):
            return EnergyDTOUpdate(
                connection_fits=ConnectionFits.CONSTANT,
                without_ep_dto=without_ep_dto,
                with_ep_dto=self.energy_dto.model_copy(deep=True),
            )
        if isinstance(self.energy_dto, EnergyDTOLargeConsumer):
            connection_update_large_consumer = (-connection_update / 1000) // 0.1

            if connection_update_large_consumer > 0:
                with_ep_dto = self.energy_dto.model_copy(deep=True)
                with_ep_dto.update_contracted_capacity(-connection_update_large_consumer * 0.1 * 1000)
                return EnergyDTOUpdate(
                    connection_fits=ConnectionFits.ABUNDANCE, without_ep_dto=without_ep_dto, with_ep_dto=with_ep_dto
                )

        return EnergyDTOUpdate(
            connection_fits=ConnectionFits.CONSTANT,
            without_ep_dto=without_ep_dto,
            with_ep_dto=self.energy_dto.model_copy(deep=True),
        )

    def calculate_updated_energy_dtos(self) -> EnergyDTOUpdate:
        """Determines the (updated) energy DTO's for the scenario's with and without EnergyPod."""
        load_balancing_init = LoadBalancingOrchestrator(self.energy_dto)
        connection_update = load_balancing_init.calculate_size_connection_update()

        if connection_update > 0:
            return self.power_shortage(connection_update)
        if connection_update < 0:
            return self.power_abundance(connection_update)
        return EnergyDTOUpdate(
            connection_fits=ConnectionFits.CONSTANT, without_ep_dto=self.energy_dto, with_ep_dto=self.energy_dto
        )
