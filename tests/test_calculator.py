"""Tests for the Calculator facade."""

import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import CalculatorError, OperationError, ValidationError
from app.history import History, Observer


class RecordingObserver(Observer):
    """A test observer that remembers every calculation it is told about."""

    def __init__(self):
        self.calls = []

    def update(self, calculation):
        self.calls.append(str(calculation))


@pytest.fixture
def config(tmp_path):
    return CalculatorConfig(base_dir=tmp_path)


@pytest.fixture
def calculator(config):
    return Calculator(config)


@pytest.fixture
def manual_calculator(tmp_path, monkeypatch):
    """A calculator with auto-save turned off."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "false")
    return Calculator(CalculatorConfig(base_dir=tmp_path))


def test_default_config_is_used_when_none_is_given(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert Calculator().config.base_dir.resolve() == tmp_path.resolve()


def test_new_calculator_starts_empty(calculator):
    assert len(calculator.history) == 0
    assert calculator.startup_warning is None
    assert calculator.caretaker.can_undo is False


def test_calculate_returns_and_records_the_calculation(calculator):
    calculation = calculator.calculate("add", 2, 3)
    assert isinstance(calculation, Calculation)
    assert calculation.result == 5
    assert len(calculator.history) == 1


def test_calculate_rounds_to_the_configured_precision(calculator):
    assert calculator.calculate("divide", 1, 3).result == 0.3333


@pytest.mark.parametrize("text, expected", [
    ("add 2 3", 5.0),
    ("subtract 10 4", 6.0),
    ("multiply 3 4", 12.0),
    ("divide 10 4", 2.5),
    ("power 2 3", 8.0),
    ("root 27 3", 3.0),
])
def test_calculate_from_text(calculator, text, expected):
    assert calculator.calculate_from_text(text).result == pytest.approx(expected)


@pytest.mark.parametrize("text, error", [
    ("add 2", ValidationError),
    ("add x 3", ValidationError),
    ("add 2 999999999", ValidationError),
    ("modulo 2 3", OperationError),
    ("divide 1 0", OperationError),
])
def test_failed_calculations_change_nothing(calculator, text, error):
    with pytest.raises(error):
        calculator.calculate_from_text(text)
    assert len(calculator.history) == 0
    assert calculator.caretaker.can_undo is False


def test_observers_are_notified_of_every_calculation(calculator):
    observer = RecordingObserver()
    calculator.attach(observer)
    calculator.calculate("add", 2, 3)
    calculator.calculate("multiply", 2, 4)
    assert observer.calls == ["add(2, 3) = 5", "multiply(2, 4) = 8"]


def test_auto_save_writes_the_history_file(calculator, config):
    calculator.calculate("add", 2, 3)
    assert config.history_file.exists()


def test_auto_save_can_be_turned_off(manual_calculator):
    manual_calculator.calculate("add", 2, 3)
    assert not manual_calculator.config.history_file.exists()


def test_existing_history_is_loaded_on_startup(config):
    saved = History()
    saved.add(Calculation("add", 1, 1))
    saved.add(Calculation("add", 2, 2))
    saved.save(config.history_file)
    assert len(Calculator(config).history) == 2


def test_a_corrupted_history_file_gives_a_warning_not_a_crash(config):
    config.history_dir.mkdir(parents=True)
    config.history_file.write_text("")
    calculator = Calculator(config)
    assert "Could not read history file" in calculator.startup_warning
    assert len(calculator.history) == 0


def test_undo_and_redo_step_through_the_history(calculator):
    calculator.calculate("add", 1, 1)
    calculator.calculate("add", 2, 2)
    calculator.undo()
    assert len(calculator.history) == 1
    calculator.redo()
    assert len(calculator.history) == 2


def test_undo_with_nothing_to_undo_raises(calculator):
    with pytest.raises(CalculatorError, match="Nothing to undo"):
        calculator.undo()


def test_redo_with_nothing_to_redo_raises(calculator):
    with pytest.raises(CalculatorError, match="Nothing to redo"):
        calculator.redo()


def test_clear_history_can_be_undone(calculator):
    calculator.calculate("add", 1, 1)
    calculator.clear_history()
    assert len(calculator.history) == 0
    calculator.undo()
    assert len(calculator.history) == 1


def test_save_history_writes_the_file(manual_calculator):
    manual_calculator.calculate("add", 2, 3)
    assert not manual_calculator.config.history_file.exists()
    manual_calculator.save_history()
    assert manual_calculator.config.history_file.exists()


def test_load_history_replaces_the_history_and_can_be_undone(manual_calculator):
    manual_calculator.calculate("add", 1, 1)
    manual_calculator.save_history()
    manual_calculator.calculate("add", 2, 2)
    assert len(manual_calculator.history) == 2
    manual_calculator.load_history()
    assert len(manual_calculator.history) == 1
    manual_calculator.undo()
    assert len(manual_calculator.history) == 2


def test_load_history_without_a_file_raises_and_changes_nothing(manual_calculator):
    with pytest.raises(CalculatorError, match="not found"):
        manual_calculator.load_history()
    assert manual_calculator.caretaker.can_undo is False