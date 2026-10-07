"""Calculation history (pandas) and the observers that react to calculations."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from app.exceptions import CalculatorError

COLUMNS = ["operation", "a", "b", "result", "timestamp"]

logger = logging.getLogger("calculator")


class History:
    """Stores calculations in a DataFrame, with CSV save and load."""

    def __init__(self, max_size=100):
        self.max_size = max_size
        self._df = pd.DataFrame(columns=COLUMNS)

    def __len__(self):
        return len(self._df)

    def add(self, calculation):
        """Append a calculation, dropping the oldest rows past max_size."""
        row = pd.DataFrame([calculation.to_dict()])
        if self._df.empty:
            self._df = row
        else:
            self._df = pd.concat([self._df, row], ignore_index=True)
        self._trim()

    def clear(self):
        """Remove every calculation from the history."""
        self._df = pd.DataFrame(columns=COLUMNS)

    def to_dataframe(self):
        """Return a copy of the history as a DataFrame."""
        return self._df.copy()

    def display(self):
        """Return the history as printable text."""
        if self._df.empty:
            return "No calculations yet."
        return self._df.to_string()

    def snapshot(self):
        """Return a copy of the current state (used by the Memento pattern)."""
        return self._df.copy()

    def restore(self, snapshot):
        """Replace the current state with a snapshot."""
        self._df = snapshot.copy()

    def save(self, path):
        """Write the history to a CSV file."""
        path = Path(path)
        try:  # EAFP: just try to write the file
            path.parent.mkdir(parents=True, exist_ok=True)
            self._df.to_csv(path, index=False)
        except OSError as error:
            raise CalculatorError(f"Could not save history: {error}")

    def load(self, path):
        """Replace the history with the contents of a CSV file."""
        path = Path(path)
        # LBYL: make sure the file exists before reading it
        if not path.exists():
            raise CalculatorError(f"History file not found: {path}")
        try:  # EAFP: just try to read it
            loaded = pd.read_csv(path)
        except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
            raise CalculatorError(f"Could not read history file: {error}")
        # LBYL: check the columns before accepting the data
        if list(loaded.columns) != COLUMNS:
            raise CalculatorError("History file has unexpected columns")
        self._df = loaded
        self._trim()

    def _trim(self):
        """Keep only the newest max_size rows."""
        if len(self._df) > self.max_size:
            self._df = self._df.iloc[-self.max_size:].reset_index(drop=True)


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