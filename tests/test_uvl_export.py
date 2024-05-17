from cfmtoolbox_uvl_export import UVLExportPlugin

from cfmtoolbox.models import CFM
from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    plugins = load_plugins()
    assert plugins
    assert any(issubclass(plugin, UVLExportPlugin) for plugin in plugins.values())


def test_plugin_does_only_handle_uvl_format():
    plugin = UVLExportPlugin()
    assert plugin.dump("not-uvl", CFM()) is None
    assert plugin.dump("uvl", CFM()) is not None
