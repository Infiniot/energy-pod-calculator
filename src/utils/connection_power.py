"""Functions related to the connection power capacity."""

import pandas as pd

from src.domain.connection_power import ConnectionPower
from src.utils.datetime_year import get_datetimes_year


def connection_power_to_year(connection_power: float, *, overnight_charging: bool = False) -> list[ConnectionPower]:
    """Extends the connection power to a year."""
    datetimes = get_datetimes_year(overnight_charging=overnight_charging)
    return connection_power_df_to_list(pd.DataFrame({"datetime": datetimes, "power": connection_power}))


def connection_power_df_to_list(connection_power_df: pd.DataFrame) -> list[ConnectionPower]:
    """Converts a connection power dataframe to a list of ConnectionPower objects."""
    datetimes = connection_power_df["datetime"]
    powers = connection_power_df["power"]
    return [ConnectionPower(datetime=datetimes.iloc[i], power=powers.iloc[i]) for i in range(len(datetimes))]
