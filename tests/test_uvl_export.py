import cfmtoolbox.plugins.uvl_export as uvl_export_plugin
from cfmtoolbox.plugins.uvl_export import export_uvl
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_export_plugin in app.load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert export_uvl() is None
