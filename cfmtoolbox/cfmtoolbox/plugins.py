from importlib.metadata import entry_points
from types import ModuleType


def load_plugins() -> list[ModuleType]:
    plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
    return [ep.load() for ep in plugin_entry_points]
