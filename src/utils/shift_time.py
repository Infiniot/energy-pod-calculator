"""Functions related to time shifts."""

import pandas as pd

from src.config import first_day_of_year


def find_shift_index_day_of_week(old_day_of_week: int, new_day_of_week: int) -> int:
    """Finds the index that corresponds to the shift in day of week."""
    if old_day_of_week < new_day_of_week:
        return (new_day_of_week - old_day_of_week) * 96
    return (6 - old_day_of_week + new_day_of_week + 1) * 96


def shift_df_index_day_of_week(
    old_day_of_week: int, new_day_of_week: int, df: pd.DataFrame, *, overnight_charging: bool = False
) -> pd.DataFrame:
    """Shifts dataframe based on the index corresponding to the shift in day of week."""
    shift_index_day_of_week = find_shift_index_day_of_week(old_day_of_week, new_day_of_week)
    year_df = df.iloc[0]["Start date"].year
    shift_index_leap_year = 2 if year_df % 4 == 0 else 1

    return pd.concat(
        [
            df.iloc[shift_index_day_of_week:],
            df.iloc[
                96 * shift_index_leap_year : shift_index_day_of_week
                + (1 + int(first_day_of_year.year % 4 == 0) + int(overnight_charging)) * 96
            ],
        ]
    )
