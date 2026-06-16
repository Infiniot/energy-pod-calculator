"""Unit tests for application.with_energy_pod.calculate_energy_pod_power using Arrange/Act/Assert (AAA).

Each test follows Arrange / Act / Assert, includes a docstring and returns None.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException

from src.application.with_energy_pod import EnergyPodPower
from src.domain.baseload_profile import BaseloadProfile
from src.domain.energy_dto import EnergyDTOSmallConsumer
from src.domain.energy_pod import EnergyPodResults
from src.domain.vehicle_info import VehicleInfoDTO, VehicleTypeInfoDTO


@pytest.fixture
def valid_energy_pod_dto() -> EnergyDTOSmallConsumer:
    """Fixture providing a valid EnergyDTOSmallConsumer with all required fields populated."""
    return EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=10, annual_km=55),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=0, power_usage=0, annual_km=0),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=0, power_usage=0, annual_km=0),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[BaseloadProfile(datetime=datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Amsterdam")), power=0.0)]
        * 96
        * 365,
        connection_category="3 x 25A",
        zip_code="1111AA",
        battery_capacity=None,
        charge_point_power=200,
    )


@pytest.fixture
def invalid_energy_pod_dto() -> EnergyDTOSmallConsumer:
    """Fixture providing a valid EnergyDTOSmallConsumer with all required fields populated."""
    return EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=3, power_usage=0.2, annual_km=20000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=3, power_usage=0.5, annual_km=50000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=3, power_usage=1, annual_km=70000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[BaseloadProfile(datetime=datetime(2025, 1, 1, tzinfo=ZoneInfo("Europe/Amsterdam")), power=0.0)]
        * 96
        * 365,
        connection_category="3 x 25A",
        zip_code="1111AA",
        battery_capacity=None,
        charge_point_power=200,
    )


def test_calculate_energy_pod_power_optimization(valid_energy_pod_dto: EnergyDTOSmallConsumer) -> None:
    """Arrage: Calculate_optimization happy flow."""
    # Arrange
    mock_energy_pod_power_init = EnergyPodPower(valid_energy_pod_dto)

    # Act
    result = mock_energy_pod_power_init.calculate_energy_pod_power_results()

    # Assert
    # no throw and returns a list
    assert isinstance(result, EnergyPodResults)


def test_calculate_energy_pod_power_optimization_error_logs_and_raises(
    invalid_energy_pod_dto: EnergyDTOSmallConsumer,
) -> None:
    """Arrange: EnergyPodOptimization.calculate_optimization raises OptimizationError (logged).

    Act / Assert: function logs the error and raises HTTPException.
    """
    with pytest.raises(HTTPException):
        EnergyPodPower(invalid_energy_pod_dto).calculate_energy_pod_power_results()
