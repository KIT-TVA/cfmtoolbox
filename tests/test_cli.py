import shutil
import subprocess

import pytest
from typer.testing import CliRunner

from cfmtoolbox import app

runner = CliRunner(mix_stderr=False)


def test_cli_aborts_when_commands_are_invoked_without_import_option():
    result = runner.invoke(app.typer, ["convert"])
    assert result.exit_code == 1
    assert result.stderr == "Please provide a model via the --import option.\n"
    assert not result.stdout


@pytest.mark.skipif(shutil.which("poetry") is None, reason="poetry command required")
def test_cli_invokation_from_shell():
    proc = subprocess.run(
        ["poetry", "run", "cfmtoolbox", "--help"], capture_output=True
    )
    assert proc.returncode == 0
    assert not proc.stderr
    assert "cfmtoolbox [OPTIONS] COMMAND [ARGS]" in proc.stdout.decode()
