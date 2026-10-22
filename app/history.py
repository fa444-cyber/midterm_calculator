"""Calculation history (a list of Calculation objects) and the observers."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from app.calculation import Calculation
from app.exceptions import CalculatorError

COLUMNS = ["operation", "a", "b", "result", "timestamp"]

logger = logging.getLogger("calculator")


class History:
    """Keeps Calculation objects in a list, and uses pandas for CSV save and load."""

    def __init__(self, max_size=100, encoding="utf-8"):
        self.max_size = max_size
        self.encoding = encoding
        self._calculations = []

    def __len__(self):
        return len(self._calculations)

    @property
    def calculations(self):
        """Return a copy of the list of calculations, oldest first."""
        return list(self._calculations)

    def add(self, calculation):
        """Append a calculation, dropping the oldest ones past max_size."""
        self._calculations.append(calculation)
        self._trim()

    def clear(self):
        """Remove every calculation from the history."""
        self._calculations = []

    def to_dataframe(self):
        """Convert the calculations into a DataFrame, one row per calculation."""
        rows = [calculation.to_dict() for calculation in self._calculations]
        return pd.DataFrame(rows, columns=COLUMNS)

    def display(self):
        """Return the history as printable text."""
        if not self._calculations:
            return "No calculations yet."
        return self.to_dataframe().to_string()

    def snapshot(self):
        """Return a copy of the current state (used by the Memento pattern)."""
        return list(self._calculations)

    def restore(self, snapshot):
        """Replace the current state with a snapshot."""
        self._calculations = list(snapshot)

    def save(self, path):
        """Write the history to a CSV file using pandas."""
        path = Path(path)
        try:  # EAFP: just try to write the file
            path.parent.mkdir(parents=True, exist_ok=True)
            self.to_dataframe().to_csv(path, index=False, encoding=self.encoding)
        except OSError as error:
            raise CalculatorError(f"Could not save history: {error}")

    def load(self, path):
        """Replace the history with the calculations stored in a CSV file."""
        path = Path(path)
        # LBYL: make sure the file exists before reading it
        if not path.exists():
            raise CalculatorError(f"History file not found: {path}")
        try:  # EAFP: just try to read it
            loaded = pd.read_csv(path, encoding=self.encoding)
        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            UnicodeDecodeError,
        ) as error:
            raise CalculatorError(f"Could not read history file: {error}")
        # LBYL: check the columns and the cells before accepting the data
        if list(loaded.columns) != COLUMNS:
            raise CalculatorError("History file has unexpected columns")
        if loaded.isna().any().any():
            raise CalculatorError("History file has missing values")
        try:  # EAFP: turn each row back into a Calculation
            calculations = [
                Calculation.from_dict(row) for row in loaded.to_dict("records")
            ]
        except (CalculatorError, ValueError, TypeError) as error:
            raise CalculatorError(f"History file has invalid data: {error}")
        self._calculations = calculations
        self._trim()

    def _trim(self):
        """Keep only the newest max_size calculations."""
        if len(self._calculations) > self.max_size:
            self._calculations = self._calculations[-self.max_size:]


class Observer(ABC):
    """Observer interface: reacts whenever a calculation is performed."""

    @abstractmethod
    def update(self, calculation):
        """Called by the subject after each new calculation."""
        pass  # pragma: no cover


class LoggingObserver(Observer):
    """Writes every calculation to the application log."""

    def update(self, calculation):
        logger.info("Calculation performed: %s", calculation)


class AutoSaveObserver(Observer):
    """Saves the history to a CSV file after every calculation."""

    def __init__(self, history, path):
        self.history = history
        self.path = path

    def update(self, calculation):
        self.history.save(self.path)