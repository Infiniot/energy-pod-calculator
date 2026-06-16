"""Contains functions to retrieve energy prices."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from src.config import days_in_current_year, energy_price_column, file_path_energy_prices, first_day_of_year
from src.domain.energy_prices import EnergyPrice, ScaledEnergyPrice
from src.utils.shift_time import shift_df_index_day_of_week


def read_energy_prices_from_csv(filepath: str) -> pd.DataFrame:
    """Reads Entsoe energy prices from file.

    Args:
        filepath: Path to the energy prices file.
    """
    return pd.read_csv(filepath)


def save_energy_prices_to_csv(energy_prices: pd.DataFrame, filepath: str) -> None:
    """Save Energy price data to csv.

    Args:
        energy_prices: Dataframe containing the energy prices.
        filepath: Path to save the energy prices file.
    """
    energy_prices.to_csv(filepath)


def convert_datetimes(data: pd.DataFrame) -> pd.DataFrame:
    """Converts datetimes in string format to datetime format with timezone.

    Args:
        data: Dataframe containing datetimes that need to be converted.
    """
    data["start_date"] = data["MTU (CET/CEST)"].apply(lambda x: x.split(" - ")[0])
    data["day"] = data["start_date"].apply(lambda x: int(x.split("/")[0]))
    data["month"] = data["start_date"].apply(lambda x: int(x.split("/")[1]))
    data["year"] = data["start_date"].apply(lambda x: int(x.split("/")[-1].split(" ")[0]))
    data["hour"] = data["start_date"].apply(
        lambda x: int(x.split(" ")[-1].split(":")[0])
        if x.split(" ")[-1] not in {"(CET)", "(CEST)"}
        else int(x.split(" ")[-2].split(":")[0])
    )
    data["minute"] = data["start_date"].apply(
        lambda x: int(x.split(" ")[-1].split(":")[1])
        if x.split(" ")[-1] not in {"(CET)", "(CEST)"}
        else int(x.split(" ")[-2].split(":")[1])
    )
    data["second"] = data["start_date"].apply(
        lambda x: int(x.split(" ")[-1].split(":")[2])
        if x.split(" ")[-1] not in {"(CET)", "(CEST)"}
        else int(x.split(" ")[-2].split(":")[2])
    )

    data["start_date_utc"] = data[["day", "month", "year", "hour", "minute", "second"]].apply(
        lambda x: datetime(
            year=x["year"],
            month=x["month"],
            day=x["day"],
            hour=x["hour"],
            minute=x["minute"],
            second=x["second"],
            tzinfo=ZoneInfo("Europe/Berlin"),
        ),
        axis=1,
    )

    energy_prices = pd.DataFrame({energy_price_column: data[energy_price_column], "Start date": data["start_date_utc"]})

    energy_prices["Start date"] = pd.to_datetime(energy_prices["Start date"], utc=True) + timedelta(hours=1)

    energy_prices.loc[7202, "Start date"] = datetime(year=2024, month=10, day=27, hour=2, tzinfo=UTC)

    return energy_prices.reset_index(drop=True)


def interpolate_energy_prices(data: pd.DataFrame) -> pd.DataFrame:
    """Interpolates the energy prices for each quarter of an hour.

    Args:
        data: Dataframe containing the energy prices.
    """
    start_date = data["Start date"].min()
    end_date = data["Start date"].max()

    date_range_15min = pd.date_range(start=start_date, end=end_date + timedelta(minutes=45), freq="15min")
    prices = []
    for t in date_range_15min:
        prices.append(  # noqa: PERF401
            data[  # noqa: PD011
                (data["Start date"].dt.date == t.date()) & (data["Start date"].dt.hour == t.hour)
            ][energy_price_column].values[0]
        )

    return pd.DataFrame({"Start date": date_range_15min, energy_price_column: prices})


def etl_energy_prices(filepath: str) -> None:
    """Convert string datetimes to datetime objects with timezones.

    Args:
        filepath: Path to the energy prices file.
    """
    data = read_energy_prices_from_csv(filepath)

    new_data = convert_datetimes(data)

    new_data = interpolate_energy_prices(new_data)

    save_energy_prices_to_csv(new_data, file_path_energy_prices)


def load_energy_prices() -> list[EnergyPrice]:
    """Loads Entsoe energy prices from file."""
    energy_data = read_energy_prices_from_csv(file_path_energy_prices)

    prices = energy_data[energy_price_column].to_list()
    datetimes = energy_data["Start date"].apply(lambda x: x.split(" - ")[0]).to_list()

    return [EnergyPrice(datetime=datetimes[i], price=prices[i]) for i in range(len(prices))]


def load_interpolated_energy_prices_year(*, overnight_charging: bool = False) -> list[ScaledEnergyPrice]:
    """Loads interpolated energy prices from csv file."""
    c_t = read_energy_prices_from_csv("./input/energy_prices/energy_prices_2024.csv")
    c_t["Start date"] = pd.to_datetime(c_t["Start date"], utc=True)
    c_t["Day of week"] = c_t["Start date"].apply(lambda x: x.weekday())

    start_datetime = first_day_of_year
    days = days_in_current_year + int(overnight_charging)

    c_t_shifted = shift_df_index_day_of_week(
        int(c_t["Day of week"].iloc[0]), start_datetime.weekday(), c_t, overnight_charging=overnight_charging
    )

    datetimes = [start_datetime + timedelta(minutes=15 * t) for t in range(days * 96)]
    prices = c_t_shifted[energy_price_column].to_numpy() / 1000

    return [ScaledEnergyPrice(datetime=datetimes[i], price=prices[i]) for i in range(len(datetimes))]
