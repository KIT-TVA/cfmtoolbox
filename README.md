# CFM Toolbox

[![Versions][versions-image]][versions-url]
[![PyPI][pypi-image]][pypi-url]
[![License][license-image]][license-url]

[versions-image]: https://img.shields.io/pypi/pyversions/cfmtoolbox
[versions-url]: https://github.com/KIT-TVA/cfmtoolbox/blob/main/pyproject.toml
[pypi-image]: https://img.shields.io/pypi/v/cfmtoolbox
[pypi-url]: https://pypi.org/project/cfmtoolbox/
[license-image]: https://img.shields.io/pypi/l/cfmtoolbox
[license-url]: https://github.com/KIT-TVA/cfmtoolbox/blob/main/LICENSE

A plugin-based toolbox for working with cardinality-based feature models.
This repository contains the `cfmtoolbox` itself and a few first party plugins demonstrating how to extend the toolbox.

[Read the documentation](https://kit-tva.github.io/cfmtoolbox/) to learn more.

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

### Previewing the documentation

1. `poetry run mkdocs serve`
