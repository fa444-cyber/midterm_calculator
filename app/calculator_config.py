"""Application settings, loaded from environment variables and an optional .env file."""

import codecs
import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


class CalculatorConfig:
    """Holds validated application settings loaded from the environment."""

    def __init__(self, base_dir=None):
        load_dotenv()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

        # Folders: each one falls back to a folder inside base_dir
        self.log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", self.base_dir / "logs"))
        self.history_dir = Path(
            os.getenv("CALCULATOR_HISTORY_DIR", self.base_dir / "history")
        )

        # Files: a file name (or full path) that lives inside the matching folder
        self.log_file = self.log_dir / os.getenv(
            "CALCULATOR_LOG_FILE", "calculator.log"
        )
        self.history_file = self.history_dir / os.getenv(
            "CALCULATOR_HISTORY_FILE", "calculation_history.csv"
        )

        # Numbers and switches
        self.max_history_size = self._get_int("CALCULATOR_MAX_HISTORY_SIZE", 100)
        self.auto_save = self._get_bool("CALCULATOR_AUTO_SAVE", True)
        self.precision = self._get_int("CALCULATOR_PRECISION", 4)
        self.max_input_value = self._get_float("CALCULATOR_MAX_INPUT_VALUE", 1e6)
        self.default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")
        self.validate()

    def validate(self):
        """LBYL: check that every setting makes sense before the app uses it."""
        if self.max_history_size <= 0:
            raise ConfigurationError("CALCULATOR_MAX_HISTORY_SIZE must be positive")
        if self.precision < 0:
            raise ConfigurationError("CALCULATOR_PRECISION cannot be negative")
        if self.max_input_value <= 0:
            raise ConfigurationError("CALCULATOR_MAX_INPUT_VALUE must be positive")
        try:  # EAFP: let Python tell us whether it knows this encoding
            codecs.lookup(self.default_encoding)
        except LookupError:
            raise ConfigurationError(
                "CALCULATOR_DEFAULT_ENCODING must be a valid text encoding, "
                f"got '{self.default_encoding}'"
            )

    @staticmethod
    def _get_int(name, default):
        """Read an integer setting from the environment."""
        raw = os.getenv(name)
        if raw is None:
            return default
        try:  # EAFP: just try the conversion
            return int(raw)
        except ValueError:
            raise ConfigurationError(f"{name} must be an integer, got '{raw}'")

    @staticmethod
    def _get_float(name, default):
        """Read a decimal setting from the environment."""
        raw = os.getenv(name)
        if raw is None:
            return default
        try:  # EAFP
            return float(raw)
        except ValueError:
            raise ConfigurationError(f"{name} must be a number, got '{raw}'")

    @staticmethod
    def _get_bool(name, default):
        """Read a true/false setting from the environment."""
        raw = os.getenv(name)
        if raw is None:
            return default
        value = raw.strip().lower()
        # LBYL: only accept values we recognize
        if value in ("true", "1", "yes"):
            return True
        if value in ("false", "0", "no"):
            return False
        raise ConfigurationError(f"{name} must be true or false, got '{raw}'")