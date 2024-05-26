import pytest

import cfmtoolbox.plugins.uvl_import as uvl_import_plugin
from cfmtoolbox import CFM
from cfmtoolbox.plugins.uvl_import import import_uvl
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_import_plugin in app.load_plugins()


def test_import_uvl(capsys: pytest.CaptureFixture[str]):
    cfm = import_uvl(b"")
    assert isinstance(cfm, CFM)

    captured = capsys.readouterr()
    assert captured.out == "Importing UVL\n"
