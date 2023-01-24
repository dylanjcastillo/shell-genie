from typer.testing import CliRunner

from shell_genie.main import app

runner = CliRunner()


def test_init():
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "'os': 'MacOS'" in result.stdout


def test_ask():
    result = runner.invoke(app, ["ask", "'list files in the current directory'"])
    assert result.exit_code == 0
    assert result.stdout.split("\n")[0] == "Command: ls"
