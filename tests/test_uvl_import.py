import cfmtoolbox_uvl_import
from cfmtoolbox_uvl_import import import_uvl

from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    assert cfmtoolbox_uvl_import in load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert import_uvl() is None
