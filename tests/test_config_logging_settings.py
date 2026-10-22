"""Tests for the log, history file, and encoding settings."""

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


def test_logging_defaults(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.log_dir == tmp_path / "logs"
    assert config.log_file == tmp_path / "logs" / "calculator.log"
    assert config.default_encoding == "utf-8"


def test_log_dir_can_be_overridden(tmp_path, monkeypatch):
    custom = tmp_path / "my_logs"
    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(custom))
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.log_dir == custom
    assert config.log_file == custom / "calculator.log"


def test_log_file_name_can_be_overridden(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_LOG_FILE", "events.log")
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.log_file == tmp_path / "logs" / "events.log"


def test_history_file_name_can_be_overridden(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "saved.csv")
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.history_file == tmp_path / "history" / "saved.csv"


@pytest.mark.parametrize("encoding", ["utf-8", "latin-1", "ascii"])
def test_valid_encodings_are_accepted(tmp_path, monkeypatch, encoding):
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", encoding)
    assert CalculatorConfig(base_dir=tmp_path).default_encoding == encoding


@pytest.mark.parametrize("encoding", ["not-a-real-encoding", "utf-99"])
def test_unknown_encodings_are_rejected(tmp_path, monkeypatch, encoding):
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", encoding)
    with pytest.raises(ConfigurationError, match="valid text encoding"):
        CalculatorConfig(base_dir=tmp_path)