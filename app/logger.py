"""Application logging: sends the calculator's log messages to a file."""

import logging
from pathlib import Path

LOGGER_NAME = "calculator"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


class Logger:
    """Writes the calculator's log messages to the file named in the configuration."""

    def __init__(self, config):
        self.log_file = Path(config.log_file)
        self._logger = logging.getLogger(LOGGER_NAME)
        self._logger.setLevel(logging.INFO)
        self._handler = self._create_handler(config.default_encoding)
        self._logger.addHandler(self._handler)

    def _create_handler(self, encoding):
        """Create the log folder if needed and open the log file."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(self.log_file, encoding=encoding)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        return handler

    def info(self, message, *args):
        """Record normal activity, such as a finished calculation."""
        self._logger.info(message, *args)

    def warning(self, message, *args):
        """Record something unexpected that the user can fix, such as bad input."""
        self._logger.warning(message, *args)

    def error(self, message, *args):
        """Record a failure, such as a file that could not be saved."""
        self._logger.error(message, *args)

    def close(self):
        """Stop writing to the log file and release it."""
        self._logger.removeHandler(self._handler)
        self._handler.close()