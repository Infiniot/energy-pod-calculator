"""Fixtures for all tests."""

from datetime import datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

import numpy as np
import pytest

from src.application.charging_profiles_without_ep import ChargingProfilesWithoutEP, Vehicle
from src.domain.baseload_profile import BaseloadProfile
from src.domain.charging_profiles import ChargingProfileDTO
from src.domain.connection_power import ConnectionPower
from src.domain.vehicle_info import VehicleType, VehicleTypeInfo


@pytest.fixture
def seed_default_rng(request: pytest.FixtureRequest):  # noqa: ANN201
    """Fixture: default generator to always get the same sequence of random numbers."""
    seeded_rng = np.random.default_rng(seed=0)
    mock_location = request.node.get_closest_marker("rng_location").args[0]
    with mock.patch(f"{mock_location}.np.random.default_rng") as mocked:
        mocked.return_value = seeded_rng
        yield


@pytest.fixture
def mock_baseload_profiles() -> list[BaseloadProfile]:
    """Fixture: mock baseload profiles."""
    return [
        BaseloadProfile(
            datetime=datetime(year=2025, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
            + timedelta(minutes=15 * i),
            power=10,
        )
        for i in range(96 * 365)
    ]


@pytest.fixture
def mock_baseload_profiles_with_overnight() -> list[BaseloadProfile]:
    """Fixture: mock baseload profiles."""
    return [
        BaseloadProfile(
            datetime=datetime(year=2025, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
            + timedelta(minutes=15 * i),
            power=10,
        )
        for i in range(96 * 366)
    ]


@pytest.fixture
def mock_arrival_and_departure_time_without_overnight_charging() -> tuple[datetime, datetime]:
    """Fixture: mock arrival and departure time without overnight charging."""
    mock_arrival_time = datetime(year=2025, month=1, day=2, hour=8, tzinfo=ZoneInfo("Europe/Amsterdam"))
    mock_departure_time = datetime(year=2025, month=1, day=2, hour=18, tzinfo=ZoneInfo("Europe/Amsterdam"))

    return mock_arrival_time, mock_departure_time


@pytest.fixture
def mock_vehicle_info_multiple_vehicles() -> list[VehicleTypeInfo]:
    """Fixture: Mock vehicle info including 1 van, 5 box trucks, 3 semi-trailer trucks.

    Default values for power usage and annual km for each vehicle type.
    """
    return [
        VehicleTypeInfo(vehicle_type=VehicleType.VAN, nr_of_vehicles=1, power_usage=0.2, annual_km=20000),
        VehicleTypeInfo(vehicle_type=VehicleType.BOXTRUCK, nr_of_vehicles=5, power_usage=0.5, annual_km=50000),
        VehicleTypeInfo(vehicle_type=VehicleType.SEMITRAILERTRUCK, nr_of_vehicles=3, power_usage=1, annual_km=70000),
    ]


@pytest.fixture
def mock_connection_powers() -> list[ConnectionPower]:
    """Fixture: mock connection powers."""
    return [
        ConnectionPower(
            datetime=datetime(year=2025, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
            + timedelta(minutes=15 * i),
            power=55,
        )
        for i in range(96 * 365)
    ]


@pytest.fixture
def mock_connection_powers_with_overnight() -> list[ConnectionPower]:
    """Fixture: mock connection powers."""
    return [
        ConnectionPower(
            datetime=datetime(year=2025, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
            + timedelta(minutes=15 * i),
            power=55,
        )
        for i in range(96 * 366)
    ]


@pytest.fixture
def mock_charging_profile_dto_without_overnight_charging(
    mock_connection_powers: list[ConnectionPower],
) -> ChargingProfileDTO:
    """Mock arrival and departure datetimes and current connection without overnight charging."""
    return ChargingProfileDTO(arrival_time="08:00", departure_time="18:00", connection_power=mock_connection_powers)


@pytest.fixture
def mock_init_multiple_vehicles_without_overnight_charging(
    mock_charging_profile_dto_without_overnight_charging: ChargingProfileDTO,
    mock_vehicle_info_multiple_vehicles: list[VehicleTypeInfo],
    mock_baseload_profiles: list[BaseloadProfile],
) -> ChargingProfilesWithoutEP:
    """Initialize ChargingProfilesWithoutEP class with mock values for multiple vehicles without overnight charging."""
    return ChargingProfilesWithoutEP(
        charging_profiles_input=mock_charging_profile_dto_without_overnight_charging,
        vehicle_info=mock_vehicle_info_multiple_vehicles,
        baseload_profiles=mock_baseload_profiles,
        charge_point_power=200,
    )


@pytest.fixture
def mock_charging_profile_dto_with_overnight_charging(
    mock_connection_powers_with_overnight: list[ConnectionPower],
) -> ChargingProfileDTO:
    """Mock arrival and departure datetimes and current connection with overnight charging."""
    return ChargingProfileDTO(
        arrival_time="18:00", departure_time="08:00", connection_power=mock_connection_powers_with_overnight
    )


@pytest.fixture
def mock_stochastic_arrival_times() -> np.ndarray:
    """Fixture: mock stochastic arrival times for multiple vehicles without overnight charging."""
    return np.array(
        [
            datetime(year=2025, month=1, day=2, hour=8, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=15, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=7, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=15, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=8, minute=30, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=7, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
        ]
    )


@pytest.fixture
def mock_stochastic_departure_times() -> np.ndarray:
    """Fixture: mock stochastic departure times for multiple vehicles without overnight charging."""
    return np.array(
        [
            datetime(year=2025, month=1, day=2, hour=17, minute=30, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=17, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=18, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=16, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=18, minute=0, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=17, minute=30, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=17, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=17, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
            datetime(year=2025, month=1, day=2, hour=17, minute=45, tzinfo=ZoneInfo("Europe/Amsterdam")),
        ]
    )


@pytest.fixture
def mock_vehicles(
    mock_vehicle_info_multiple_vehicles: list[VehicleTypeInfo],
    mock_stochastic_arrival_times: np.ndarray,
    mock_stochastic_departure_times: np.ndarray,
) -> list[Vehicle]:
    """Fixture: mock vehicles without overnight charging."""
    vehicles = []

    vehicle_count = 0
    for v in mock_vehicle_info_multiple_vehicles:
        for _ in range(v.nr_of_vehicles):
            vehicles.append(
                Vehicle(
                    vehicle_type=v.vehicle_type,
                    power_usage=v.power_usage,
                    annual_km=v.annual_km,
                    arrival_time=mock_stochastic_arrival_times[vehicle_count],
                    departure_time=mock_stochastic_departure_times[vehicle_count],
                )
            )
            vehicle_count += 1

    return vehicles
