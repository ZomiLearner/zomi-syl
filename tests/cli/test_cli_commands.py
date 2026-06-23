# tests/cli/test_cli_commands.py

import pytest
from click.testing import CliRunner
from zomi_syl.cli import main as cli_main


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


# --------------------------------------------------------------
# Basic CLI behavior
# --------------------------------------------------------------

def test_cli_help(runner):
    result = runner.invoke(cli_main, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "syllabify" in result.output
    assert "analyze" in result.output
    assert "models" in result.output
    assert "profiles" in result.output


# --------------------------------------------------------------
# syllabify command
# --------------------------------------------------------------

def test_cli_syllabify_rule(runner):
    result = runner.invoke(cli_main, ["syllabify", "itna", "--model", "rule"])
    assert result.exit_code == 0
    assert "it na" in result.output or "['it', 'na']" in result.output


def test_cli_syllabify_crf(runner):
    result = runner.invoke(cli_main, ["syllabify", "itna", "--model", "crf"])
    assert result.exit_code == 0
    assert "it na" in result.output or "['it', 'na']" in result.output


# --------------------------------------------------------------
# analyze command
# --------------------------------------------------------------

def test_cli_analyze(runner):
    result = runner.invoke(cli_main, ["analyze", "itna", "--model", "rule"])
    assert result.exit_code == 0
    assert "backend" in result.output
    assert "syllables" in result.output


# --------------------------------------------------------------
# models command
# --------------------------------------------------------------

def test_cli_models_list(runner):
    result = runner.invoke(cli_main, ["models", "list"])
    assert result.exit_code == 0
    assert "rule" in result.output
    assert "crf" in result.output


def test_cli_models_info(runner):
    result = runner.invoke(cli_main, ["models", "info", "rule"])
    assert result.exit_code == 0
    assert "backend_type" in result.output


# --------------------------------------------------------------
# profiles command
# --------------------------------------------------------------

def test_cli_profiles_list(runner):
    result = runner.invoke(cli_main, ["profiles", "list"])
    assert result.exit_code == 0
    assert "tedim" in result.output or "default" in result.output


def test_cli_profiles_info(runner):
    result = runner.invoke(cli_main, ["profiles", "info", "tedim"])
    assert result.exit_code == 0
    assert "dialect" in result.output or "profile" in result.output


# --------------------------------------------------------------
# Error handling
# --------------------------------------------------------------

def test_cli_unknown_command(runner):
    result = runner.invoke(cli_main, ["does-not-exist"])
    assert result.exit_code != 0
    assert "No such command" in result.output
