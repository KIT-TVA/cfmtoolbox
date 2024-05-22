# CFM Toolsuite

A plugin-based toolbox for working with cardinality-based feature models.
This repository contains the `cfmtoolbox` itself and a few first party plugins demonstrating how to extend the toolbox.

## Development

1. Install [poetry](https://python-poetry.org/)
2. `poetry install`
3. `poetry run pre-commit install`

### Running the cfmtoolbox

1. `poetry run cfmtoolbox`

### Formatting, linting and testing

1. `poetry run ruff format .`
2. `poetry run ruff check .`
3. `poetry run mypy .`
4. `poetry run pytest`
