"""Contains the pydantic models related to energy input for the EnergyPod and without EnergyPod endpoints."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import time

import pandas as pd
from pydantic import BaseModel, ConfigDict

from src.application.small_consumer_connection import calculate_small_consumer_connection
from src.domain.baseload_profile import BaseloadProfile
from src.domain.connection_power import ConnectionFits, ConnectionPower
from src.domain.vehicle_info import VehicleInfoDTO
from src.utils.connection_power import connection_power_df_to_list, connection_power_to_year
from src.utils.datetime_year import get_datetimes_year


class EnergyDTO(BaseModel, ABC):
    """A pydantic model representing the input for the EnergyPod and without EnergyPod endpoints as DTO."""

    model_config = ConfigDict(from_attributes=True)

    vehicle_info: VehicleInfoDTO
    arrival_time: str
    departure_time: str
    baseload: list[BaseloadProfile]
    zip_code: str
    battery_capacity: int | None
    charge_point_power: int

    @abstractmethod
    def calculate_contracted_capacity(self) -> float:
        """Calculates the maximum contract capacity."""
        ...

    @abstractmethod
    def calculate_contracted_capacity_year(self, *, overnight_charging: bool = False) -> list[ConnectionPower]:
        """Calculates contracted capacity for a whole year."""
        ...

    @abstractmethod
    def calculate_connection_capacity(self) -> float:
        """Calculates the connection capacity."""
        ...


class EnergyDTOSmallConsumer(EnergyDTO):
    """A pydantic model representing the input for the small consumer endpoints as DTO."""

    connection_category: str

    def calculate_contracted_capacity(self) -> float:
        """Calculates the maximum contract capacity."""
        return calculate_small_consumer_connection(self.connection_category)

    def calculate_contracted_capacity_year(self, *, overnight_charging: bool = False) -> list[ConnectionPower]:
        """Calculates the contracted capacity for a whole year."""
        connection_power = calculate_small_consumer_connection(self.connection_category)
        return connection_power_to_year(connection_power, overnight_charging=overnight_charging)

    def calculate_connection_capacity(self) -> float:
        """Calculates the connection capacity."""
        return calculate_small_consumer_connection(self.connection_category)

    def update_connection_category(self, connection_update: str) -> None:
        """Updates current connection with a new value."""
        self.connection_category = connection_update


class EnergyDTOLargeConsumer(EnergyDTO):
    """A pydantic model representing the input for the large consumer endpoints as DTO."""

    contract_capacity: float
    connection_capacity: float

    def calculate_contracted_capacity(self) -> float:
        """Calculates the maximum contract capacity."""
        return self.contract_capacity * 1000

    def calculate_contracted_capacity_year(self, *, overnight_charging: bool = False) -> list[ConnectionPower]:
        """Calculates the contracted capacity for a whole year."""
        return connection_power_to_year(self.contract_capacity * 1000, overnight_charging=overnight_charging)

    def calculate_connection_capacity(self) -> float:
        """Calculates the connection capacity."""
        return self.connection_capacity * 1000

    def update_contracted_capacity(self, connection_update: float) -> None:
        """Updates the contract capacity with a new value."""
        self.contract_capacity = round(float(self.contract_capacity + connection_update / 1000) * 1.15, 4)
        self.connection_capacity = max(self.contract_capacity, self.connection_capacity)


class EnergyDTOLargeConsumerCLC(EnergyDTOLargeConsumer):
    """A pydantic model representing the input for the large consumer with CLC endpoints as DTO."""

    clc_start: str
    clc_end: str
    clc_capacity: float

    def calculate_contracted_capacity_year(self, *, overnight_charging: bool = False) -> list[ConnectionPower]:
        """Calculates the contracted capacity for a whole year."""
        contract_capacity_kw = self.contract_capacity * 1000
        clc_start_time = pd.to_datetime(self.clc_start).time()
        clc_end_time = pd.to_datetime(self.clc_end).time()
        clc_capacity = self.clc_capacity * 1000

        datetimes = get_datetimes_year(overnight_charging=overnight_charging)
        clc_df = pd.DataFrame({"datetime": datetimes, "power": contract_capacity_kw})
        if clc_end_time < clc_start_time:
            clc_start_time_1 = time(0, 0)
            clc_end_time_1 = clc_end_time
            clc_start_time_2 = clc_start_time
            clc_end_time_2 = time(23, 45)
            clc_mask = (
                (clc_df["datetime"].dt.time >= clc_start_time_1) & (clc_df["datetime"].dt.time < clc_end_time_1)
            ) | ((clc_df["datetime"].dt.time >= clc_start_time_2) & (clc_df["datetime"].dt.time <= clc_end_time_2))
        else:
            clc_mask = (clc_df["datetime"].dt.time >= clc_start_time) & (clc_df["datetime"].dt.time < clc_end_time)
        clc_df.loc[clc_mask, "power"] = clc_capacity
        return connection_power_df_to_list(clc_df)


class EnergyDTOUpdate(BaseModel):
    """A pydantic model representing the result of the check current connection endpoint as DTO."""

    model_config = ConfigDict(from_attributes=True)

    connection_fits: ConnectionFits
    without_ep_dto: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC
    with_ep_dto: EnergyDTOSmallConsumer | EnergyDTOLargeConsumer | EnergyDTOLargeConsumerCLC
