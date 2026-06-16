"""Function to retrieve datetimes over a year with 15-minute intervals."""

from datetime import timedelta

from pandas.core.indexes.datetimes import DatetimeIndex  # type: ignore[import-untyped]

from src.config import days_in_current_year, first_day_of_year


def get_datetimes_year(*, overnight_charging: bool = False) -> DatetimeIndex:
    """Returns datetimes over a year with 15-minute intervals."""
    start_datetime = first_day_of_year
    days = days_in_current_year + int(overnight_charging)
    return [start_datetime + timedelta(minutes=15 * t) for t in range(96 * days)]
