"""Command-line REPL for the enhanced calculator."""

import logging

from app.calculator import Calculator
from app.colors import color_help, failure, heading, info, success, warning
from app.exceptions import CalculatorError, OperationError, ValidationError
from app.help_menu import build_help_menu
from app.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def help_text():
    """Return the help menu, built on the fly with the decorator pattern."""
    return build_help_menu().render()


def build_commands(calculator):
    """Map each special command to a function that returns a message."""

    def show_help():
        return color_help(help_text())

    def show_history():
        return calculator.history.display()

    def clear():
        calculator.clear_history()
        return info("History cleared.")

    def undo():
        calculator.undo()
        return info("Undone.")

    def redo():
        calculator.redo()
        return info("Redone.")

    def save():
        calculator.save_history()
        return info("History saved.")

    def load():
        calculator.load_history()
        return info("History loaded.")

    return {
        "help": show_help,
        "history": show_history,
        "clear": clear,
        "undo": undo,
        "redo": redo,
        "save": save,
        "load": load,
    }


def log_failure(user_input, error):
    """Log a failed command: a WARNING when the user can fix it, an ERROR otherwise."""
    if isinstance(error, (ValidationError, OperationError)):
        logger.warning("Rejected input %r: %s", user_input, error)
    else:
        logger.error("Command %r failed: %s", user_input, error)


def repl(calculator=None):
    """Run the Read-Eval-Print Loop until the user types exit."""
    calculator = calculator or Calculator()
    commands = build_commands(calculator)

    logger.info("Calculator started")
    print(heading("Welcome to the Enhanced Calculator!"))
    if calculator.startup_warning:
        logger.warning("Startup problem: %s", calculator.startup_warning)
        print(warning(f"Warning: {calculator.startup_warning}"))
    print(color_help(help_text()))
    print()

    while True:
        user_input = input("calc> ").strip()
        command = user_input.lower()

        if command == "exit":
            print(info("Goodbye!"))
            logger.info("Calculator exited")
            break

        try:  # EAFP: just try it, and report any calculator error
            # LBYL: check if it is a special command before parsing a calculation
            if command in commands:
                print(commands[command]())
                logger.info("Command executed: %s", command)
            else:
                calculation = calculator.calculate_from_text(user_input)
                print(success(f"Result: {calculation.result}"))
        except CalculatorError as error:
            log_failure(user_input, error)
            print(failure(f"Error: {error}"))
        print()