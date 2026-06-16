# Contributing to EnergyPod Calculator

Welcome to the EnergyPod Calculator project! We appreciate your interest in contributing to this open-source initiative. Whether you're fixing bugs, improving documentation, or adding new features, your contributions are valuable and will help us continue to develop high-quality software.

## Reporting Bugs and Requesting Features

If you encounter a bug or have an idea for a new feature, please follow these steps:

1. Check if the issue has already been reported by searching the [issue tracker](https://github.com/Infiniot/energy-pod-calculator/issues).

2. If the issue is not already reported, create a new issue in the project's issue tracker. Be sure to provide detailed information about the problem or suggestion.

## Contributing Code

Contributions to this project are welcome! To contribute code, follow these steps:
1. Clone the repository and create the virtual environment

    ```bash
    git clone https://github.com/Infiniot/energy-pod-calculator.git
    cd energy-pod-calculator
    poetry install
    ```

2. Choose a meaningful branch name that describes your changes (e.g., `bug/###` or `feature/###`).

3. Create a new branch for your changes based on the chosen branch name.

    ```bash
    git checkout -b bug/###
    ```

4. Make your changes and add tests to ensure they work as expected.

    ```bash
    poetry run python -m pytest
    ```

5. Perform the linting step.

    ```bash
    poetry run pre-commit run --all-files
    ```

5. Submit a pull request to the main branch of the repository.

6. A member of the project team will review your pull request and provide feedback or merge it into the main codebase.

By following these steps, you can help make the EnergyPod Calculator even better!


## Pull Request Guidelines

To safeguard the quality and maintainability of our codebase, please adhere to the following guidelines when submitting a pull request:

- Link the related issue (e.g., `Closes #123`)
- Clearly describe your changes
- Keep PRs small and focused
