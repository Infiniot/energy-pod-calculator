"""Module for validating baseload files."""

import pandas as pd


def validate_time_series(input_df: pd.DataFrame, mffbas_time_series: pd.DataFrame) -> bool:
    """Validates if the time series in the input file is in correct format (CET, CEST)."""
    format_profiles = mffbas_time_series[7:].reset_index(drop=True)
    format_time_series = format_profiles.iloc[:, :3]
    format_time_series = format_time_series.apply(pd.to_datetime, format="%d-%m-%Y %H:%M")

    input_file_time_series = input_df[7:].reset_index(drop=True).iloc[:, :3]
    input_file_time_series = input_file_time_series.apply(pd.to_datetime, format="%d/%m/%Y %H:%M")
    input_file_time_series = input_file_time_series.apply(lambda x: x + pd.DateOffset(years=-1))

    input_file_time_series_year = input_file_time_series.iloc[0, 0].year
    format_time_series_year = format_time_series.iloc[0, 0].year
    if format_time_series_year != input_file_time_series_year:
        year_diff = input_file_time_series_year - format_time_series_year
        format_time_series = format_time_series.apply(lambda x: x + pd.DateOffset(years=year_diff))

    return format_time_series.equals(input_file_time_series)


def validate_null_values(input_df: pd.DataFrame) -> bool:
    """Validates that there are no null values in the input file."""
    input_profiles = input_df[7:].reset_index(drop=True)
    return not input_profiles.iloc[:, 3:].isna().any().any()


def validate_mffbas(baseload_df: pd.DataFrame) -> bool:
    """Validates that the file is in mffbas format."""
    valid = True
    mffbas_format_file = pd.read_csv(
        "input/Standaardprofiel E4A avondtarief elektriciteit 2026 versie E4A_21 1.00.csv", sep=";", header=None
    )

    if not validate_time_series(baseload_df, mffbas_format_file):
        valid = False
    if not validate_null_values(baseload_df):
        valid = False
    return valid
