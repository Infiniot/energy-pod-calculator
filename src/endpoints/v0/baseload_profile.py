"""Router containing the endpoint to calculate the yearly baseload profile."""

from __future__ import annotations

from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, Form, UploadFile

from src.application.baseload_profile import (
    get_baseload_profile_from_business_category,
    get_baseload_profile_from_file,
)
from src.application.validate_mffbas import validate_mffbas
from src.domain.baseload_profile import BaseloadProfile

baseload_profile_router = APIRouter(prefix="/baseload_profile", tags=["baseload profile"])


@baseload_profile_router.post("/ko_profiles/")
def calculate_baseload_profile_from_ko_profiles(
    business_category: Annotated[str, Form()], annual_consumption: Annotated[float, Form()]
) -> list[BaseloadProfile]:
    """Calculates the yearly baseload profile from the KO profile information.

    Args:
        business_category: The business category of the consumer.
        annual_consumption: The annual consumption of the consumer in kWh.
    """
    return get_baseload_profile_from_business_category(business_category, int(annual_consumption))


@baseload_profile_router.post("/input_file/")
def calculate_baseload_profile_from_file(baseload_file: Annotated[UploadFile, File]) -> list[BaseloadProfile]:
    """Calculates the yearly baseload profile from the baseload file.

    Args:
        baseload_file: The baseload file containing the baseload profile.
    """
    baseload_df = pd.read_csv(baseload_file.file, sep=";", header=None)
    valid = validate_mffbas(baseload_df)
    return get_baseload_profile_from_file(baseload_df) if valid else []
