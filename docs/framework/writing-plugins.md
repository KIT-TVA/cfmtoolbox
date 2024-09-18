CFM Toolbox plugins are Python packages with entry point metadata, installed in the same environment as the toolbox, and discovered and loaded at runtime.
Each Python package can contain multiple plugins, which can be used to extend the toolbox with new functionality.

Generally, there are three types of plugins: **importers**, **commands**, and **exporters**.
We highly recommend using `python-poetry` to manage your plugin's dependencies and packaging.
Below you'll find guides on how to write each type of plugin using `python-poetry`.

## Importers

1. Start by running `poetry new cfmtoolbox-example-importer` to create a new Python project
2. Your importer's code will live in the `cfmtoolbox_example_importer` package
3. To create a minimal valid importer, add the following code to your `cfmtoolbox_example_importer/__init__.py` file:

    ```python
    from cfmtoolbox import app, CFM, Feature, Cardinality

    @app.importer(".example")
    def import_example(file_contents: bytes) -> CFM:
        # TODO: parse the `file_contents` and construct a real CFM

        return CFM(
            root=Feature(
                name="sandwich",
                instance_cardinality=Cardinality(intervals=[]),
                group_type_cardinality=Cardinality(intervals=[]),
                group_instance_cardinality=Cardinality(intervals=[]),
                parent=None,
                children=[]
            ),
            constraints=[],
        )
    ```

4. To enable the CFM Toolbox to discover and automatically load your plugin, add the following to your `pyproject.toml` file:

    ```toml
    [tool.poetry.plugins."cfmtoolbox.plugins"]
    example-importer = "cfmtoolbox_example_importer"
    ```

That's it!
As soon as you install your plugin in the same environment as the CFM Toolbox, it will be automatically discovered and loaded.
This plugin would allow the CFM Toolbox to import feature models from a `.example` file format.


## Commands

1. Start by running `poetry new cfmtoolbox-example-command` to create a new Python project
2. Your command's code will live in the `cfmtoolbox_example_command` package
3. To create a minimal valid command, add the following code to your `cfmtoolbox_example_command/__init__.py` file:

    ```python
    from cfmtoolbox import app, CFM

    @app.command()
    def example_command(cfm: CFM) -> CFM:
        print(f"Nice CFM! It even has {len(cfm.constraints)} constraints!")
        return cfm
    ```

4. To enable the CFM Toolbox to discover and automatically load your plugin, add the following to your `pyproject.toml` file:

    ```toml
    [tool.poetry.plugins."cfmtoolbox.plugins"]
    example-command = "cfmtoolbox_example_command"
    ```

That's it!
As soon as you install your plugin in the same environment as the CFM Toolbox, it will be automatically discovered and loaded.
This plugin would add a new `example-command` command to the CFM Toolbox, which would print the number of constraints in the CFM and return the CFM unchanged.


## Exporters

1. Start by running `poetry new cfmtoolbox-summary-exporter` to create a new Python project
2. Your exporter's code will live in the `cfmtoolbox_summary_exporter` package
3. To create a minimal valid exporter, add the following code to your `cfmtoolbox_summary_exporter/__init__.py` file:

    ```python
    from cfmtoolbox import app, CFM

    @app.exporter(".summary")
    def export_example(cfm: CFM) -> bytes:
        contents = f"This CFM has {len(cfm.features)} features"
        return contents.encode("utf-8")
    ```

4. To enable the CFM Toolbox to discover and automatically load your plugin, add the following to your `pyproject.toml` file:

    ```toml
    [tool.poetry.plugins."cfmtoolbox.plugins"]
    summary-exporter = "cfmtoolbox_summary_exporter"
    ```

That's it!
As soon as you install your plugin in the same environment as the CFM Toolbox, it will be automatically discovered and loaded.
This plugin would allow the CFM Toolbox to export feature models to a `.summary` file format, which would report the number of features in the CFM.
