# CFM Toolsuite

A plugin-based toolbox for working with cardinality-based feature models.
This repository contains the `cfmtoolbox` itself and a few first party plugins demonstrating how to extend the toolbox.

## Development

In order to develop the `cfmtoolbox` and its plugins, you need to set up a Python virtual environment.
Within the virtual environment, [Poetry](https://python-poetry.org/) is used to manage dependencies, metadata and for building.

In the following, we assume that you do not have installed Poetry globally.
If you do, you can run Poetry commands without the `python3 -m` prefix.

### One time setup

Set up a virtual environment and install Poetry:

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install poetry`

Install the formatter and linter and set up the pre-commit hooks:

1. `python3 -m poetry install`
2. `python3 -m poetry run pre-commit install`

Install the cfmtoolbox and its plugins in editable mode:

1. `python3 -m poetry -C cfmtoolbox install`
2. `python3 -m poetry -C cfmtoolbox-random-sampling install`
3. `python3 -m poetry -C cfmtoolbox-uvl-export install`
4. `python3 -m poetry -C cfmtoolbox-uvl-import install`

### Running the cfmtoolbox

1. `source .venv/bin/activate`
2. `python3 -m poetry -C cfmtoolbox install`
3. `python3 -m cfmtoolbox`

### Formatting and linting

1. `source .venv/bin/activate`
2. `python3 -m poetry run ruff format .`
3. `python3 -m poetry run ruff check .`
4. `python3 -m poetry run mypy .`

### Adding dependencies

Run the following commands to add the dependency `<dependency>` to the package `<package>`.

1. `source .venv/bin/activate`
2. `python3 -m poetry -C <package> add <dependency>`
