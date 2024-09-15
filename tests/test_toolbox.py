import inspect

import pytest
import typer

from cfmtoolbox import CFM, Cardinality, CFMToolbox, Feature


@pytest.fixture
def root_feature():
    return Feature(
        name="root",
        instance_cardinality=Cardinality([]),
        group_type_cardinality=Cardinality([]),
        group_instance_cardinality=Cardinality([]),
        parent=None,
        children=[],
    )


def test_import_model_does_nothing_without_import_path():
    app = CFMToolbox()
    assert app.import_path is None
    assert app.import_model() is None


def test_import_model_reports_unsupported_formats(tmp_path):
    import_path = tmp_path / "test.txt"
    import_path.touch()

    app = CFMToolbox()
    app.import_path = import_path

    with pytest.raises(typer.Abort, match="Unsupported import format"):
        app.import_model()


def test_import_model_returns_cfm_of_supported_format(root_feature, tmp_path):
    cfm = CFM(root_feature, [])
    import_path = tmp_path / "test.uvl"
    import_path.touch()

    app = CFMToolbox()
    app.import_path = import_path

    @app.importer(".uvl")
    def import_uvl(data: bytes):
        return cfm

    assert app.import_model() is cfm


def test_export_model_does_nothing_without_export_path(root_feature):
    cfm = CFM(root_feature, [])

    app = CFMToolbox()
    assert app.export_path is None

    app.export_model(cfm)


def test_export_model_reports_unsupported_formats(root_feature, tmp_path):
    cfm = CFM(root_feature, [])
    export_path = tmp_path / "test.txt"

    app = CFMToolbox()
    app.export_path = export_path

    with pytest.raises(typer.Abort, match="Unsupported export format"):
        app.export_model(cfm)

    assert not export_path.exists()


def test_export_model_stores_exported_model_in_supported_format(root_feature, tmp_path):
    cfm = CFM(root_feature, [])
    export_path = tmp_path / "test.uvl"

    app = CFMToolbox()
    app.export_path = export_path

    @app.exporter(".uvl")
    def export_uvl(cfm: CFM):
        return "hello".encode()

    app.export_model(cfm)
    assert export_path.read_text() == "hello"


def test_importer_registers_the_decorated_importer(root_feature):
    app = CFMToolbox()

    @app.importer(".uvl")
    def import_uvl(data: bytes):
        return CFM(root_feature, [])

    assert len(app.registered_importers) == 1
    assert app.registered_importers[".uvl"] == import_uvl


def test_exporter_registers_the_decorated_exporter():
    app = CFMToolbox()

    @app.exporter(".uvl")
    def export_uvl(cfm: CFM):
        return b""

    assert len(app.registered_exporters) == 1
    assert app.registered_exporters[".uvl"] == export_uvl


def test_command_registers_the_decorated_command():
    app = CFMToolbox()
    assert len(app.typer.registered_commands) == 0

    @app.command()
    def make_sandwich(cfm: CFM) -> CFM:
        return cfm

    assert len(app.typer.registered_commands) == 1

    command = app.typer.registered_commands[0]
    assert getattr(command.callback, "__name__") == "make_sandwich"


def test_command_prevent_typer_from_including_the_cfm_argument_in_the_cli():
    app = CFMToolbox()

    @app.command()
    def make_sandwich(cfm: CFM) -> CFM:
        return cfm

    command = app.typer.registered_commands[0]
    callback = command.callback
    assert callback is not None
    assert "cfm" not in inspect.signature(callback).parameters


def test_load_plugins_loads_all_core_plugins():
    app = CFMToolbox()
    plugins = app.load_plugins()
    assert len(plugins) == 10
