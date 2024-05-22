import cfmtoolbox_uvl_export
from cfmtoolbox_uvl_export import export_uvl

from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert cfmtoolbox_uvl_export in app.load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert export_uvl() is None
