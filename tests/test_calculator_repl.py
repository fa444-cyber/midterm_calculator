"""Tests for the command-line REPL."""

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import build_commands, help_text, repl


@pytest.fixture
def calculator(tmp_path):
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def run_repl(monkeypatch, capsys, lines, calculator=None):
    """Feed the REPL a list of typed lines and return everything it printed."""
    typed = iter(lines)
    monkeypatch.setattr("builtins.input", lambda _: next(typed))
    repl(calculator)
    return capsys.readouterr().out


@pytest.mark.parametrize("word", [
    "add", "subtract", "multiply", "divide", "power", "root",
    "help", "history", "clear", "undo", "redo", "save", "load", "exit",
])
def test_help_text_mentions_every_operation_and_command(word):
    assert word in help_text()


def test_build_commands_covers_every_special_command(calculator):
    assert sorted(build_commands(calculator)) == [
        "clear", "help", "history", "load", "redo", "save", "undo",
    ]


def test_welcome_and_goodbye(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["exit"], calculator)
    assert "Welcome to the Enhanced Calculator!" in out
    assert "Goodbye!" in out


def test_exit_ignores_case_and_spaces(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["  EXIT  "], calculator)
    assert "Goodbye!" in out


def test_repl_builds_its_own_calculator_when_none_is_given(
    monkeypatch, capsys, tmp_path
):
    monkeypatch.chdir(tmp_path)
    assert "Goodbye!" in run_repl(monkeypatch, capsys, ["exit"])


def test_help_command(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["help", "exit"], calculator)
    assert out.count("Usage:") == 2


@pytest.mark.parametrize("text, expected", [
    ("add 2 3", "Result: 5.0"),
    ("subtract 10 4", "Result: 6.0"),
    ("multiply 3 4", "Result: 12.0"),
    ("divide 10 4", "Result: 2.5"),
    ("power 2 3", "Result: 8.0"),
    ("root 27 3", "Result: 3.0"),
])
def test_calculations_print_their_result(
    monkeypatch, capsys, calculator, text, expected
):
    out = run_repl(monkeypatch, capsys, [text, "exit"], calculator)
    assert expected in out


@pytest.mark.parametrize("text, expected", [
    ("divide 1 0", "Error: Cannot divide by zero"),
    ("power 0 -1", "Error: Zero cannot be raised to a negative power"),
    ("root -4 2", "Error: Cannot take the root of a negative number"),
    ("modulo 1 2", "Error: Unknown operation: 'modulo'"),
    ("add 2", "Error: Use the format"),
    ("add x 3", "Error: 'x' is not a valid number"),
    ("", "Error: Use the format"),
])
def test_errors_are_reported_and_the_loop_keeps_running(
    monkeypatch, capsys, calculator, text, expected
):
    out = run_repl(monkeypatch, capsys, [text, "exit"], calculator)
    assert expected in out
    assert "Goodbye!" in out


def test_history_command_shows_calculations(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["add 2 3", "history", "exit"], calculator)
    assert "operation" in out


def test_history_command_when_empty(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["history", "exit"], calculator)
    assert "No calculations yet." in out


def test_clear_command(monkeypatch, capsys, calculator):
    lines = ["add 2 3", "clear", "history", "exit"]
    out = run_repl(monkeypatch, capsys, lines, calculator)
    assert "History cleared." in out
    assert "No calculations yet." in out


def test_undo_and_redo_commands(monkeypatch, capsys, calculator):
    lines = ["add 2 3", "undo", "history", "redo", "exit"]
    out = run_repl(monkeypatch, capsys, lines, calculator)
    assert "Undone." in out
    assert "No calculations yet." in out
    assert "Redone." in out
    assert len(calculator.history) == 1


@pytest.mark.parametrize("command, expected", [
    ("undo", "Error: Nothing to undo"),
    ("redo", "Error: Nothing to redo"),
])
def test_undo_and_redo_with_nothing_to_do(
    monkeypatch, capsys, calculator, command, expected
):
    out = run_repl(monkeypatch, capsys, [command, "exit"], calculator)
    assert expected in out


def test_save_command(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["add 2 3", "save", "exit"], calculator)
    assert "History saved." in out


def test_load_command(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["add 2 3", "load", "exit"], calculator)
    assert "History loaded." in out


def test_load_command_without_a_saved_file(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["load", "exit"], calculator)
    assert "Error: History file not found" in out


def test_startup_warning_is_shown(monkeypatch, capsys, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    config.history_dir.mkdir(parents=True)
    config.history_file.write_text("")
    out = run_repl(monkeypatch, capsys, ["exit"], Calculator(config))
    assert "Warning: Could not read history file" in out