"""Router containing endpoints related to grid tariffs."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.grid_tariffs import calculate_grid_tariff_large, calculate_grid_tariff_small
from src.domain.grid_tariff import GridTariffDTOLargeConsumer, GridTariffDTOSmallConsumer

grid_tariff_router = APIRouter(prefix="/grid_tariff", tags=["grid tariff"])


@grid_tariff_router.post("/small_consumer")
def get_grid_tariff_small(grid_tariff_input: GridTariffDTOSmallConsumer) -> float:
    """Retrieves the grid tariff for the small consumer grid connection.

    Args:
        grid_tariff_input: the input for the small consumer grid tariff calculation.
    """
    return calculate_grid_tariff_small(grid_tariff_input)


@grid_tariff_router.post("/large_consumer")
def get_grid_tariff_large(grid_tariff_input: GridTariffDTOLargeConsumer) -> float:
    """Retrieves the grid tariff for the large consumer grid connection.

    Args:
        grid_tariff_input: the input for the large consumer grid tariff calculation.
    """
    return calculate_grid_tariff_large(grid_tariff_input)
