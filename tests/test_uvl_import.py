import cfmtoolbox.plugins.cfmtoolbox_uvl_import as cfmtoolbox_uvl_import
from cfmtoolbox.plugins.cfmtoolbox_uvl_import import import_uvl
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert cfmtoolbox_uvl_import in app.load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert import_uvl() is None
