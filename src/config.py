"""Module to import variables."""

from datetime import datetime
from zoneinfo import ZoneInfo

from decouple import config

frontend_url = config("FRONTEND_URL", default="http://localhost:5173")
energy_price_column = "Day-ahead Price (EUR/MWh)"
file_path_energy_prices = "input/energy_prices/energy_prices_2024.csv"
file_path_baseloads = "input/ko_profiles/"
file_path_grid_tariffs_small = "./input/grid/tariffs_small.csv"
file_path_grid_tariffs_large = "./input/grid/tariffs_large.xlsx"
file_path_pc6 = "./input/grid/pc6.csv"
first_day_of_year = datetime.now(tz=ZoneInfo("Europe/Amsterdam")).replace(
    month=1, day=1, hour=0, minute=0, second=0, microsecond=0
)
days_in_current_year = 365 + (first_day_of_year.year % 4 == 0)
fast_charging_tariff = 0.85
battery_step_size = 100
min_battery_steps = 1
max_battery_steps = 10
battery_price_per_kwh = 200
cp_price_per_kw = 100
battery_loss_charge = 0.1
battery_loss_discharge = 0.1
ere_tariff = 0.1
energy_price_markup = 0.0025
