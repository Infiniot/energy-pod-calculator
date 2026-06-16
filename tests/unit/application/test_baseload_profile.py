"""Unit tests for application.baseload_profile using Arrange/Act/Assert (AAA).

Each test follows the AAA pattern and returns None.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from src.application.baseload_profile import (
    baseloads_df_to_list,
    baseloads_list_to_df,
    calculate_baseload_profiles_average_week,
    calculate_shifted_baseload_profiles,
    get_annual_consumption_from_baseload_list,
    get_baseload_profile_from_business_category,
    map_business_category,
)
from src.domain.baseload_profile import BaseloadProfile


def test_map_business_category_returns_correct_category() -> None:
    """Arrange: Provide existing business category.

    Act: Call map_business_category.
    Assert: Returned correct type and category.
    """
    # Arrange and act
    result = map_business_category("Industrie")

    # Assert
    assert isinstance(result, str)
    assert result == "INDUSTRIE"


def test_map_business_category_raises_error() -> None:
    """Arrange: Provide non-existing business category.

    Act: Call map_business_category.
    Assert: Value error is raised.
    """
    with pytest.raises(ValueError, match="Unknown business category: "):
        # Arrange / Act / Assert
        map_business_category("Bakker")


@patch("src.application.baseload_profile.pd.read_csv")
def test_get_baseload_profile_from_business_category_correctly(mock_read_csv: MagicMock) -> None:
    """Arrange: Prepare a baseload csv with ISO datetimes and power values.

    Act: Call get_baseload_profile_from_business_category.
    Assert: Returned dataframe length, datetime and computed powers are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
    mock_datetimes = [(start_datetime + timedelta(minutes=15 * t)) for t in range(365 * 96)]
    iso_datetimes = [t.isoformat() for t in mock_datetimes]
    powers = [10] * (365 * 96)
    df_input = pd.DataFrame({"DATUM_TIJDSTIP": iso_datetimes, "WAARDE": powers})
    mock_read_csv.return_value = df_input

    mock_business_category = "Industrie"
    mock_annual_consumption = 1000

    # Act
    result = get_baseload_profile_from_business_category(
        business_category=mock_business_category, annual_consumption=mock_annual_consumption
    )

    expected_length = 365 * 96
    expected_total_consumption = 365 * 96 * 10
    expected_peak_consumption = mock_annual_consumption / (0.25 * expected_total_consumption)

    # Assert
    assert isinstance(result, list)
    assert len(result) == expected_length

    for i, baseload_profile in enumerate(result):
        assert hasattr(baseload_profile, "datetime")
        assert isinstance(baseload_profile.datetime, datetime)
        assert hasattr(baseload_profile, "power")
        assert isinstance(baseload_profile.power, float)
        assert baseload_profile.power == round(powers[i] * expected_peak_consumption, 2)


@patch("src.application.baseload_profile.pd.read_csv")
def test_calculate_shifted_baseload_profiles_computes_expected_powers_without_overnight(
    mock_read_csv: MagicMock,
) -> None:
    """Arrange: Prepare a baseload csv with ISO datetimes and power values.

    Act: Call calculate_shifted_baseload_profiles.
    Assert: Returned list length, datetime tzinfo and computed powers are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
    iso_datetimes = [(start_datetime + timedelta(minutes=15 * t)).isoformat() for t in range(365 * 96)]
    powers = list(range(365 * 96))
    df_input = pd.DataFrame({"DATUM_TIJDSTIP": iso_datetimes, "WAARDE": powers})
    mock_read_csv.return_value = df_input
    annual_consumption = 1000

    expected_length = 365 * 96

    # Act
    result = calculate_shifted_baseload_profiles(
        get_baseload_profile_from_business_category(business_category="Farmer", annual_consumption=annual_consumption)
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == expected_length

    total_renorm = sum(powers)
    peak_consumption = annual_consumption / (0.25 * total_renorm)
    expected_powers = powers[4 * 96 :] + powers[96 : 5 * 96]
    for r in range(len(result)):
        assert hasattr(result[r], "datetime")
        assert isinstance(result[r].datetime, datetime)
        assert hasattr(result[r], "power")
        assert isinstance(result[r].power, float)
        assert result[r].datetime.tzinfo == ZoneInfo("Europe/Amsterdam")
        assert pytest.approx(result[r].power, rel=1e-4) == round(expected_powers[r] * peak_consumption, 2)

    # verify pandas.read_csv was called for the SBI file (path string presence)
    mock_read_csv.assert_called_once()
    called_arg = mock_read_csv.call_args[0][0]
    assert called_arg.endswith("AGRARIER.csv")


@patch("src.application.baseload_profile.pd.read_csv")
def test_calculate_shifted_baseload_profiles_computes_expected_powers_with_overnight(mock_read_csv: MagicMock) -> None:
    """Arrange: Prepare a baseload csv with ISO datetimes and power values.

    Act: Call calculate_shifted_baseload_profiles.
    Assert: Returned list length, datetime tzinfo and computed powers are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
    iso_datetimes = [(start_datetime + timedelta(minutes=15 * t)).isoformat() for t in range(365 * 96)]
    powers = list(range(365 * 96))
    df_input = pd.DataFrame({"DATUM_TIJDSTIP": iso_datetimes, "WAARDE": powers})
    mock_read_csv.return_value = df_input
    annual_consumption = 1000

    expected_length = 366 * 96

    # Act
    result = calculate_shifted_baseload_profiles(
        get_baseload_profile_from_business_category(business_category="Farmer", annual_consumption=annual_consumption),
        overnight_charging=True,
    )

    # Assert
    assert isinstance(result, list)
    assert len(result) == expected_length

    total_renorm = sum(powers)
    peak_consumption = annual_consumption / (0.25 * total_renorm)
    expected_powers = powers[4 * 96 :] + powers[96 : 6 * 96]
    for r in range(len(result)):
        assert hasattr(result[r], "datetime")
        assert hasattr(result[r], "power")
        assert isinstance(result[r].datetime, datetime)
        assert isinstance(result[r].power, float)
        assert result[r].datetime.tzinfo == ZoneInfo("Europe/Amsterdam")
        assert pytest.approx(result[r].power, rel=1e-4) == round(expected_powers[r] * peak_consumption, 2)

    # verify pandas.read_csv was called for the SBI file (path string presence)
    mock_read_csv.assert_called_once()
    called_arg = mock_read_csv.call_args[0][0]
    assert called_arg.endswith("AGRARIER.csv")


def test_baseloads_df_to_list() -> None:
    """Arrange: Prepare a dataframe with ISO datetimes and power values.

    Act: Call baseloads_df_to_list.
    Assert: Returned list length, attributes and values are correct.
    """
    # Arrange
    mock_datetimes = [
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
    ]
    mock_powers = [1, 2]
    mock_baseloads = pd.DataFrame({"Start date": mock_datetimes, "power_consumption": mock_powers})

    # Act
    result = baseloads_df_to_list(mock_baseloads)
    expected_length = 2

    # Assert
    assert len(result) == expected_length
    assert isinstance(result, list)
    assert hasattr(result[0], "datetime")
    assert hasattr(result[0], "power")
    assert result[0].datetime == mock_datetimes[0]
    assert result[0].power == mock_powers[0]
    assert hasattr(result[1], "datetime")
    assert hasattr(result[1], "power")
    assert result[1].datetime == mock_datetimes[1]
    assert result[1].power == mock_powers[1]


def test_baseloads_list_to_df() -> None:
    """Arrange: Prepare list of BaseloadProfile objects with ISO datetimes and power values.

    Act: Call baseloads_list_to_df.
    Assert: Returned dataframe has correct length and attributes.
    """
    # Arrange
    mock_datetimes = [
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
    ]
    mock_powers = [1, 2]
    mock_baseloads = [BaseloadProfile(datetime=mock_datetimes[t], power=mock_powers[t]) for t in range(2)]

    # Act
    result = baseloads_list_to_df(mock_baseloads)
    expected_length = 2

    # Assert
    assert len(result) == expected_length
    assert isinstance(result, pd.DataFrame)
    assert result.iloc[0]["Start date"] == mock_datetimes[0]
    assert result.iloc[0]["power_consumption"] == mock_powers[0]
    assert result.iloc[1]["Start date"] == mock_datetimes[1]
    assert result.iloc[1]["power_consumption"] == mock_powers[1]


def test_calculate_baseload_profiles_average_week_correctly() -> None:
    """Arrange: Prepare a dataframe with ISO datetimes and powers.

    Act: Call calculate_baseload_profiles_average_week.
    Assert: Returned list length and values are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2024, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam"))
    mock_datetimes = [(start_datetime + timedelta(minutes=15 * t)) for t in range(366 * 96)]
    mock_powers = np.repeat(list(range(52)), 7 * 96).tolist() + [53] * 2 * 96
    mock_baseloads = [BaseloadProfile(datetime=mock_datetimes[i], power=mock_powers[i]) for i in range(366 * 96)]

    # Act
    result = calculate_baseload_profiles_average_week(mock_baseloads)
    expected_length = 7 * 96

    # Assert
    assert isinstance(result, list)
    assert len(result) == expected_length
    assert result == [25.5] * 7 * 96


def test_get_annual_consumption_from_baseload_list() -> None:
    """Arrange: Prepare a list of baseload profiles.

    Act: Call get_annual_consumption_from_baseload_list.
    Assert: Returned type and value are correct.
    """
    # Arrange
    mock_datetimes = [
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
        datetime(year=2023, month=1, day=1, tzinfo=ZoneInfo("Europe/Amsterdam")),
    ]
    mock_powers = [1, 2]
    mock_baseloads = [BaseloadProfile(datetime=mock_datetimes[t], power=mock_powers[t]) for t in range(2)]

    # Act
    result = get_annual_consumption_from_baseload_list(mock_baseloads)
    expected_result = 0.75

    # Assert
    assert isinstance(result, float)
    assert result == expected_result
