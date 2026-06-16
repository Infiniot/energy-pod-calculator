"""Router containing the endpoint to check if the baseload file is in valid MFFBAS format."""

from __future__ import annotations

from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, UploadFile

from src.application.validate_mffbas import validate_mffbas

validate_baseload_file_router = APIRouter(prefix="/validate_baseload_file", tags=["validate baseload file"])


@validate_baseload_file_router.post("/")
def validate_baseload_file(baseload_file: Annotated[UploadFile, File]) -> bool:
    """Validates the baseload file and returns the yearly baseload profile."""
    try:
        baseload_df = pd.read_csv(baseload_file.file, sep=";", header=None)
        return validate_mffbas(baseload_df)
    except Exception:  # noqa: BLE001
        return False
