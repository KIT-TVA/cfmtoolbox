from typer.testing import CliRunner

from cfmtoolbox import app

runner = CliRunner(mix_stderr=False)


def test_cli_aborts_when_commands_are_invoked_without_import_option():
    result = runner.invoke(app.typer, ["convert"])
    assert result.exit_code == 1
    assert result.stderr == "Please provide a model via the --import option.\n"
    assert not result.stdout
