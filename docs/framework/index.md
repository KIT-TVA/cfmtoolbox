The CFM Toolbox is a plugin-based framework for working with cardinality-based feature models and consists of three main components:

- Shared **models** for representing feature models
- A **plugin system** for extending the toolbox with new functionality
- A **command-line interface** for interacting with the toolbox

All three components are glued together by the `CFMToolbox` class, which is instantiated when the `cfmtoolbox` Python module is run as a script (i.e., its `__main__.py` file is run via `python3 -m cfmtoolbox`).

## Models

The core models included in the toolbox are shared between the framework, core plugins, and third-party plugins.
Since they are used to exchange data between first-party and third-party code, they are meant to be kept stable.

!!! warning
    Introducing breaking changes to the models will break plugins, so keep their interfaces lean.

The toolbox's models live in the `cfmtoolbox.models` module and are mostly implemented as Python dataclasses.
Take a look at the [models documentation](models.md) to learn more about the available models, their fields, and methods.

## Plugin system

The toolbox's plugin system discovers plugins based on [Python package metadata](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-package-metadata) and the [Entry points specification](https://packaging.python.org/specifications/entry-points/).
This allows us to discover and load core plugins and third-party plugins installed in the same environment as the toolbox in the same way.

Plugins can be used to extend the toolbox with new functionality.
This can be done by using Python decorators provided by the toolbox.
The following decorators can be used to register new functionality with the toolbox:

### Importers

The `importer` decorator is used to register new importers with the toolbox.
Importers are used to import feature models from different formats into the toolbox's internal representation.

Generally, importers handle exactly one file format, receive a file's contents as bytes, and return a CFM model instance.
The framework chooses the importer to use based on the file extension of the file being imported.
For example, the signature of on `.uvl` file importer would look like this:

```python
@app.importer(".uvl")
def import_uvl(file_contents: bytes) -> CFM: ...
```

To learn more please refer to the [writing plugins](writing-plugins.md#importers) guide.

### Commands

The `command` decorator is used to register new commands with the toolbox.
A command can be used to process feature models which have been imported into the toolbox.

Generally, commands receive a CFM model instance, process the instance, and return the processed instance.
Returning the processed instance enables users to export the processed instance and chain commands via shell scripting.
The name of commands is derived from the function name.
For example, the following signature would register a command named `my-command`:

```python
@app.command()
def my_command(cfm: CFM) -> CFM: ...
```

Note that commands can also take additional arguments, which can be passed to the command via the toolbox's command-line interface.
Extra arguments must use Python type hints to be automatically picked up by the framework.
Here is an example signature of a command that takes an optional integer argument with a default value of `10`:

```python
@app.command()
def my_command(cfm: CFM, my_argument: int = 10) -> CFM: ...
```

To learn more please refer to the [writing plugins](writing-plugins.md#commands) guide.

### Exporters

The `exporter` decorator is used to register new exporters with the toolbox.
Exporters are used to export feature models from the toolbox's internal representation to different formats.

Generally, exporters handle exactly one file format, receive a CFM model instance and return the model's contents as bytes.
The framework chooses the exporter to use based on the file extension of the file being exported.
For example, the signature of on `.uvl` file exporter would look like this:

```python
@app.exporter(".uvl")
def export_uvl(cfm: CFM) -> bytes: ...
```

To learn more please refer to the [writing plugins](writing-plugins.md#exporters) guide.

## Command Line Interface

The toolbox's CLI can be used to import models into the toolbox, process them with commands, and export them.
All commands of the toolbox are implemented via the plugin system.

The CLI itself is powered by [typer](https://github.com/fastapi/typer), a powerful and type-safe CLI library.
One key feature of `typer` is, that it can automatically generate a CLI based on Python type hints.
This is precicesly how the `@app.command()` decorator works under the hood.
Furthermore, this allows CFM Toolbox commands to make use of all `typer` features, such as descriptions for commands and arguments, autocompletion, and more.
