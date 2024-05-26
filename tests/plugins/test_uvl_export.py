import pytest

import cfmtoolbox.plugins.uvl_export as uvl_export_plugin
from cfmtoolbox import CFM
from cfmtoolbox.plugins.uvl_export import export_uvl
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_export_plugin in app.load_plugins()


def test_export_uvl(capsys: pytest.CaptureFixture[str]):
    data = export_uvl(CFM([], [], []))
    assert isinstance(data, bytes)

    captured = capsys.readouterr()
    assert captured.out == "Exporting UVL\n"
