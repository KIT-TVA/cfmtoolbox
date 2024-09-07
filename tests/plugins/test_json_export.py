import json

import cfmtoolbox.plugins.json_export as json_export_plugin
from cfmtoolbox import CFM
from cfmtoolbox.plugins.json_export import export_json
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert json_export_plugin in app.load_plugins()


def test_json_export():
    cfm = CFM([], [], [])
    output = export_json(cfm)

    assert output.decode() == json.dumps(
        {"features": [], "require_constraints": [], "exclude_constraints": []}, indent=2
    )
