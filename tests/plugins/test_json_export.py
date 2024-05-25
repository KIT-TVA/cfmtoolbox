import json
from pathlib import Path

import pytest

import cfmtoolbox.plugins.json_export as json_export_plugin
from cfmtoolbox import CFM
from cfmtoolbox.plugins.json_export import export_json
from cfmtoolbox.toolbox import CFMToolbox


def test_plugin_can_be_loaded():
    app = CFMToolbox()
    assert json_export_plugin in app.load_plugins()


def test_json_export_requires_model(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cfmtoolbox.app.output_path", "output.json")
    assert export_json() is None


def test_json_export_requires_output_path(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("cfmtoolbox.app.model", CFM([], [], []))
    assert export_json() is None


def test_json_export(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    output_path = tmp_path / "output.json"
    cfm = CFM([], [], [])

    monkeypatch.setattr("cfmtoolbox.app.output_path", output_path)
    monkeypatch.setattr("cfmtoolbox.app.model", cfm)

    export_json()

    assert output_path.exists()
    assert output_path.read_text() == json.dumps(
        {"features": [], "require_constraints": [], "exclude_constraints": []}
    )
