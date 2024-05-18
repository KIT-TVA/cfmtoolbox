import cfmtoolbox_random_sampling
from cfmtoolbox_random_sampling import random_sampling

from cfmtoolbox.plugins import load_plugins


def test_plugin_can_be_loaded():
    assert cfmtoolbox_random_sampling in load_plugins()


def test_random_sampling():
    assert random_sampling() is None
