from importlib.metadata import entry_points

plugin_entry_points = entry_points(group="cfmtoolbox.plugins")
plugins = {ep.name: ep.load() for ep in plugin_entry_points}

print("Hello, cfmtoolbox!")
print("Discovered plugins:", plugin_entry_points)
print("Loaded plugins:", plugins)
