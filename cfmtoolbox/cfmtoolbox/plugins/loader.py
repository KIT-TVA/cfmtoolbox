from importlib.metadata import entry_points

from cfmtoolbox.plugins import BasePlugin


def load_plugins() -> dict[str, type[BasePlugin]]:
    plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
    return {ep.name: ep.load() for ep in plugin_entry_points}
