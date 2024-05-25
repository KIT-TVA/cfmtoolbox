from pathlib import Path

import pytest
import typer

from cfmtoolbox.toolbox import CFMToolbox


def test_load_model_without_input_path():
    app = CFMToolbox()
    assert app.input_path is None

    app.import_model()
    assert app.model is None


def test_load_model_without_matching_importer():
    app = CFMToolbox()
    app.input_path = Path("test.txt")

    with pytest.raises(typer.Abort):
        app.import_model()

    assert app.model is None


def test_load_model_with_matching_importer():
    app = CFMToolbox()
    app.input_path = Path("test.uvl")
    success = False

    @app.importer(".uvl")
    def import_uvl():
        nonlocal success
        success = True

    app.import_model()
    assert success


def test_dump_model_without_output_path():
    app = CFMToolbox()
    assert app.output_path is None

    app.export_model()


def test_dump_model_without_matching_exporter():
    app = CFMToolbox()
    app.output_path = Path("test.txt")

    with pytest.raises(typer.Abort):
        app.export_model()


def test_dump_model_with_matching_exporter():
    app = CFMToolbox()
    app.output_path = Path("test.uvl")
    success = False

    @app.exporter(".uvl")
    def export_uvl():
        nonlocal success
        success = True

    app.export_model()
    assert success


def test_registering_an_importer():
    app = CFMToolbox()

    @app.importer(".uvl")
    def import_uvl():
        pass

    assert len(app.registered_importers) == 1
    assert app.registered_importers[".uvl"] == import_uvl


def test_registering_an_exporter():
    app = CFMToolbox()

    @app.exporter(".uvl")
    def export_uvl():
        pass

    assert len(app.registered_exporters) == 1
    assert app.registered_exporters[".uvl"] == export_uvl


def test_load_plugins():
    app = CFMToolbox()
    plugins = app.load_plugins()
    assert len(plugins) == 5
