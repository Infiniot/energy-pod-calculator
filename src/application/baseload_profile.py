"""Contains functions to calculate a baseload profile."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from src.config import days_in_current_year, file_path_baseloads, first_day_of_year
from src.domain.baseload_profile import BaseloadProfile
from src.utils.shift_time import shift_df_index_day_of_week


def map_business_category(business_category: str) -> str:
    """Maps the received string to a business category."""
    options = {
        "Farmer": "AGRARIER",
        "Data center": "DATACENTER",
        "Industry": "INDUSTRIE",
        "Office and education": "KANTOOR_ONDERWIJS",
        "Logistics": "LOGISTIEK",
        "Other": "OVERIG",
        "Greenhouse horticulture": "GLASTUINBOUW",
        "Agrariër": "AGRARIER",
        "Datacenter": "DATACENTER",
        "Industrie": "INDUSTRIE",
        "Kantoor en onderwijs": "KANTOOR_ONDERWIJS",
        "Logistiek": "LOGISTIEK",
        "Overig": "OVERIG",
        "Glastuinbouw": "GLASTUINBOUW",
    }
    mapped = options.get(business_category)
    if mapped is None:
        message = f"Unknown business category: {business_category}"
        raise ValueError(message)
    return mapped


def get_baseload_profile_from_business_category(
    business_category: str, annual_consumption: int
) -> list[BaseloadProfile]:
    """Reads the baseload profile corresponding to the specified business category and applies scaling.

    Args:
        business_category: The business category of the company.
        annual_consumption: The total energy consumption in one year.
    """
    mapped_category = map_business_category(business_category)
    baseloads = pd.read_csv(f"{file_path_baseloads}{mapped_category}.csv", sep=";")

    total_consumption = sum(baseloads["WAARDE"])
    peak_consumption = annual_consumption / (0.25 * total_consumption)

    baseloads["power_consumption"] = baseloads.apply(
        lambda row: round(row["WAARDE"] * peak_consumption, 2),
        axis=1,
    )
    baseloads["Start date"] = baseloads["DATUM_TIJDSTIP"].apply(lambda x: datetime.fromisoformat(x))

    return baseloads_df_to_list(baseloads)


def get_baseload_profile_from_file(baseload_file_df: pd.DataFrame) -> list[BaseloadProfile]:
    """Extract the relevant data from the baseload input file dataframe and return it as a list of BaseloadProfiles.

    Args:
        baseload_file_df: the baseload input file as a dataframe.
    """
    datetimes = baseload_file_df[7:].reset_index(drop=True).iloc[:, 1]
    datetimes = datetimes.apply(
        lambda x: datetime.strptime(x, "%d/%m/%Y %H:%M").replace(tzinfo=ZoneInfo("Europe/Amsterdam"))
    ).to_list()
    col = baseload_file_df.iloc[4][baseload_file_df.iloc[4] == "A"].index[0]
    powers = baseload_file_df[7:].reset_index(drop=True).iloc[:, col]
    powers = powers.apply(lambda x: float(x.replace(",", ".")))

    return [BaseloadProfile(datetime=datetimes[i], power=round(powers[i], 2)) for i in range(len(datetimes))]


def calculate_shifted_baseload_profiles(
    baseloads: list[BaseloadProfile], *, overnight_charging: bool = False
) -> list[BaseloadProfile]:
    """Shifts the baseload profile for a whole year to start on the weekday of the first day of the current year.

    Args:
        baseloads: List of BaseloadProfiles containing the baseload profile for a year.
        overnight_charging: Boolean that indicates if vehicles can charge overnight.
    """
    baseloads_df = baseloads_list_to_df(baseloads)
    baseloads_df["Day of week"] = baseloads_df["Start date"].apply(lambda x: x.weekday())

    baseloads_shifted = shift_df_index_day_of_week(
        int(baseloads_df["Day of week"].iloc[0]),
        first_day_of_year.weekday(),
        baseloads_df,
        overnight_charging=overnight_charging,
    )

    days = days_in_current_year + int(overnight_charging)
    datetimes = [first_day_of_year + timedelta(minutes=15 * t) for t in range(days * 96)]
    powers = baseloads_shifted["power_consumption"].tolist()

    return [BaseloadProfile(datetime=datetimes[i], power=powers[i]) for i in range(len(datetimes))]


def baseloads_df_to_list(baseloads_shifted: pd.DataFrame) -> list[BaseloadProfile]:
    """Converts baseloads from dataframe to list of BaseloadProfiles.

    Args:
        baseloads_shifted: Dataframe containing the shifted baseload profile for a year.
    """
    datetimes = baseloads_shifted["Start date"]
    powers = baseloads_shifted["power_consumption"]
    return [BaseloadProfile(datetime=datetimes[i], power=round(powers[i], 4)) for i in range(len(datetimes))]


def baseloads_list_to_df(baseloads: list[BaseloadProfile]) -> pd.DataFrame:
    """Converts baseloads from list of BaseloadProfiles to dataframe.

    Args:
        baseloads: List of BaseloadProfiles containing the baseload profile for a year.
    """
    datetimes = [baseload.datetime for baseload in baseloads]
    powers = [baseload.power for baseload in baseloads]
    return pd.DataFrame({"Start date": datetimes, "power_consumption": powers})


def calculate_baseload_profiles_average_week(baseloads_year: list[BaseloadProfile]) -> list[float]:
    """Calculates an average week of baseload profile from baseload profiles over a year.

    Args:
        baseloads_year: the baseload power consumption over a year.
    """
    baseloads_week = []
    baseloads_year_df: pd.DataFrame = pd.DataFrame(
        {"Start date": [b.datetime for b in baseloads_year], "power_consumption": [b.power for b in baseloads_year]}
    )

    baseloads_year_df["Day of week"] = baseloads_year_df["Start date"].apply(lambda x: x.weekday())

    first_week_start_index = baseloads_year_df["Day of week"][baseloads_year_df["Day of week"] == 0].index[0]

    start_week, end_week = first_week_start_index, first_week_start_index + 7 * 96

    while end_week < len(baseloads_year_df):
        baseloads_week.append(baseloads_year_df.iloc[start_week:end_week]["power_consumption"].tolist())

        start_week += 7 * 96
        end_week += 7 * 96

    return np.average(np.array(baseloads_week), axis=0).tolist()


def get_annual_consumption_from_baseload_list(baseloads: list[BaseloadProfile]) -> float:
    """Calculates the annual consumption from the baseload profile.

    Args:
        baseloads: List of BaseloadProfiles containing the baseload profile for a year.
    """
    return round(sum(baseload.power for baseload in baseloads) * 0.25, 2)
