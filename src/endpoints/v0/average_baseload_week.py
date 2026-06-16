"""Router containing the endpoint to calculate the average weekly baseload profile."""

from __future__ import annotations

from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile

from src.application.baseload_profile import (
    calculate_baseload_profiles_average_week,
    calculate_shifted_baseload_profiles,
    get_baseload_profile_from_business_category,
    get_baseload_profile_from_file,
)
from src.application.validate_mffbas import validate_mffbas

average_baseload_week_router = APIRouter(prefix="/average_baseload_week", tags=["average baseload week"])


@average_baseload_week_router.post("/ko_profiles/")
def calculate_average_baseload_week_from_ko_profiles(
    business_category: Annotated[str, Form()], annual_consumption: Annotated[float, Form()]
) -> list[float]:
    """Calculates the average weekly baseload profile from the KO profile information.

    Args:
        business_category: The business category of the consumer.
        annual_consumption: The annual consumption of the consumer in kWh.
    """
    baseload_profile = get_baseload_profile_from_business_category(business_category, int(annual_consumption))
    shifted_baseload_profile = calculate_shifted_baseload_profiles(baseload_profile)
    return calculate_baseload_profiles_average_week(shifted_baseload_profile)


@average_baseload_week_router.post("/input_file/")
def calculate_average_baseload_week_from_file(baseload_file: Annotated[UploadFile, File]) -> list[float]:
    """Calculates the average weekly baseload profile from the baseload file.

    Args:
        baseload_file: The baseload file containing the baseload profile.
    """
    baseload_df = pd.read_csv(baseload_file.file, sep=";", header=None)
    valid = validate_mffbas(baseload_df)
    baseload_profile = get_baseload_profile_from_file(baseload_df) if valid else []
    shifted_baseload_profile = calculate_shifted_baseload_profiles(baseload_profile)
    return calculate_baseload_profiles_average_week(shifted_baseload_profile)
