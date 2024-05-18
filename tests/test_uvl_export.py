import cfmtoolbox_uvl_export
from cfmtoolbox_uvl_export import export_uvl

from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    assert cfmtoolbox_uvl_export in load_plugins()


def test_plugin_does_only_handle_uvl_format():
    assert export_uvl() is None
