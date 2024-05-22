import cfmtoolbox.plugins.uvl_import as uvl_import_plugin
from cfmtoolbox.plugins.uvl_import import import_uvl
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert uvl_import_plugin in app.load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert import_uvl() is None
