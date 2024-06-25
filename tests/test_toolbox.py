from pathlib import Path

import pytest
import typer

from cfmtoolbox import CFM
from cfmtoolbox.toolbox import CFMToolbox


def test_import_model_without_import_path():
    app = CFMToolbox()
    assert app.import_path is None

    app.import_model()
    assert app.model is None


def test_import_model_without_matching_importer(tmp_path: Path):
    app = CFMToolbox()
    app.import_path = tmp_path / "test.txt"
    app.import_path.touch()

    with pytest.raises(typer.Abort, match="Unsupported import format"):
        app.import_model()

    assert app.model is None


def test_import_model_with_matching_importer(tmp_path: Path):
    app = CFMToolbox()
    app.import_path = tmp_path / "test.uvl"
    app.import_path.touch()

    cfm = CFM([], [], [])
    assert app.model is not cfm

    @app.importer(".uvl")
    def import_uvl(data: bytes):
        return cfm

    app.import_model()
    assert app.model is cfm


def test_export_model_without_export_path():
    app = CFMToolbox()
    assert app.export_path is None

    app.export_model()


def test_export_model_without_matching_exporter(tmp_path: Path):
    app = CFMToolbox()
    app.model = CFM([], [], [])
    app.export_path = tmp_path / "test.txt"

    with pytest.raises(typer.Abort, match="Unsupported export format"):
        app.export_model()


def test_export_model_with_matching_exporter(tmp_path: Path):
    app = CFMToolbox()
    app.model = CFM([], [], [])
    app.export_path = tmp_path / "test.uvl"

    @app.exporter(".uvl")
    def export_uvl(cfm: CFM):
        return "hello".encode()

    app.export_model()
    assert app.export_path.read_text() == "hello"


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
    assert len(plugins) == 6
