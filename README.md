# Enhanced Calculator

A command-line calculator written in Python. It uses five design patterns (Factory, Strategy, Observer, Memento, and Facade), keeps its calculation history in a pandas DataFrame that is saved to and loaded from a CSV file, reads its settings from environment variables, and has 100% test coverage enforced by GitHub Actions.

## Features

- Interactive REPL (Read-Eval-Print Loop)
- Six operations: add, subtract, multiply, divide, power, and root
- Calculation history stored in a pandas DataFrame
- History saved to a CSV file automatically and loaded again at startup
- Undo and redo
- Special commands: help, history, clear, undo, redo, save, load, exit
- Configuration through environment variables and a .env file
- Custom exceptions and input validation, using both LBYL and EAFP error handling
- Logging of every calculation
- 100% test coverage, enforced by pytest and by GitHub Actions

## Design Patterns

- **Factory**: OperationFactory in app/operations.py creates the right operation object from the name the user types.
- **Strategy**: each operation (Add, Subtract, Multiply, Divide, Power, Root) is its own class with the same execute method, so they can be swapped freely.
- **Observer**: LoggingObserver and AutoSaveObserver in app/history.py are notified after every calculation. One writes a log entry and the other saves the history to CSV.
- **Memento**: Memento and Caretaker in app/calculator_memento.py save snapshots of the history, which makes undo and redo possible.
- **Facade**: the Calculator class in app/calculator.py gives the REPL one simple interface to the config, history, observers, validation, and undo/redo.

## Project Structure

    enhanced_calculator/
        app/
            __init__.py
            calculation.py          one executed calculation (operation, inputs, result, time)
            calculator.py           Calculator facade
            calculator_config.py    settings from environment variables
            calculator_memento.py   Memento and Caretaker (undo and redo)
            calculator_repl.py      the interactive command loop
            exceptions.py           custom exceptions
            history.py              pandas history, CSV save and load, observers
            input_validators.py     input parsing and validation
            operations.py           Strategy classes and OperationFactory
        tests/
            conftest.py
            test_calculations.py
            test_calculator.py
            test_calculator_config.py
            test_calculator_memento.py
            test_calculator_repl.py
            test_exceptions.py
            test_history.py
            test_input_validators.py
            test_operations.py
        main.py
        pytest.ini
        requirements.txt
        .github/workflows/python-app.yml

## Setup

1. Clone the repository and move into it:

        git clone git@github.com:fa444-cyber/enhanced_calculator.git
        cd enhanced_calculator

2. Create and activate a virtual environment:

        python -m venv venv
        venv\Scripts\Activate.ps1

   On Mac or Linux, activate it with: source venv/bin/activate

3. Install the dependencies:

        pip install -r requirements.txt

## Usage

Start the calculator:

    python main.py

Type a calculation as the operation name followed by two numbers:

    calc> add 2 3
    Result: 5.0

    calc> power 2 3
    Result: 8.0

    calc> root 27 3
    Result: 3.0

    calc> divide 1 0
    Error: Cannot divide by zero

The root operation takes the b-th root of a, so root 27 3 is the cube root of 27.

### Commands

- help: show the usage message
- history: show every calculation in the current session
- clear: erase the history (this can be undone)
- undo: step the history back
- redo: step the history forward again after an undo
- save: save the history to the CSV file
- load: replace the history with the contents of the CSV file
- exit: leave the calculator

## Configuration

Settings are read from environment variables. You can also put them in a file named .env in the project folder, which is loaded with python-dotenv. Every setting has a default.

- CALCULATOR_HISTORY_DIR: folder for the history CSV (default: history, inside the project folder)
- CALCULATOR_MAX_HISTORY_SIZE: how many calculations to keep (default: 100)
- CALCULATOR_AUTO_SAVE: save the history after every calculation, true or false (default: true)
- CALCULATOR_PRECISION: decimal places results are rounded to (default: 4)
- CALCULATOR_MAX_INPUT_VALUE: the largest number the calculator will accept (default: 1000000)

Invalid values, such as a negative precision or a non-numeric history size, raise a ConfigurationError with a clear message.

## History and CSV

Every calculation is stored as a row in a pandas DataFrame with the columns operation, a, b, result, and timestamp. With auto-save on, the history is written to history/calculation_history.csv after every calculation, and the file is loaded again the next time the calculator starts. If the file is damaged, the calculator shows a warning and starts with an empty history instead of crashing. Each run also writes calculator.log.

## Error Handling

The calculator uses two styles of error handling on purpose:

- **LBYL (Look Before You Leap)**: check first, then act. Examples are checking for a zero divisor before dividing, checking that the input has exactly three parts, checking that the history file exists before reading it, and validating configuration values.
- **EAFP (Easier to Ask Forgiveness than Permission)**: try it, and handle the failure. Examples are converting text to a number inside try and except, reading and writing the CSV file, and catching an overflow in the power operation.

All calculator errors inherit from CalculatorError, so the REPL catches any of them, prints a friendly message, and keeps running.

## Testing

Run the whole test suite:

    pytest

pytest.ini turns on coverage reporting and fails the run if coverage is below 100%. Lines that can never run, such as the empty bodies of abstract methods, are marked with a pragma: no cover comment so they do not count against the total.

## Continuous Integration

A GitHub Actions workflow in .github/workflows/python-app.yml runs on every push and pull request to main. It installs the dependencies, runs the tests with coverage, and then runs coverage report with a 100% requirement. If coverage drops below 100%, the build fails.