from cfmtoolbox.plugins import load_plugins


def test_load_plugins():
    plugins = load_plugins()
    assert len(plugins) == 3
