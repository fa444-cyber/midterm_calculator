"""Tests for the colors the REPL uses."""

import pytest
from colorama import Fore

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import repl
from app.colors import failure, heading, info, success


@pytest.fixture
def calculator(tmp_path):
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def run_repl(monkeypatch, capsys, lines, calculator):
    """Feed the REPL some typed lines and return everything it printed."""
    typed = iter(lines)
    monkeypatch.setattr("builtins.input", lambda _: next(typed))
    repl(calculator)
    return capsys.readouterr().out


def test_the_welcome_message_is_a_heading(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["exit"], calculator)
    assert heading("Welcome to the Enhanced Calculator!") in out


def test_results_are_green(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["add 2 3", "exit"], calculator)
    assert success("Result: 5.0") in out


def test_errors_are_red(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["divide 1 0", "exit"], calculator)
    assert failure("Error: Cannot divide by zero") in out


def test_confirmations_and_goodbye_are_cyan(monkeypatch, capsys, calculator):
    lines = ["add 2 3", "clear", "exit"]
    out = run_repl(monkeypatch, capsys, lines, calculator)
    assert info("History cleared.") in out
    assert info("Goodbye!") in out


def test_the_help_command_colors_its_headings(monkeypatch, capsys, calculator):
    out = run_repl(monkeypatch, capsys, ["help", "exit"], calculator)
    assert out.count(heading("Operations:")) == 2


def test_a_startup_warning_is_yellow(monkeypatch, capsys, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    config.history_dir.mkdir(parents=True)
    config.history_file.write_text("")
    out = run_repl(monkeypatch, capsys, ["exit"], Calculator(config))
    assert Fore.YELLOW + "Warning: Could not read history file" in out