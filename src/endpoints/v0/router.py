"""Module containing all the routers for the v0 version of the API."""

from fastapi import APIRouter

from .average_baseload_week import average_baseload_week_router
from .baseload_profile import baseload_profile_router
from .check_current_connection import check_current_connection_router
from .energy_costs_savings import energy_costs_savings_router
from .grid_tariff import grid_tariff_router
from .payback_time import payback_time_router
from .small_consumer_connection import small_consumer_connection_router
from .validate_baseload_file import validate_baseload_file_router
from .validate_energy_demand import validate_energy_demand_router
from .with_energy_pod import with_energy_pod_router
from .without_energy_pod import without_energy_pod_router
from .yearly_savings import yearly_savings_router

v0_router = APIRouter(prefix="/v0")
router_list = [
    average_baseload_week_router,
    baseload_profile_router,
    small_consumer_connection_router,
    grid_tariff_router,
    with_energy_pod_router,
    without_energy_pod_router,
    payback_time_router,
    yearly_savings_router,
    check_current_connection_router,
    validate_energy_demand_router,
    validate_baseload_file_router,
    energy_costs_savings_router,
]

for router in router_list:
    router.tags.append("v0")
    v0_router.include_router(router)
