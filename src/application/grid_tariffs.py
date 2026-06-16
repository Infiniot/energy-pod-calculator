"""Contains functions for determining the yearly grid tariff based on zip code and connection information."""

import pandas as pd

from src.application.baseload_profile import get_annual_consumption_from_baseload_list
from src.config import file_path_grid_tariffs_large, file_path_grid_tariffs_small, file_path_pc6
from src.custom_exceptions.grid_error import (
    ConnectionCapacityError,
    GridTariffDSORangeError,
    ZipCodeError,
)
from src.domain.grid_tariff import GridTariffDTOLargeConsumer, GridTariffDTOSmallConsumer


def read_pc6_dso_map() -> pd.DataFrame:
    """Load pc6 zip code to DSO mapping."""
    return pd.read_csv(file_path_pc6, sep=";")


def read_grid_tariffs_small() -> pd.DataFrame:
    """Load grid tariffs from csv file."""
    return pd.read_csv(file_path_grid_tariffs_small, sep=";")


def get_dso(zip_code: str) -> str:
    """Derive the dso from the pc6 zip code.

    Args:
        zip_code: The pc6 zip code of the consumer.
    """
    zip_code = zip_code.replace(" ", "")
    pc6 = read_pc6_dso_map()
    dso_rows = pc6[pc6["postcode"] == zip_code]["RNB_postcode"].to_numpy()
    if len(dso_rows) != 1:
        raise ZipCodeError
    return dso_rows[0]


def map_connection_to_range(connection: str) -> str:
    """Maps the connection category to the corresponding capacity range.

    Args:
        connection: The connection category of the consumer.
    """
    connection_to_range = {
        "1 x 6A": "≤ 1x10A",
        "1 x 10A": "≤ 1x10A",
        "1 x 25A": "≤ 3x25A",
        "1 x 35A": "≤ 3x25A",
        "1 x 40A": "≤ 3x25A",
        "3 x 25A": "≤ 3x25A",
        "3 x 35A": "≤ 3x35A",
        "3 x 40A": "≤ 3x50A",
        "3 x 50A": "≤ 3x50A",
        "3 x 63A": "≤ 3x63A",
        "3 x 80A": "≤ 3x80A",
    }
    try:
        connection_range = connection_to_range[connection]
    except KeyError as e:
        raise ConnectionCapacityError(connection) from e
    return connection_range


def calculate_grid_tariff_small(grid_tariff_input: GridTariffDTOSmallConsumer) -> float:
    """Compute the yearly grid tariff for a small consumer.

    Args:
        grid_tariff_input: GridTariffDTOSmallConsumer containing the input data for calculating the grid tariff for a
        small consumer.
    """
    dso = get_dso(grid_tariff_input.zip_code)

    connection_range = map_connection_to_range(grid_tariff_input.connection_category)
    tariffs = read_grid_tariffs_small()
    tariff_rows = tariffs[tariffs["Company"] == dso][connection_range].to_numpy()
    return float(round(tariff_rows[0], 2))


def calculate_grid_tariff_large(grid_tariff_input: GridTariffDTOLargeConsumer) -> float:
    """Compute the yearly grid tariff for a large consumer.

    Args:
        grid_tariff_input: GridTariffDTOLargeConsumer containing the input data for calculating the grid tariff for a
        large consumer.
    """
    dso = get_dso(grid_tariff_input.zip_code)

    xls = pd.ExcelFile(file_path_grid_tariffs_large)
    tariffs = pd.read_excel(xls, "Grootverbruik")
    tariffs = tariffs.loc[tariffs["Netbeheerder"] == dso]

    row = tariffs[
        (tariffs["Netvlak ondergrens"] < grid_tariff_input.connection_capacity)
        & (tariffs["Netvlak bovengrens"] >= grid_tariff_input.connection_capacity)
    ]
    if len(row) == 0:
        message = f"Connection capacity {grid_tariff_input.connection_capacity} kW is out of range for DSO {dso}."
        raise GridTariffDSORangeError(message)

    annual_consumption = get_annual_consumption_from_baseload_list(grid_tariff_input.baseload)

    annual_tariff = (
        row["Vastrecht aansluiting €/jaar"]
        + row["Vastrecht transport €/jaar"]
        + row["Transport vermogen tarief €/kWjaar"] * grid_tariff_input.contract_capacity * 1000
        + row["Max vermogen tarief €/kW/maand"] * grid_tariff_input.connection_capacity * 1000 * 12
        + row["Energie tarief €/kWh"] * annual_consumption
    )
    return round(annual_tariff.iloc[0], 2)
