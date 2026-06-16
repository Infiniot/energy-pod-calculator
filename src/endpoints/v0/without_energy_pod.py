"""The router containing the endpoints for calculating the energy usage without EnergyPod."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.without_energy_pod import calculate_results_without_energypod
from src.domain.energy_dto import EnergyDTOLargeConsumer, EnergyDTOLargeConsumerCLC, EnergyDTOSmallConsumer
from src.domain.without_energy_pod import ResultWithoutEP

without_energy_pod_router = APIRouter(prefix="/without_energypod", tags=["without EnergyPod"])


@without_energy_pod_router.post("/small_consumer")
def get_without_energy_pod_small_consumer(
    without_energy_pod_input: EnergyDTOSmallConsumer,
) -> ResultWithoutEP:
    """Retrieves energy usage for a small consumer with the given parameters.

    Args:
        without_energy_pod_input: Data transfer object containing input parameters for case without EnergyPod.
    """
    return calculate_results_without_energypod(without_energy_pod_input)


@without_energy_pod_router.post("/large_consumer")
def get_without_energy_pod_large_consumer(
    without_energy_pod_input: EnergyDTOLargeConsumer,
) -> ResultWithoutEP:
    """Retrieves energy usage for a large consumer with the given parameters.

    Args:
        without_energy_pod_input: Data transfer object containing input parameters for case without EnergyPod.
    """
    return calculate_results_without_energypod(without_energy_pod_input)


@without_energy_pod_router.post("/large_consumer/clc")
def get_without_energy_pod_large_consumer_clc(
    without_energy_pod_input: EnergyDTOLargeConsumerCLC,
) -> ResultWithoutEP:
    """Retrieves energy usage for a large consumer with a capacity limiting contract with the given parameters.

    Args:
        without_energy_pod_input: Data transfer object containing input parameters for case without EnergyPod.
    """
    return calculate_results_without_energypod(without_energy_pod_input)
