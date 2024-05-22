import cfmtoolbox.plugins.cfmtoolbox_random_sampling as cfmtoolbox_random_sampling
from cfmtoolbox.plugins.cfmtoolbox_random_sampling import random_sampling
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert cfmtoolbox_random_sampling in app.load_plugins()


def test_random_sampling():
    assert random_sampling() is None
