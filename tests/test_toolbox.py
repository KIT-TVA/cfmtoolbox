from pathlib import Path

import pytest
import typer

from cfmtoolbox import CFM
from cfmtoolbox.toolbox import CFMToolbox


def test_import_model_without_input_path():
    app = CFMToolbox()
    assert app.input_path is None

    app.import_model()
    assert app.model is None


def test_import_model_without_matching_importer(tmp_path: Path):
    app = CFMToolbox()
    app.input_path = tmp_path / "test.txt"
    app.input_path.touch()

    with pytest.raises(typer.Abort):
        app.import_model()

    assert app.model is None


def test_import_model_with_matching_importer(tmp_path: Path):
    app = CFMToolbox()
    app.input_path = tmp_path / "test.uvl"
    app.input_path.touch()

    cfm = CFM([], [], [])
    assert app.model is not cfm

    @app.importer(".uvl")
    def import_uvl(data: bytes):
        return cfm

    app.import_model()
    assert app.model is cfm


def test_export_model_without_output_path():
    app = CFMToolbox()
    assert app.output_path is None

    app.export_model()


def test_export_model_without_matching_exporter(tmp_path: Path):
    app = CFMToolbox()
    app.model = CFM([], [], [])
    app.output_path = tmp_path / "test.txt"

    with pytest.raises(typer.Abort):
        app.export_model()


def test_export_model_with_matching_exporter(tmp_path: Path):
    app = CFMToolbox()
    app.model = CFM([], [], [])
    app.output_path = tmp_path / "test.uvl"

    @app.exporter(".uvl")
    def export_uvl(cfm: CFM):
        return "hello".encode()

    app.export_model()
    assert app.output_path.read_text() == "hello"


def test_importer_registration():
    app = CFMToolbox()

    @app.importer(".uvl")
    def import_uvl(data: bytes):
        return CFM([], [], [])

    assert len(app.registered_importers) == 1
    assert app.registered_importers[".uvl"] == import_uvl


def test_exporter_registration():
    app = CFMToolbox()

    @app.exporter(".uvl")
    def export_uvl(cfm: CFM):
        return b""

    assert len(app.registered_exporters) == 1
    assert app.registered_exporters[".uvl"] == export_uvl


def test_load_plugins():
    app = CFMToolbox()
    plugins = app.load_plugins()
    assert len(plugins) == 5
