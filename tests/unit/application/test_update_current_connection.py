"""Unit tests for application.update_current_connection using Arrange / Act / Assert (AAA).

Each test follows AAA, includes a docstring and returns None.
"""

from datetime import timedelta

import pytest

from src.application.update_current_connection import UpdateCurrentConnection
from src.config import days_in_current_year, first_day_of_year
from src.domain.baseload_profile import BaseloadProfile
from src.domain.energy_dto import ConnectionFits, EnergyDTOLargeConsumer, EnergyDTOSmallConsumer, EnergyDTOUpdate
from src.domain.vehicle_info import VehicleInfoDTO, VehicleTypeInfoDTO


@pytest.fixture
def valid_energy_pod_input_small_consumer() -> EnergyDTOSmallConsumer:
    """Arrange: provide a minimal EnergyPodDTO object for a small consumer with required attributes."""
    return EnergyDTOSmallConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.2, annual_km=2000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.5, annual_km=5000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=4, power_usage=1.0, annual_km=10000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[
            BaseloadProfile(datetime=first_day_of_year + timedelta(minutes=15 * t), power=1.0)
            for t in range(days_in_current_year * 96)
        ],
        zip_code="1111AA",
        connection_category="1 x 6A",
        battery_capacity=100,
        charge_point_power=200,
    )


@pytest.fixture
def valid_energy_pod_input_large_consumer() -> EnergyDTOLargeConsumer:
    """Arrange: provide a minimal EnergyPodDTO object for a large consumer with required attributes."""
    return EnergyDTOLargeConsumer(
        vehicle_info=VehicleInfoDTO(
            vans=VehicleTypeInfoDTO(nr_of_vehicles=1, power_usage=0.2, annual_km=2000),
            boxtrucks=VehicleTypeInfoDTO(nr_of_vehicles=0, power_usage=0.5, annual_km=5000),
            semitrailertrucks=VehicleTypeInfoDTO(nr_of_vehicles=0, power_usage=1.0, annual_km=10000),
        ),
        arrival_time="08:00",
        departure_time="18:00",
        baseload=[
            BaseloadProfile(datetime=first_day_of_year + timedelta(minutes=15 * t), power=1.0)
            for t in range(days_in_current_year * 96)
        ],
        zip_code="1111AA",
        connection_capacity=0.03,
        contract_capacity=0.03,
        battery_capacity=100,
        charge_point_power=200,
    )


def test_map_small_connection_increase_to_new_connection_small_consumer_correctly(
    valid_energy_pod_input_small_consumer: EnergyDTOSmallConsumer,
) -> None:
    """Arrange: Prepare an EnergyPod DTO for a small consumer and a connection update.

    Act: Call map_increase_to_new_connection.
    Assert: Returned object is EnergyDTOSmallConsumer and has correct connection category.
    """
    # Arrange
    mock_connection_update = 9
    mock_update_current_connection_init = UpdateCurrentConnection(valid_energy_pod_input_small_consumer)

    # Act
    result = mock_update_current_connection_init.map_small_connection_increase_to_new_connection(
        valid_energy_pod_input_small_consumer, mock_connection_update
    )
    expected_connection_category = "3 x 25A"

    # Assert
    assert isinstance(result, EnergyDTOSmallConsumer)
    assert result.connection_category == expected_connection_category


def test_map_small_connection_increase_to_new_connection_large_consumer_correctly(
    valid_energy_pod_input_small_consumer: EnergyDTOSmallConsumer,
) -> None:
    """Arrange: Prepare an EnergyPod DTO for a small consumer and a connection update.

    Act: Call map_increase_to_new_connection.
    Assert: Returned object is EnergyDTOLargeConsumer and has correct connection and contract capacity.
    """
    # Arrange
    mock_connection_update = 70
    mock_update_current_connection_init = UpdateCurrentConnection(valid_energy_pod_input_small_consumer)

    # Act
    result = mock_update_current_connection_init.map_small_connection_increase_to_new_connection(
        valid_energy_pod_input_small_consumer, mock_connection_update
    )
    expected_connection_capacity = 0.0816

    # Assert
    assert isinstance(result, EnergyDTOLargeConsumer)
    assert result.connection_capacity == expected_connection_capacity
    assert result.contract_capacity == expected_connection_capacity


def test_increase_current_connection_large_consumer_to_large_consumer_correctly(
    valid_energy_pod_input_large_consumer: EnergyDTOLargeConsumer,
) -> None:
    """Arrange: Prepare an EnergyPod DTO for a large consumer and a connection update.

    Act: Call increase_current_connection.
    Assert: Returned object is EnergyDTOLargeConsumer and has correct connection and contract capacity.
    """
    # Arrange
    mock_connection_update = 10
    mock_update_current_connection_init = UpdateCurrentConnection(valid_energy_pod_input_large_consumer)

    # Act
    updated_dto = mock_update_current_connection_init.increase_current_connection(
        energy_dto=valid_energy_pod_input_large_consumer, connection_update=mock_connection_update
    )
    expected_contract_capacity = 0.046

    assert isinstance(updated_dto, EnergyDTOLargeConsumer)
    assert updated_dto.connection_capacity == expected_contract_capacity
    assert updated_dto.contract_capacity == expected_contract_capacity


def test_power_shortage_fits_with_energy_pod(valid_energy_pod_input_large_consumer: EnergyDTOLargeConsumer) -> None:
    """Arrange: Prepare an EnergyPod DTO for a large consumer and a connection update.

    Initialize UpdateCurrentConnectionClass.
    Act: Call power_shortage.
    Assert: Returned object contains correct EnergyPod DTO's for with and without EnergyPod scenario.
    """
    # Arrange
    update_current_connection_init = UpdateCurrentConnection(valid_energy_pod_input_large_consumer)
    mock_connection_update = 10

    # Act
    result = update_current_connection_init.power_shortage(mock_connection_update)

    expected_without_ep_dto = valid_energy_pod_input_large_consumer.model_copy(deep=True)
    expected_without_ep_dto.connection_capacity = 0.046
    expected_without_ep_dto.contract_capacity = 0.046

    expected_with_ep_dto = valid_energy_pod_input_large_consumer

    # Assert
    assert isinstance(result, EnergyDTOUpdate)
    assert result.connection_fits == ConnectionFits.SHORTAGE
    assert isinstance(result.without_ep_dto, EnergyDTOLargeConsumer)
    assert isinstance(result.with_ep_dto, EnergyDTOLargeConsumer)
    assert result.without_ep_dto.connection_capacity == expected_without_ep_dto.connection_capacity
    assert result.without_ep_dto.contract_capacity == expected_without_ep_dto.contract_capacity
    assert result.with_ep_dto.connection_capacity == expected_with_ep_dto.connection_capacity
    assert result.with_ep_dto.contract_capacity == expected_with_ep_dto.contract_capacity


def test_power_shortage_not_fits_with_energy_pod(valid_energy_pod_input_small_consumer: EnergyDTOSmallConsumer) -> None:
    """Arrange: Prepare an EnergyPod DTO for a small consumer and a connection update.

    Initialize UpdateCurrentConnectionClass.
    Act: Call power_shortage.
    Assert: Returned object contains correct EnergyPod DTO's for with and without EnergyPod scenario.
    """
    # Arrange
    update_current_connection_init = UpdateCurrentConnection(valid_energy_pod_input_small_consumer)
    mock_connection_update = 10

    # Act
    result = update_current_connection_init.power_shortage(mock_connection_update)
    expected_with_ep_dto = valid_energy_pod_input_small_consumer.model_copy(deep=True)
    expected_with_ep_dto.connection_category = "1 x 35A"

    expected_without_ep_dto = valid_energy_pod_input_small_consumer.model_copy(deep=True)
    expected_without_ep_dto.connection_category = "3 x 25A"

    # Assert
    assert isinstance(result, EnergyDTOUpdate)
    assert result.connection_fits == ConnectionFits.SHORTAGE
    assert isinstance(result.without_ep_dto, EnergyDTOSmallConsumer)
    assert isinstance(result.with_ep_dto, EnergyDTOSmallConsumer)
    assert result.without_ep_dto.connection_category == expected_without_ep_dto.connection_category
    assert result.with_ep_dto.connection_category == expected_with_ep_dto.connection_category


def test_power_abundance_small_consumer(valid_energy_pod_input_small_consumer: EnergyDTOSmallConsumer) -> None:
    """Arrange: Prepare an EnergyPod DTO for a small consumer and a connection update.

    Initialize UpdateCurrentConnectionClass.
    Act: Call power_abundance.
    Assert: Returned object contains correct EnergyPod DTO's for with and without EnergyPod scenario.
    """
    # Arrange
    mock_energy_dto_small_consumer = valid_energy_pod_input_small_consumer.model_copy(deep=True)
    mock_energy_dto_small_consumer.vehicle_info.boxtrucks.nr_of_vehicles = 0
    mock_energy_dto_small_consumer.vehicle_info.semitrailertrucks.nr_of_vehicles = 0
    update_current_connection_init = UpdateCurrentConnection(mock_energy_dto_small_consumer)
    mock_connection_update = 0

    # Act
    result = update_current_connection_init.power_abundance(mock_connection_update)
    expected_without_ep_dto = mock_energy_dto_small_consumer
    expected_with_ep_dto = mock_energy_dto_small_consumer

    # Assert
    assert isinstance(result, EnergyDTOUpdate)
    assert result.connection_fits == ConnectionFits.CONSTANT
    assert isinstance(result.without_ep_dto, EnergyDTOSmallConsumer)
    assert isinstance(result.with_ep_dto, EnergyDTOSmallConsumer)
    assert result.without_ep_dto.connection_category == expected_without_ep_dto.connection_category
    assert result.with_ep_dto.connection_category == expected_with_ep_dto.connection_category


def test_power_abundance_large_consumer(valid_energy_pod_input_large_consumer: EnergyDTOLargeConsumer) -> None:
    """Arrange: Prepare an EnergyPod DTO for a large consumer and a connection update.

    Initialize UpdateCurrentConnectionClass.
    Act: Call power_abundance.
    Assert: Returned object contains correct EnergyPod DTO's for with and without EnergyPod scenario.
    """
    # Arrange
    mock_energy_dto_large_consumer = valid_energy_pod_input_large_consumer.model_copy(deep=True)
    mock_energy_dto_large_consumer.connection_capacity = 0.6
    mock_energy_dto_large_consumer.contract_capacity = 0.6
    update_current_connection_init = UpdateCurrentConnection(mock_energy_dto_large_consumer)
    mock_connection_update = -254

    # Act
    result = update_current_connection_init.power_abundance(mock_connection_update)
    expected_without_ep_dto = mock_energy_dto_large_consumer
    expected_with_ep_dto = valid_energy_pod_input_large_consumer.model_copy(deep=True)
    expected_with_ep_dto.contract_capacity = 0.46
    expected_with_ep_dto.connection_capacity = 0.6

    # Assert
    assert isinstance(result, EnergyDTOUpdate)
    assert result.connection_fits == ConnectionFits.ABUNDANCE
    assert isinstance(result.without_ep_dto, EnergyDTOLargeConsumer)
    assert isinstance(result.with_ep_dto, EnergyDTOLargeConsumer)
    assert result.without_ep_dto.connection_capacity == expected_without_ep_dto.connection_capacity
    assert result.without_ep_dto.contract_capacity == expected_without_ep_dto.contract_capacity
    assert result.with_ep_dto.connection_capacity == expected_with_ep_dto.connection_capacity
    assert result.with_ep_dto.contract_capacity == expected_with_ep_dto.contract_capacity
