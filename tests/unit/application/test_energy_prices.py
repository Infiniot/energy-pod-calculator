"""Unit tests for application.energy_prices using Arrange / Act / Assert (AAA).

Each test follows AAA, includes a docstring and returns None.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pandas as pd

from src.application import energy_prices
from src.config import energy_price_column
from src.domain.energy_prices import ScaledEnergyPrice


@patch("src.application.energy_prices.pd.read_csv")
def test_read_energy_prices_from_csv_calls_pandas_read_csv(mock_read_csv: MagicMock) -> None:
    """Arrange: prepare a filepath.

    Act: call read_energy_prices_from_csv.
    Assert: pandas.read_csv called once.
    """
    # Arrange
    filepath = "some/path.csv"

    # Act
    energy_prices.read_energy_prices_from_csv(filepath)

    # Assert
    mock_read_csv.assert_called_once_with(filepath)


@patch("src.application.energy_prices.pd.DataFrame.to_csv")
def test_save_energy_prices_to_csv_calls_to_csv(mock_to_csv: MagicMock) -> None:
    """Arrange: make a small DataFrame.

    Act: call save_energy_prices_to_csv.
    Assert: DataFrame.to_csv called with filepath.
    """
    # Arrange
    df = pd.DataFrame({"a": [1, 2]})  # noqa: PD901
    filepath = "out.csv"

    # Act
    energy_prices.save_energy_prices_to_csv(df, filepath)

    # Assert
    mock_to_csv.assert_called_once_with(filepath)


def test_convert_datetimes_parses_and_returns_expected_columns() -> None:
    """Arrange: create sample raw energy CSV dataframe rows.

    Act: call convert_datetimes.
    Assert: returned DataFrame has 'Start date' and price column preserved.
    """
    # Arrange
    # patch module energy_price_column to known name
    colname = "Day-ahead Price (EUR/MWh)"
    raw = pd.DataFrame(
        {
            "MTU (CET/CEST)": ["01/01/2024 00:00:00 - 01/01/2024 01:00:00"],
            colname: [100.0],
        }
    )
    expected_price = 100.0
    # Act
    with patch("application.energy_prices.energy_price_column", colname):
        out = energy_prices.convert_datetimes(raw)

    # Assert
    assert isinstance(out, pd.DataFrame)
    assert "Start date" in out.columns
    assert colname in out.columns
    # Start date should be timezone-aware UTC
    assert pd.api.types.is_datetime64_any_dtype(out["Start date"])
    assert out.shape[0] == 2  # noqa: PLR2004
    assert out.iloc[0][colname] == expected_price


def test_interpolate_energy_prices_creates_15min_grid_and_maps_values() -> None:
    """Arrange: create hourly data for two consecutive hours.

    Act: call interpolate_energy_prices.
    Assert: output contains 15-min slots with correct mapping.
    """
    # Arrange
    col = "price"
    base = pd.to_datetime("2024-01-01T00:00:00+00:00")
    df = pd.DataFrame(  # noqa: PD901
        {
            "Start date": [base, base + timedelta(hours=1)],
            col: [100.0, 200.0],
            "Day-ahead Price (EUR/MWh)": [100.0, 200.0],
        }
    )
    expected_first_quarter_price = 100.0
    expected_fifth_quarter_price = 200.0
    # Act
    with patch("application.energy_prices.energy_price_column", col):
        out = energy_prices.interpolate_energy_prices(df)

    # Assert
    # From 00:00 to 01:45 inclusive step 15min -> 8 slots
    assert isinstance(out, pd.DataFrame)
    assert out.shape[0] == 8  # noqa: PLR2004
    assert out["Day-ahead Price (EUR/MWh)"].iloc[0] == expected_first_quarter_price
    assert out["Day-ahead Price (EUR/MWh)"].iloc[4] == expected_fifth_quarter_price


@patch("src.application.energy_prices.read_energy_prices_from_csv")
def test_load_energy_prices_returns_list_of_domain_objects(mock_read: MagicMock) -> None:
    """Arrange: read_energy_prices_from_csv returns dataframe with Start date strings.

    Act: call load_energy_prices.
    Assert: returns list with expected length and attributes.
    """
    # Arrange
    col = "Day-ahead Price (EUR/MWh)"
    data = pd.DataFrame(
        {
            col: [10.0, 20.0],
            "Start date": ["2024/01/01 00:00 - 2024/01/01 01:00", "2024/01/01 01:00 - 2024/01/01 02:00"],
        }
    )
    with patch("application.energy_prices.energy_price_column", col):
        mock_read.return_value = data

        # Act
        out = energy_prices.load_energy_prices()

    # Assert
    assert isinstance(out, list)
    assert hasattr(out[0], "datetime")
    assert hasattr(out[0], "price")
    assert out[0].price == 10.0  # noqa: PLR2004


@patch("src.application.energy_prices.read_energy_prices_from_csv")
def test_load_interpolated_energy_prices_year_without_overnight(mock_read: MagicMock) -> None:
    """Arrange: prepare a csv containing energy prices with ISO datetimes.

    Act: call load_interpolated_energy_prices_year.
    Assert: returned list length, datetime tzinfo and computed prices are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2024, month=1, day=1, tzinfo=UTC)
    iso_datetimes = [(start_datetime + timedelta(minutes=15 * t)).isoformat() for t in range(366 * 96)]
    prices = [i / 1000 for i in range(366 * 96)]
    df_input = pd.DataFrame({"Start date": iso_datetimes, energy_price_column: prices})
    mock_read.return_value = df_input

    expected_length = 365 * 96

    # Act
    result = energy_prices.load_interpolated_energy_prices_year()

    # Assert
    assert isinstance(result, list)
    assert isinstance(result[0], ScaledEnergyPrice)
    assert len(result) == expected_length
    expected_prices = prices[3 * 96 :] + prices[2 * 96 : 4 * 96]
    for r in range(len(result)):
        assert isinstance(result[r].datetime, datetime)
        assert isinstance(result[r].price, float)
        assert result[r].datetime.tzinfo == ZoneInfo("Europe/Amsterdam")
        assert result[r].price == expected_prices[r] / 1000


@patch("src.application.energy_prices.read_energy_prices_from_csv")
def test_load_interpolated_energy_prices_year_with_overnight(mock_read: MagicMock) -> None:
    """Arrange: prepare a csv containing energy prices with ISO datetimes.

    Act: call load_interpolated_energy_prices_year.
    Assert: returned list length, datetime tzinfo and computed prices are as expected.
    """
    # Arrange
    start_datetime = datetime(year=2024, month=1, day=1, tzinfo=UTC)
    iso_datetimes = [(start_datetime + timedelta(minutes=15 * t)).isoformat() for t in range(366 * 96)]
    prices = [i / 1000 for i in range(366 * 96)]
    df_input = pd.DataFrame({"Start date": iso_datetimes, energy_price_column: prices})
    mock_read.return_value = df_input

    expected_length = 366 * 96

    # Act
    result = energy_prices.load_interpolated_energy_prices_year(overnight_charging=True)

    # Assert
    assert isinstance(result, list)
    assert isinstance(result[0], ScaledEnergyPrice)
    assert len(result) == expected_length
    expected_prices = prices[3 * 96 :] + prices[2 * 96 : 5 * 96]
    for r in range(len(result)):
        assert isinstance(result[r].datetime, datetime)
        assert isinstance(result[r].price, float)
        assert result[r].datetime.tzinfo == ZoneInfo("Europe/Amsterdam")
        assert result[r].price == expected_prices[r] / 1000
