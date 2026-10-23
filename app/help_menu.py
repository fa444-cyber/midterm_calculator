"""Dynamic help menu, built with the Decorator pattern."""

from abc import ABC, abstractmethod

from app.operations import OperationFactory

COMMAND_DESCRIPTIONS = {
    "help": "Show this help menu",
    "history": "Show every calculation so far",
    "clear": "Erase the history (this can be undone)",
    "undo": "Undo the last change",
    "redo": "Redo what was undone",
    "save": "Save the history to the CSV file",
    "load": "Load the history from the CSV file",
    "exit": "Leave the calculator",
}


class HelpMenu(ABC):
    """Component interface: anything that can produce help text."""

    @abstractmethod
    def render(self):
        """Return the help text."""
        pass  # pragma: no cover


class BasicHelp(HelpMenu):
    """The plain component: explains how to type a calculation."""

    def render(self):
        return "Usage: <operation> <number> <number>   (example: add 2 3)"


class HelpDecorator(HelpMenu):
    """Base decorator: wraps another help menu so subclasses can add to its text."""

    def __init__(self, wrapped):
        self._wrapped = wrapped

    def render(self):
        return self._wrapped.render()


class OperationsHelp(HelpDecorator):
    """Adds one line for every operation the factory knows about."""

    def render(self):
        lines = [super().render(), "", "Operations:"]
        for name, description in OperationFactory.describe_operations():
            lines.append(f"  {name:<11} {description}")
        return "\n".join(lines)


class CommandsHelp(HelpDecorator):
    """Adds one line for every special command."""

    def __init__(self, wrapped, commands=None):
        super().__init__(wrapped)
        self._commands = COMMAND_DESCRIPTIONS if commands is None else commands

    def render(self):
        lines = [super().render(), "", "Commands:"]
        for name, description in self._commands.items():
            lines.append(f"  {name:<11} {description}")
        return "\n".join(lines)


def build_help_menu():
    """Stack the decorators to build the complete help menu."""
    return CommandsHelp(OperationsHelp(BasicHelp()))