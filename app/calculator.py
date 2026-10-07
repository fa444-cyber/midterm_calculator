"""Facade: one simple interface over the calculator's subsystems."""

from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import Caretaker, Memento
from app.exceptions import CalculatorError
from app.history import AutoSaveObserver, History, LoggingObserver
from app.input_validators import InputValidator


class Calculator:
    """Facade hiding config, history, observers, and undo/redo behind simple methods."""

    def __init__(self, config=None):
        self.config = config or CalculatorConfig()
        self.history = History(self.config.max_history_size)
        self.caretaker = Caretaker()
        self.startup_warning = None
        self._observers = []

        self.attach(LoggingObserver())
        if self.config.auto_save:
            self.attach(AutoSaveObserver(self.history, self.config.history_file))

        # LBYL: only try to load history if the file exists
        if self.config.history_file.exists():
            try:  # EAFP: a bad file should not crash the app
                self.history.load(self.config.history_file)
            except CalculatorError as error:
                self.startup_warning = str(error)

    def attach(self, observer):
        """Register an observer to be told about every new calculation."""
        self._observers.append(observer)

    def notify(self, calculation):
        """Tell every observer that a calculation was performed."""
        for observer in self._observers:
            observer.update(calculation)

    def calculate(self, operation_name, a, b):
        """Run an operation, record it in the history, and notify observers."""
        # Build the calculation first: if it fails, nothing has changed yet
        calculation = Calculation(operation_name, a, b, self.config.precision)
        self._remember()
        self.history.add(calculation)
        self.notify(calculation)
        return calculation

    def calculate_from_text(self, text):
        """Validate a line like 'add 2 3' and run it."""
        operation_name, a, b = InputValidator.parse_calculation(
            text, self.config.max_input_value
        )
        return self.calculate(operation_name, a, b)

    def undo(self):
        """Step the history back to its previous state."""
        current = Memento(self.history.snapshot())
        self.history.restore(self.caretaker.undo(current).state)

    def redo(self):
        """Step the history forward again after an undo."""
        current = Memento(self.history.snapshot())
        self.history.restore(self.caretaker.redo(current).state)

    def clear_history(self):
        """Erase the history (this can be undone)."""
        self._remember()
        self.history.clear()

    def save_history(self):
        """Save the history to the configured CSV file."""
        self.history.save(self.config.history_file)

    def load_history(self):
        """Replace the history with the contents of the CSV file (undoable)."""
        before = self.history.snapshot()
        self.history.load(self.config.history_file)
        self.caretaker.save(Memento(before))

    def _remember(self):
        """Save the current state so it can be undone."""
        self.caretaker.save(Memento(self.history.snapshot()))