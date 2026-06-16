"""Functions related to time frames."""

import time


def calculate_indices_arrival_departure_time(arrival_time: str, departure_time: str) -> tuple[int, int]:
    """Determines the indices of the arrival and departure time of the first day of the year."""
    t_arr_split = time.strptime(arrival_time, "%H:%M")
    t_arr_hours, t_arr_minutes = t_arr_split.tm_hour, t_arr_split.tm_min
    t_arr_ind = t_arr_hours * 4 + t_arr_minutes // 15

    t_dep_split = time.strptime(departure_time, "%H:%M")
    t_dep_hours, t_dep_minutes = t_dep_split.tm_hour, t_dep_split.tm_min
    t_dep_ind = t_dep_hours * 4 + t_dep_minutes // 15
    if departure_time < arrival_time:
        t_dep_ind += 96

    return t_arr_ind, t_dep_ind
