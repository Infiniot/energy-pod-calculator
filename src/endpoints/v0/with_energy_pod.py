"""The router containing endpoints for calculating EnergyPod power usage."""

from __future__ import annotations

from fastapi import APIRouter

from src.application.with_energy_pod import EnergyPodPower
from src.domain.energy_dto import EnergyDTOLargeConsumer, EnergyDTOLargeConsumerCLC, EnergyDTOSmallConsumer
from src.domain.energy_pod import EnergyPodResults

with_energy_pod_router = APIRouter(prefix="/with_energypod", tags=["with energy pod"])


@with_energy_pod_router.post("/small_consumer")
def get_energy_pod_small_consumer(energy_pod_input: EnergyDTOSmallConsumer) -> EnergyPodResults:
    """Retrieves EnergyPod power usage for the given parameters.

    Args:
        energy_pod_input: Input parameters for EnergyPod as DTO.
    """
    return EnergyPodPower(energy_pod_input).calculate_energy_pod_power_results()


@with_energy_pod_router.post("/large_consumer")
def get_energy_pod_large_consumer(energy_pod_input: EnergyDTOLargeConsumer) -> EnergyPodResults:
    """Retrieves EnergyPod power usage for the given parameters.

    Args:
        energy_pod_input: Input parameters for EnergyPod as DTO.
    """
    return EnergyPodPower(energy_pod_input).calculate_energy_pod_power_results()


@with_energy_pod_router.post("/large_consumer/clc")
def get_energy_pod_large_consumer_with_clc(
    energy_pod_input: EnergyDTOLargeConsumerCLC,
) -> EnergyPodResults:
    """Retrieves EnergyPod power usage for the given parameters.

    Args:
        energy_pod_input: Input parameters for EnergyPod as DTO.
    """
    return EnergyPodPower(energy_pod_input).calculate_energy_pod_power_results()
