"""Tests for the messages the REPL writes to the log."""

import logging

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import log_failure, repl
from app.exceptions import CalculatorError, OperationError, ValidationError


@pytest.fixture
def calculator(tmp_path):
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def run_and_collect(monkeypatch, caplog, lines, calculator):
    """Run the REPL on the given input and return the log records it produced."""
    typed = iter(lines)
    monkeypatch.setattr("builtins.input", lambda _: next(typed))
    with caplog.at_level(logging.INFO, logger="calculator"):
        repl(calculator)
    return caplog.records


def levels_and_messages(records):
    return [(record.levelname, record.getMessage()) for record in records]


def test_start_and_exit_are_logged(monkeypatch, caplog, calculator):
    records = run_and_collect(monkeypatch, caplog, ["exit"], calculator)
    assert levels_and_messages(records) == [
        ("INFO", "Calculator started"),
        ("INFO", "Calculator exited"),
    ]


def test_calculations_are_logged_as_info(monkeypatch, caplog, calculator):
    lines = ["modulus 10 3", "exit"]
    records = run_and_collect(monkeypatch, caplog, lines, calculator)
    expected = ("INFO", "Calculation performed: modulus(10.0, 3.0) = 1.0")
    assert expected in levels_and_messages(records)


def test_commands_are_logged(monkeypatch, caplog, calculator):
    records = run_and_collect(monkeypatch, caplog, ["history", "exit"], calculator)
    assert ("INFO", "Command executed: history") in levels_and_messages(records)


@pytest.mark.parametrize("text", ["add 2", "add x 3", "divide 1 0", "modulus 5 0"])
def test_rejected_input_is_logged_as_a_warning(
    monkeypatch, caplog, calculator, text
):
    records = run_and_collect(monkeypatch, caplog, [text, "exit"], calculator)
    warnings = [r for r in records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    assert f"Rejected input '{text}'" in warnings[0].getMessage()


def test_other_failures_are_logged_as_errors(monkeypatch, caplog, calculator):
    records = run_and_collect(monkeypatch, caplog, ["load", "exit"], calculator)
    errors = [r for r in records if r.levelname == "ERROR"]
    assert len(errors) == 1
    assert "Command 'load' failed" in errors[0].getMessage()


def test_a_startup_problem_is_logged_as_a_warning(monkeypatch, caplog, tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    config.history_dir.mkdir(parents=True)
    config.history_file.write_text("")
    records = run_and_collect(monkeypatch, caplog, ["exit"], Calculator(config))
    warnings = [r for r in records if r.levelname == "WARNING"]
    assert len(warnings) == 1
    assert "Startup problem" in warnings[0].getMessage()


@pytest.mark.parametrize("error_class, level", [
    (ValidationError, "WARNING"),
    (OperationError, "WARNING"),
    (CalculatorError, "ERROR"),
])
def test_log_failure_picks_the_level(caplog, error_class, level):
    with caplog.at_level(logging.INFO, logger="calculator"):
        log_failure("some input", error_class("boom"))
    assert [record.levelname for record in caplog.records] == [level]