from cfmtoolbox_uvl_import import UVLImportPlugin

from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    plugins = load_plugins()
    assert plugins
    assert any(issubclass(plugin, UVLImportPlugin) for plugin in plugins.values())


def test_plugin_does_only_handle_uvl_format():
    plugin = UVLImportPlugin()
    assert plugin.load("not-uvl", b"") is None
    assert plugin.load("uvl", b"") is not None
