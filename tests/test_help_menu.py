"""Tests for the decorator-based help menu."""

import pytest

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_repl import build_commands, help_text
from app.help_menu import (
    COMMAND_DESCRIPTIONS,
    BasicHelp,
    CommandsHelp,
    HelpDecorator,
    HelpMenu,
    OperationsHelp,
    build_help_menu,
)
from app.operations import Operation, OperationFactory


class Double(Operation):
    """A throwaway operation used to prove the menu updates by itself."""

    name = "double"
    description = "Double the first number"

    def execute(self, a, b):
        return a * 2


def test_help_menu_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        HelpMenu()


def test_basic_help_explains_the_usage():
    assert BasicHelp().render().startswith("Usage:")


def test_a_plain_decorator_passes_the_text_through():
    assert HelpDecorator(BasicHelp()).render() == BasicHelp().render()


def test_operations_help_adds_every_operation():
    text = OperationsHelp(BasicHelp()).render()
    assert text.startswith(BasicHelp().render())
    assert "Operations:" in text
    for name in OperationFactory.available_operations():
        assert name in text


def test_commands_help_adds_every_command():
    text = CommandsHelp(BasicHelp()).render()
    assert "Commands:" in text
    for name in COMMAND_DESCRIPTIONS:
        assert name in text


def test_commands_help_accepts_its_own_command_list():
    text = CommandsHelp(BasicHelp(), {"jump": "Jump around"}).render()
    assert "jump" in text
    assert "Jump around" in text
    assert "history" not in text


def test_the_decorators_stack_in_order():
    text = build_help_menu().render()
    assert text.index("Usage:") < text.index("Operations:") < text.index("Commands:")


@pytest.mark.parametrize("name, description", OperationFactory.describe_operations())
def test_every_operation_has_a_description(name, description):
    assert description.strip() != ""


def test_adding_an_operation_updates_the_menu_automatically(monkeypatch):
    assert "double" not in build_help_menu().render()
    monkeypatch.setitem(OperationFactory._operations, "double", Double)
    text = build_help_menu().render()
    assert "double" in text
    assert "Double the first number" in text


def test_the_menu_lists_every_real_command(tmp_path):
    calculator = Calculator(CalculatorConfig(base_dir=tmp_path))
    real_commands = set(build_commands(calculator)) | {"exit"}
    assert real_commands == set(COMMAND_DESCRIPTIONS)


def test_the_repl_help_text_uses_the_decorated_menu():
    assert help_text() == build_help_menu().render()