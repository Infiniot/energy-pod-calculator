"""Contains the pydantic models related to connection capacity powers."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ConnectionPower(BaseModel):
    """A pydantic model representing a connection capacity power entry."""

    model_config = ConfigDict(from_attributes=True)

    datetime: datetime
    power: float


class SmallConsumerConnectionTypes(Enum):
    """Enum types for small consumer connection categories."""

    ONE_TIMES_SIX_AMPERE = "1 x 6A"
    ONE_TIMES_TEN_AMPERE = "1 x 10A"
    ONE_TIMES_TWENTY_FIVE_AMPERE = "1 x 25A"
    ONE_TIMES_THIRTY_FIVE_AMPERE = "1 x 35A"
    ONE_TIMES_FORTY_AMPERE = "1 x 40A"
    THREE_TIMES_TWENTY_FIVE_AMPERE = "3 x 25A"
    THREE_TIMES_THIRTY_FIVE_AMPERE = "3 x 35A"
    THREE_TIMES_FORTY_AMPERE = "3 x 40A"
    THREE_TIMES_FIFTY_AMPERE = "3 x 50A"
    THREE_TIMES_SIXTY_THREE_AMPERE = "3 x 63A"
    THREE_TIMES_EIGHTY_AMPERE = "3 x 80A"


class SmallConsumerCategory(BaseModel):
    """A pydantic model representing the power range of a small consumer connection category."""

    model_config = ConfigDict(from_attributes=True)

    connection_type: SmallConsumerConnectionTypes
    min_connection_power: float
    max_connection_power: float


class ConnectionFits(Enum):
    """Enum types that indicate if the current connection fits."""

    SHORTAGE = -1
    CONSTANT = 0
    ABUNDANCE = 1
