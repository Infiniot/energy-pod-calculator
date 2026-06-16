"""Fixtures for unit tests in the application folder."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from src.application.charging_profiles_without_ep import ChargingProfilesWithoutEP, Vehicle
from src.domain.baseload_profile import BaseloadProfile
from src.domain.charging_profiles import ChargingProfileDTO
from src.domain.vehicle_info import VehicleType, VehicleTypeInfo


@pytest.fixture
def mock_vehicle_info_single_vehicle() -> list[VehicleTypeInfo]:
    """Fixture: mock vehicle info including 1 van, 0 box trucks and 0 semi-trailer trucks.

    Default values for power usage and annual km for each vehicle type.
    """
    return [
        VehicleTypeInfo(vehicle_type=VehicleType.VAN, nr_of_vehicles=1, power_usage=0.2, annual_km=20000),
        VehicleTypeInfo(vehicle_type=VehicleType.BOXTRUCK, nr_of_vehicles=0, power_usage=0.5, annual_km=50000),
        VehicleTypeInfo(vehicle_type=VehicleType.SEMITRAILERTRUCK, nr_of_vehicles=0, power_usage=1, annual_km=70000),
    ]


@pytest.fixture
def mock_arrival_and_departure_time_with_overnight_charging() -> tuple[datetime, datetime]:
    """Fixture: mock arrival and departure time with overnight charging."""
    mock_arrival_time = datetime(year=2025, month=1, day=1, hour=18, tzinfo=ZoneInfo("Europe/Amsterdam"))
    mock_departure_time = datetime(year=2025, month=1, day=2, hour=8, tzinfo=ZoneInfo("Europe/Amsterdam"))

    return mock_arrival_time, mock_departure_time


@pytest.fixture
def mock_init_single_vehicle_with_overnight_charging(
    mock_charging_profile_dto_with_overnight_charging: ChargingProfileDTO,
    mock_vehicle_info_single_vehicle: list[VehicleTypeInfo],
    mock_baseload_profiles: list[BaseloadProfile],
) -> ChargingProfilesWithoutEP:
    """Initialize ChargingProfilesWithoutEP class with mock values for a single vehicle with overnight charging."""
    return ChargingProfilesWithoutEP(
        charging_profiles_input=mock_charging_profile_dto_with_overnight_charging,
        vehicle_info=mock_vehicle_info_single_vehicle,
        baseload_profiles=mock_baseload_profiles,
        charge_point_power=200,
    )


@pytest.fixture
def mock_init_single_vehicle_without_overnight_charging(
    mock_charging_profile_dto_without_overnight_charging: ChargingProfileDTO,
    mock_vehicle_info_single_vehicle: list[VehicleTypeInfo],
    mock_baseload_profiles: list[BaseloadProfile],
) -> ChargingProfilesWithoutEP:
    """Initialize ChargingProfilesWithoutEP class with mock values for a single vehicle without overnight charging."""
    return ChargingProfilesWithoutEP(
        charging_profiles_input=mock_charging_profile_dto_without_overnight_charging,
        vehicle_info=mock_vehicle_info_single_vehicle,
        baseload_profiles=mock_baseload_profiles,
        charge_point_power=200,
    )


@pytest.fixture
def mock_vehicles_t_36(
    mock_vehicles: list[Vehicle],
) -> list[Vehicle]:
    """Fixture: mock vehicles without overnight charging, evaluated at 08:00 (t=36)."""
    vehicles_charging = mock_vehicles.copy()

    vehicles_charging[0].is_charging = True
    vehicles_charging[1].is_charging = True
    vehicles_charging[2].is_charging = False
    vehicles_charging[3].is_charging = True
    vehicles_charging[4].is_charging = True
    vehicles_charging[5].is_charging = False
    vehicles_charging[6].is_charging = False
    vehicles_charging[7].is_charging = False
    vehicles_charging[8].is_charging = True

    vehicles_charging[4].current_capacity = 10 / 2 * 0.25
    vehicles_charging[8].current_capacity = 10 / 2 * 0.25

    return vehicles_charging
