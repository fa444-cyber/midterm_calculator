"""Command-line REPL for the enhanced calculator."""

import logging

from app.calculator import Calculator
from app.exceptions import CalculatorError, OperationError, ValidationError
from app.help_menu import build_help_menu
from app.logger import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


def help_text():
    """Return the help menu, built on the fly with the decorator pattern."""
    return build_help_menu().render()


def build_commands(calculator):
    """Map each special command to a function that returns a message."""

    def show_history():
        return calculator.history.display()

    def clear():
        calculator.clear_history()
        return "History cleared."

    def undo():
        calculator.undo()
        return "Undone."

    def redo():
        calculator.redo()
        return "Redone."

    def save():
        calculator.save_history()
        return "History saved."

    def load():
        calculator.load_history()
        return "History loaded."

    return {
        "help": help_text,
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
    print("Welcome to the Enhanced Calculator!")
    if calculator.startup_warning:
        logger.warning("Startup problem: %s", calculator.startup_warning)
        print(f"Warning: {calculator.startup_warning}")
    print(help_text())
    print()

    while True:
        user_input = input("calc> ").strip()
        command = user_input.lower()

        if command == "exit":
            print("Goodbye!")
            logger.info("Calculator exited")
            break

        try:  # EAFP: just try it, and report any calculator error
            # LBYL: check if it is a special command before parsing a calculation
            if command in commands:
                print(commands[command]())
                logger.info("Command executed: %s", command)
            else:
                calculation = calculator.calculate_from_text(user_input)
                print(f"Result: {calculation.result}")
        except CalculatorError as error:
            log_failure(user_input, error)
            print(f"Error: {error}")
        print()