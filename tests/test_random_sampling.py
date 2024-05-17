from cfmtoolbox_random_sampling import RandomSamplingPlugin

from cfmtoolbox.models import CFM
from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    plugins = load_plugins()
    assert plugins
    assert any(issubclass(plugin, RandomSamplingPlugin) for plugin in plugins.values())


def test_processing():
    plugin = RandomSamplingPlugin()
    assert isinstance(plugin.process(CFM()), CFM)
