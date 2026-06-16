# DITM EPBCC API
This repository contains the code for the API of the **E**nergy**P**od **B**usiness **C**ase **C**alculator.

## About the project
For a global overview of what the DITM EnergyPod Business Case Calculator does, please refer to the wiki page.

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

### .env file
The application uses environment variables for configuration. You can create a `.env` file in the root of the project to set these variables locally. Please ask one of your colleagues for the required environment variables and their values.

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

## Documentation
Documentation of the project is placed in the [`docs/`](./docs/) folder of the repository.

### Architecture
Information related to the architecture of the validation platform as a whole, as well as a deeper dive into this specific component can be found in the [`docs/architecture`](./docs/architecture/) folder of this repository.

### Toolchain
Information related to the toolchain of the EnergyPod Business Case Calculator can be found in the [`docs/toolchain`](./docs/toolchain/) folder of this repository.
