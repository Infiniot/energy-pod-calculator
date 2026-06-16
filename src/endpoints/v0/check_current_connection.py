"""The router containing the endpoint to check and update the size of the current connection."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.update_current_connection import UpdateCurrentConnection
from src.domain.energy_dto import (
    EnergyDTOLargeConsumer,
    EnergyDTOLargeConsumerCLC,
    EnergyDTOSmallConsumer,
    EnergyDTOUpdate,
)

check_current_connection_router = APIRouter(prefix="/check_current_connection", tags=["check current connection"])


@check_current_connection_router.post("/")
def get_check_current_connection(
    energy_input: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC,
) -> EnergyDTOUpdate:
    """Retrieves results after checking if the size of the current connection is sufficient.

    Args:
        energy_input: Input parameters as DTO.
    """
    return UpdateCurrentConnection(energy_input).calculate_updated_energy_dtos()
