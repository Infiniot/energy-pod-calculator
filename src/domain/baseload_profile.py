"""Contains the pydantic models related to baseload profiles."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003

from pydantic import BaseModel, ConfigDict


class BaseloadProfile(BaseModel):
    """A pydantic model representing a baseload profile entry."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    power: float
