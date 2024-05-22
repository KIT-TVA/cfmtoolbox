import cfmtoolbox.plugins.random_sampling as random_sampling_plugin
from cfmtoolbox.plugins.random_sampling import random_sampling
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert random_sampling_plugin in app.load_plugins()


def test_random_sampling():
    assert random_sampling() is None
