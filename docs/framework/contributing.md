Below you'll find some useful commands to get started if you want to contribute to the framework itself.
Note that we use [poetry](https://python-poetry.org/) for project and dependency management.

## Project setup

1. Install [poetry](https://python-poetry.org/)
2. Install project dependencies by running `poetry install`

## Running the cfmtoolbox

After installing the project and its dependencies, you can run the development version of the CFM Toolbox using the following command: 

```bash
poetry run cfmtoolbox
```

## Formatting linting

We use `ruff` for code formatting and linting, and `mypy` for static type checking.

You can format your code by running

```bash
poetry run ruff format .
```

To check for linting errors, run the following command:

```bash
poetry run ruff check .
```

For static type checking, run the following command:

```bash
poetry run mypy .
```

To automatically check the formatting, linting, and static type checking on every commit, you can install the pre-commit hooks:

```bash
poetry run pre-commit install
```

## Testing

We use `pytest` for testing.
To run the tests, use the following command:

```
poetry run pytest
```

A test coverage report will automatically be generated, displayed in the terminal, and exported as an interactive HTML report in the `htmlcov` directory.

## Previewing the documentation

We use `mkdocs` to generate the documentation from markdown files and to deploy it to GitHub Pages.
While working on the documentation, you can preview it locally by running the following command:

```bash
poetry run mkdocs serve
```
