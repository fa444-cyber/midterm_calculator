# Midterm Project: Enhanced Calculator

A command-line calculator written in Python. It runs in an interactive loop (a REPL), supports ten operations, keeps a history that can be saved to and loaded from a CSV file with pandas, can undo and redo, writes a log file, reads its settings from a .env file, and prints color-coded output. Every change was tested with pytest, and GitHub Actions checks the tests on every push.

## Features

- Interactive REPL (Read-Eval-Print Loop)
- Ten operations: add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff
- Undo and redo
- Calculation history stored as Calculation objects and saved to a CSV file with pandas
- Auto-save after every calculation, and loading of the saved history at startup
- Logging to a file with INFO, WARNING, and ERROR levels
- Settings loaded from a .env file with python-dotenv, with a default for every setting
- Custom exceptions and input validation, using both LBYL and EAFP error handling
- A help menu that builds itself from the available operations (Decorator pattern)
- Color-coded output with colorama
- Parameterized pytest tests with 100% coverage locally and a 90% minimum in CI

## Design Patterns

- **Factory**: OperationFactory in app/operations.py creates the right operation object from the name the user types.
- **Strategy**: each operation is its own class with the same execute method, so they can be swapped freely.
- **Observer**: LoggingObserver and AutoSaveObserver in app/history.py are told about every calculation. One writes a log entry and the other saves the history to CSV.
- **Memento**: Memento and Caretaker in app/calculator_memento.py save snapshots of the history, which makes undo and redo possible.
- **Facade**: the Calculator class in app/calculator.py gives the REPL one simple interface to the settings, history, observers, validation, and undo/redo.
- **Decorator**: in app/help_menu.py, BasicHelp is wrapped by OperationsHelp and CommandsHelp, which each add a section. Because the operations section reads from the factory, adding a new operation updates the help menu by itself.

## Project Structure

    midterm_calculator/
        app/
            __init__.py
            calculation.py          one calculation (operation, inputs, result, time)
            calculator.py           Calculator facade
            calculator_config.py    settings from environment variables
            calculator_memento.py   Memento and Caretaker (undo and redo)
            calculator_repl.py      the interactive command loop
            colors.py               color helpers (colorama)
            exceptions.py           custom exceptions
            help_menu.py            decorator-based help menu
            history.py              history, CSV save and load, observers
            input_validators.py     input parsing and validation
            logger.py               Logger class for the log file
            operations.py           Strategy classes and OperationFactory
        tests/                      pytest tests for every module
        .env                        default settings
        main.py                     entry point
        pytest.ini                  pytest and coverage settings
        requirements.txt
        .github/workflows/python-app.yml

## Installation

1. Clone the repository and move into it:

        git clone https://github.com/fa444-cyber/midterm_calculator.git
        cd midterm_calculator

2. Create and activate a virtual environment:

        python -m venv venv
        venv\Scripts\Activate.ps1

   On Mac or Linux, activate it with: source venv/bin/activate

3. Install the dependencies:

        pip install -r requirements.txt

## Configuration

Settings are read from environment variables. The .env file in the project folder is loaded automatically with python-dotenv, and every setting has a default, so the calculator also runs without a .env file. To change a setting, edit its line in .env.

| Variable | Default | What it does |
| --- | --- | --- |
| CALCULATOR_LOG_DIR | logs | Folder for the log file |
| CALCULATOR_LOG_FILE | calculator.log | Name of the log file, inside the log folder |
| CALCULATOR_HISTORY_DIR | history | Folder for the history file |
| CALCULATOR_HISTORY_FILE | calculation_history.csv | Name of the history file, inside the history folder |
| CALCULATOR_MAX_HISTORY_SIZE | 100 | How many calculations to keep |
| CALCULATOR_AUTO_SAVE | true | Save the history after every calculation (true or false) |
| CALCULATOR_PRECISION | 4 | Decimal places that results are rounded to |
| CALCULATOR_MAX_INPUT_VALUE | 1000000 | The largest number the calculator accepts |
| CALCULATOR_DEFAULT_ENCODING | utf-8 | Encoding for the history and log files |

Every value is checked when the calculator starts. A bad value, such as a negative precision, a history size of zero, or an unknown encoding, raises a ConfigurationError with a clear message.

## Usage

Start the calculator:

    python main.py

Type a calculation as the operation name followed by two numbers:

    calc> add 2 3
    Result: 5.0

    calc> divide 1 0
    Error: Cannot divide by zero

### Operations

| Command | What it does | Example | Result |
| --- | --- | --- | --- |
| add | Add two numbers | add 2 3 | 5.0 |
| subtract | Subtract the second number from the first | subtract 10 4 | 6.0 |
| multiply | Multiply two numbers | multiply 3 4 | 12.0 |
| divide | Divide the first number by the second | divide 10 4 | 2.5 |
| power | Raise the first number to the power of the second | power 2 3 | 8.0 |
| root | Take the root of the first number (the second is the degree) | root 27 3 | 3.0 |
| modulus | Remainder after dividing the first number by the second | modulus 10 3 | 1.0 |
| int_divide | Divide and round down to a whole number | int_divide 7 2 | 3.0 |
| percent | What percent the first number is of the second | percent 50 200 | 25.0 |
| abs_diff | Distance between the two numbers | abs_diff 3 10 | 7.0 |

int_divide rounds down, so int_divide -7 2 gives -4.0.

### Commands

| Command | What it does |
| --- | --- |
| help | Show the help menu |
| history | Show every calculation so far |
| clear | Erase the history (this can be undone) |
| undo | Undo the last change |
| redo | Redo what was undone |
| save | Save the history to the CSV file |
| load | Load the history from the CSV file |
| exit | Leave the calculator |

Output is color-coded: results are green, errors are red, warnings are yellow, and confirmations and headings are cyan.

## History and CSV

The history is a list of Calculation objects. When it is saved, pandas turns the list into a DataFrame with the columns operation, a, b, result, and timestamp, and writes it to history/calculation_history.csv. When it is loaded, pandas reads the file and each row is turned back into a Calculation object.

With auto-save on, the file is written after every calculation and loaded again the next time the calculator starts. If the file is missing, empty, or damaged (wrong columns, missing values, an unknown operation, or a bad timestamp), the calculator shows a warning and starts with an empty history instead of crashing.

## Logging

Every run writes to logs/calculator.log (the folder and file name come from the settings):

- INFO: the calculator starting and exiting, every command, and every calculation with its operation, operands, and result
- WARNING: input that was rejected (a typo, a bad number, divide by zero) and a history file that could not be read at startup
- ERROR: other failures, such as loading a history file that does not exist

Example:

    2026-10-22 16:09:33,622 INFO Calculation performed: add(2.0, 3.0) = 5.0
    2026-10-22 16:09:38,931 WARNING Rejected input 'divide 1 0': Cannot divide by zero

## Error Handling

All calculator errors inherit from CalculatorError (ValidationError, OperationError, ConfigurationError). The REPL catches them, prints a friendly message, logs it, and keeps running. The code uses both styles on purpose:

- **LBYL (Look Before You Leap)**: check first, then act. Examples are checking for a zero divisor, checking that the input has exactly three parts, and checking that the history file exists before reading it.
- **EAFP (Easier to Ask Forgiveness than Permission)**: try it and handle the failure. Examples are converting text to a number, reading and writing the CSV file, and catching an overflow in the power operation.

## Testing

Run the whole test suite with coverage:

    pytest

pytest.ini turns on the coverage report, and locally the run fails if coverage drops below 100%. Lines that can never run, such as the empty bodies of abstract methods, are marked with a pragma: no cover comment. The tests use parameterized cases for typical values and edge cases such as division by zero, negative exponents, and damaged history files. To run one file without the coverage rule, add --no-cov:

    pytest tests\test_help_menu.py --no-cov

## Continuous Integration

A GitHub Actions workflow in .github/workflows/python-app.yml runs on every push and pull request to main. It checks out the code, sets up Python, installs the packages from requirements.txt, and runs pytest with coverage. The build fails if coverage falls below 90%.

## Development Workflow

Work was done on feature branches (new-operations, logging-config, history-objects, dynamic-help, color-output, and readme) and merged into main with pull requests. Each pull request had to pass the GitHub Actions check before it was merged, and the commit history records the work step by step.