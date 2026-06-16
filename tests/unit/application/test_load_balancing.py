"""Unit tests for application.energy_prices using Arrange / Act / Assert (AAA).

Each test follows AAA, includes a docstring and returns None.
"""

from datetime import timedelta

import numpy as np
import pytest

from src.application.load_balancing import LoadBalancingOrchestrator
from src.config import days_in_current_year, first_day_of_year
from src.domain.baseload_profile import BaseloadProfile
from src.domain.energy_dto import EnergyDTOSmallConsumer
from src.domain.vehicle_info import VehicleInfoDTO, VehicleTypeInfoDTO


@pytest.fixture
def valid_energy_pod_input() -> EnergyDTOSmallConsumer:
    """Arrange: provide a minimal EnergyPodDTO object for a small consumer with required attributes."""
    return EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.2, annual_km=2000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.5, annual_km=5000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1.0, annual_km=10000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[
            BaseloadProfile(datetime=first_day_of_year + timedelta(minutes=15 * t), power=1.0)
            for t in range(days_in_current_year * 96)
        ],
        zip_code="1111AA",
        connection_category="3 x 25A",
        battery_capacity=100,
        charge_point_power=200,
    )


def test_load_balancer_has_expected_attributes(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: Prepare an EnergyPod DTO for a small consumer.

    Act: Initialize LoadBalancingOrchestrator class.
    Assert: Load balancer has expected attributes.
    """
    # Arrange / Act
    load_balancer = LoadBalancingOrchestrator(valid_energy_pod_input)

    # Assert
    assert isinstance(load_balancer, LoadBalancingOrchestrator)
    assert hasattr(load_balancer, "connection_power")
    assert hasattr(load_balancer, "baseload_profiles")
    assert hasattr(load_balancer, "battery_charging")
    assert hasattr(load_balancer, "charging_power")


def test_load_balancer_returns_increase(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: create sample raw energy CSV dataframe rows.

    Act: call convert_datetimes. Assert: returned DataFrame has 'Start date' and price column preserved.
    """
    # Arrange
    # patch module energy_price_column to known name
    valid_energy_pod_input.vehicle_info = VehicleInfoDTO(
        vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1000, annual_km=365),
        boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1000, annual_km=365),
        semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1000, annual_km=365),
    )

    load_balancer = LoadBalancingOrchestrator(valid_energy_pod_input)
    update = load_balancer.calculate_size_connection_update()

    total = 100  # percent

    assert load_balancer.percentage_power_abundances + load_balancer.percentage_power_shortages == total
    assert update > 0


def test_load_balancer_returns_decrease(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: create sample raw energy CSV dataframe rows.

    Act: call convert_datetimes. Assert: returned DataFrame has 'Start date' and price column preserved.
    """
    # Arrange
    # patch module energy_price_column to known name
    valid_energy_pod_input.vehicle_info = VehicleInfoDTO(
        vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1, annual_km=365),
        boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1, annual_km=365),
        semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=1, annual_km=365),
    )

    load_balancer = LoadBalancingOrchestrator(valid_energy_pod_input)
    update = load_balancer.calculate_size_connection_update()

    total = 100  # percent

    assert load_balancer.percentage_power_abundances + load_balancer.percentage_power_shortages == total
    assert update < 0


def test_load_balancer_returns_constant(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: create and energy pod that does not need to increase or decrease its connection.

    Act: create the energy pod and initialize the load balancer, then calculate the update.
    """
    # Arrange
    # Create a energy pod with 90 kWh demand per day and 9 kW power capacity for 10 hours
    valid_energy_pod_input.vehicle_info = VehicleInfoDTO(
        vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=30, annual_km=365),
        boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=30, annual_km=365),
        semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=30, annual_km=365),
    )
    valid_energy_pod_input.baseload = [
        BaseloadProfile(datetime=first_day_of_year + timedelta(minutes=15 * t), power=0.0)
        for t in range(days_in_current_year * 96)
    ]
    valid_energy_pod_input.connection_category = "1 x 40A"

    load_balancer = LoadBalancingOrchestrator(valid_energy_pod_input)
    update = load_balancer.calculate_size_connection_update()

    # output should return no increase or decrease of connection
    assert load_balancer.percentage_power_abundances + load_balancer.percentage_power_shortages == 0
    assert update == 0


def test_load_balancer_battery_charging(valid_energy_pod_input: EnergyDTOSmallConsumer) -> None:
    """Arrange: create sample raw energy CSV dataframe rows.

    Act: call convert_datetimes. Assert: returned DataFrame has 'Start date' and price column preserved.
    """
    # Arrange
    # patch module energy_price_column to known name
    load_balancer = LoadBalancingOrchestrator(valid_energy_pod_input)

    charging_power_before = np.sum(load_balancer.charging_power)

    load_balancer.calculate_battery_charging()

    charging_power_after = np.sum(load_balancer.charging_power)

    assert charging_power_before > charging_power_after
    assert np.sum(load_balancer.battery_charging) > 0
