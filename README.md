# EnergyPod Calculator
The EnergyPod Calculator is a repository containing an API that can be used to calculate the business case for purchasing an EnergyPod. An EnergyPod is a smart charging system containing a battery and several charge points, that can be controlled to obtain a cost- and energy-saving charging solution. It is developed as part of the [DITM project(https://brainporteindhoven.com/nl/innovatie/mobility/programmabureau-smart-green-mobility/digitale-infrastructuur-voor-toekomstbestendige-mobiliteit)], which is a collaboration between several companies and knowledge institutes focused on digital and future-proof mobility. The project is led by Brainport Eindhoven.

## About the project
This tool aims to calculate the business case for purchasing an EnergyPod and provide an estimate for the payback time and potential savings. Two different scenario's are compared: a scenario with and one without the usage of an EnergyPod.

 The most important features that are included in this tool:
 - **Load balancer**: A load balancer mechanism is built to distribute the energy demand over the charge site during the charging period. It can be used to check if the configured input fits within the provided grid connection for both the scenario with and without EnergyPod. If it does not fit, the output of the load balancer can be used to determine the minimum required grid connection for both scenario's, ensuring that there is a logical outcome in the subsequent steps.
 - **Optimization problem**: The battery power usage and charge point power usage in combination with energy prices and the configured input are fit into an optimization problem to minimize the total yearly energy costs for the scenario with EnergyPod.
 - **Cost calculations**: There are several modules to compute costs related to both scenarios, such as energy costs, grid tariffs, investment costs for charge points and battery and the ERE savings. Based on these costs, the yearly savings and payback time are determined.

## Prerequisites
You need the following installed on your local computer:
- Python 3.12.6 or newer.
- [Poetry](https://python-poetry.org/) 1.8 or newer.
  - It is recommended to use [pipx](https://github.com/pypa/pipx) to install poetry (`pipx install poetry`).
- [pre-commit](https://pre-commit.com)
  - It is recommended to use [pipx](https://github.com/pypa/pipx) to install pre-commit (`pipx install pre-commit`).

## Setting up pre-commit hooks

Set up the [pre-commit](./docs/toolchain/pre-commit.md) hooks by running `pre-commit install`.

The pre-commit hooks will automatically run the linters and formatters on the staged files when you commit. You can also install the pre-commit hooks in your IDE to run on file save. For this, we use the following extensions in VSCode:
- Ruff (charliermarsh.ruff)
- MyPy Type Checker (ms-python.mypy-type-checker)

## Installing local dependencies

Run `poetry install`. Poetry will create a new virtual environment and install all dependencies.

> If you use any sort of editor/tool that requires to 'see' your virtual environment, it is recommended to run
> `poetry config virtualenvs.in-project true` before running `poetry install`. This will create the virtual environment
> in the `.venv` directory in your project.
>
> You can also manually create a virtual environment before invoking `poetry install` and poetry will use it.

To enter the virtual environment in a new shell, run `poetry shell`. You can also run a single command using `poetry run <command>`.

## Running the application
To run the application locally, run `poetry run python -m src.app`. The application will be available at `http://localhost:8000`.

## Debugging

After setting up a local environment as above and selecting it with the VSCode python extension, you can use the VSCode Launch Configuration 'Python: Configured Debug' to launch the application locally and debug it.

### Docker

The application can also be Dockerized to better test the application as in the production environment.
To build the container use the following command:
```bash
docker build -t <NAME> .
```

Then to run the container use:
```Bash
docker run -p 8000:8000 <NAME>
```

## Getting started
We have developed an example notebook [`src/example_notebook.ipynb`](./src/example_notebook.ipynb) that takes you through all the modules in the order as they were designed to be used.

## Documentation
Documentation of the project is placed in the [`docs/`](./docs/) folder of the repository.

### Architecture
Information related to the architecture of the EnergyPod Calculator API can be found in the [`docs/architecture`](./docs/architecture/) folder of this repository. This folder contains a detailed description of the overall structure of the API and also how to use each component separately. To test the functionalities of the API, we have developed an example notebook ([`src/example_notebook.ipynb`](./src/example_notebook.ipynb)) that takes you through the steps of the EnergyPod Calculator and how it is designed to be used as a whole. Each of the components and endpoints can also be used on their own. Feel free to test and adjust the code to fit your specific use case.

### Optimization
An optimization problem is defined that serves as the foundation for calculations of energy consumption with an EnergyPod. This optimization problem can be used to calculate the energy usage for a given input configuration for a whole year. The mathematical formulation of the optimization problem that is used to calculate the scenario with EnergyPod can be found in the [`docs/model`](./docs/model/) folder of this repository.

### Toolchain
Information related to the toolchain of the EnergyPod Calculator can be found in the [`docs/toolchain`](./docs/toolchain/) folder of this repository.


## External Data Sources

There are several external data sources that have been used to support the calculations in this tool. These external data sources are explained below.

### ENTSO-E
ENTSO-E is a platform that provides the energy prices as per the day-ahead market. These energy prices are used within the EnergyPod Calculator to determine the costs for energy usage by the chargepoints and the battery in both scenario's with and without EnergyPod. For reference, please visit the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/).

### Baseload profile
Each company has a baseload profile, which is the base electricity consumption that is needed to perform all basic functionalities. Thus, this does not include energy usage for the charging of vehicles. To determine the baseload profile for your company, you can provide the tool with a csv-file containing the baseload profile of your company. This file should follow formatting as used in these files for [standard electricity profiles](https://energiedatawijzer.nl/onderwerpen/profielen/standaardprofielen/).

If you do not have the baseload profile of your company in a csv-file, the tool also provides an option to choose a predefined business category. For each business category, we use a normalized average baseload profile as provided by Liander. For more information on these standard SBI profiles, please visit [Verbruiksprofielen grootverbruikaansluitingen elektriciteit](https://www.liander.nl/over-ons/open-data#verbruiksprofielen-gv-elektriciteit).

### Grid tariffs
Additional to the energy prices, we consider the grid tariffs. The prices for the grid tariffs are obtained from: Liander, Stedin, Enexis, Coteq, Rendo and Westland. For more information on the grid tariffs and the reference sources, please visit the following sources:
- Liander: [large consumer](https://www.liander.nl/grootzakelijk/tarieven#tarieven-2025), [small consumer](https://www.liander.nl/tarieven)
- Stedin: [large consumer](https://www.stedin.net/zakelijk/betalingen-en-facturen/tarieven), [small consumer](https://www.stedin.net/tarieven/download-tarieven)
- Enexis: [large consumer](https://www.enexis.nl/zakelijk/aansluitingen/tarieven/tariefbladen), [small consumer](https://www.enexis.nl/tarieven/2026-elektriciteit-maandelijks)
- Coteq: [large consumer and small consumer](https://coteqnetbeheer.nl/actuele-tarieven)
- Rendo: [large consumer and small consumer](https://www.rendonetwerken.nl/zakelijk/tarieven-facturen/)
- Westland Infra: [large consumer](https://westlandinfra.nl/grootzakelijk/tarieven/bekijk-de-huidige-tarieven/), [small consumer](https://westlandinfra.nl/thuis-kleinzakelijk/tarieven/bekijk-de-huidige-tarieven/).

## Assumptions
Commonly used parameters throughout the EnergyPod Calculator API have been bundled in [`src/config.py`](./src/config.py). These parameters have been given default values, but feel free to adjust these parameters to fit your specific use case. Examples of commonly used parameters that you can adjust are:
- **Battery step size**: The battery energy capacity can be determined by the optimization. The optimization considers deterministic values for the battery energy capacity that are defined by: `step` * `battery_step_size`, where `step` can range from $0$ to `max_battery_steps`. Therefore, the lowest value for the battery energy capacity that is considered is equal to the battery step size.
- **Maximum number of battery steps**: The maximum value for the battery energy capacity that is considered is equal to `max_battery_steps` * `battery_step_size`.
- **Battery price per kWh**: The investment costs for the battery energy capacity are determined by multiplying `battery_price_per_kwh` by the battery energy capacity. The price per kWh is given in euros.
- **Charge point price per kW**: The investment costs for the charge point are determined by multiplying the `cp_price_per_kW` with the number of charge points and the power of a single charge point. The power of a single charge point can be provided via the configured input. The price per kW is given in euros.
- **Battery power loss for charging**: The battery power loss for charging is a factor that takes into account the loss of power when a battery is used for charging. This factor is battery specific and can be adjusted if the battery specifications are known. The factor is a number between 0 and 1, where 0 means that there is no loss of power and 1 means that all power is lost.
- **Battery power loss for discharging**: The battery power loss for discharging is a factor that takes into account the loss of power when a battery is used for discharging. This factor is battery specific and can be adjusted if the battery specifications are known. The factor is a number between 0 and 1, where 0 means that there is no loss of power and 1 means that all power is lost.

## Testing
Integration and unit tests for the modules in [`src/application`](./src/application/) can be found in [`tests/`](./tests/) folder. All tests need to have passed before committing any new code.
