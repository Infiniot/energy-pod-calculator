"""Contains the pydantic models related to the grid tariff."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from src.domain.baseload_profile import BaseloadProfile


class GridTariffDTOSmallConsumer(BaseModel):
    """A pydantic model representing the input for the small consumer grid tariff endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    zip_code: str
    connection_category: str


class GridTariffDTOLargeConsumer(BaseModel):
    """A pydantic model representing the input for the large consumer grid tariff endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    zip_code: str
    connection_capacity: float
    contract_capacity: float
    baseload: list[BaseloadProfile]
