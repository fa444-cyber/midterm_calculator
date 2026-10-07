"""Command-line REPL for the enhanced calculator."""

from app.calculator import Calculator
from app.exceptions import CalculatorError
from app.operations import OperationFactory


def help_text():
    """Return the help message."""
    operations = ", ".join(OperationFactory.available_operations())
    return (
        "Usage: <operation> <number> <number>   (example: add 2 3)\n"
        f"Operations: {operations}\n"
        "Commands: help, history, clear, undo, redo, save, load, exit"
    )


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


def repl(calculator=None):
    """Run the Read-Eval-Print Loop until the user types exit."""
    calculator = calculator or Calculator()
    commands = build_commands(calculator)

    print("Welcome to the Enhanced Calculator!")
    if calculator.startup_warning:
        print(f"Warning: {calculator.startup_warning}")
    print(help_text())
    print()

    while True:
        user_input = input("calc> ").strip()
        command = user_input.lower()

        if command == "exit":
            print("Goodbye!")
            break

        try:  # EAFP: just try it, and report any calculator error
            # LBYL: check if it is a special command before parsing a calculation
            if command in commands:
                print(commands[command]())
            else:
                calculation = calculator.calculate_from_text(user_input)
                print(f"Result: {calculation.result}")
        except CalculatorError as error:
            print(f"Error: {error}")
        print()