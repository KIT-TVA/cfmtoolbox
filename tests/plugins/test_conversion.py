import json

from typer.testing import CliRunner

from cfmtoolbox import app

runner = CliRunner()


def test_convert_command(tmp_path):
    input_path = "tests/data/sandwich.uvl"
    output_path = tmp_path / "sandwich.json"

    result = runner.invoke(
        app.typer, ["--import", input_path, "--export", str(output_path), "convert"]
    )
    assert result.exit_code == 0
    assert result.stdout == "Converting CFM...\n"
    assert output_path.exists()

    output_data = json.loads(output_path.read_text())
    assert isinstance(output_data, dict)
    assert "root" in output_data
    assert "constraints" in output_data


def test_convert_command_is_generally_idempotent(tmp_path):
    original_path = "tests/data/sandwich.json"
    output_path1 = tmp_path / "sandwich-output1.json"
    output_path2 = tmp_path / "sandwich-output2.json"

    result = runner.invoke(
        app.typer, ["--import", original_path, "--export", str(output_path1), "convert"]
    )
    assert result.exit_code == 0
    assert output_path1.exists()

    result = runner.invoke(
        app.typer, ["--import", output_path1, "--export", str(output_path2), "convert"]
    )
    assert result.exit_code == 0
    assert output_path2.exists()

    assert output_path1.read_text() == output_path2.read_text()
