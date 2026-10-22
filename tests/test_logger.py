"""Tests for the Logger class."""

import logging

import pytest

from app.calculator_config import CalculatorConfig
from app.logger import Logger


@pytest.fixture
def logger(tmp_path):
    instance = Logger(CalculatorConfig(base_dir=tmp_path))
    yield instance
    instance.close()


def read_log(logger):
    return logger.log_file.read_text(encoding="utf-8")


def test_log_folder_and_file_are_created(logger):
    assert logger.log_file.parent.is_dir()
    assert logger.log_file.exists()


@pytest.mark.parametrize("method, level", [
    ("info", "INFO"),
    ("warning", "WARNING"),
    ("error", "ERROR"),
])
def test_each_level_is_recorded(logger, method, level):
    getattr(logger, method)("something happened")
    assert f"{level} something happened" in read_log(logger)


def test_message_arguments_are_filled_in(logger):
    logger.info("Calculation performed: %s", "add(2, 3) = 5")
    assert "INFO Calculation performed: add(2, 3) = 5" in read_log(logger)


def test_messages_from_other_modules_are_collected(logger):
    logging.getLogger("calculator").info("from another module")
    assert "from another module" in read_log(logger)


def test_debug_messages_are_not_recorded(logger):
    logging.getLogger("calculator").debug("too detailed")
    assert "too detailed" not in read_log(logger)


def test_close_stops_writing_to_the_file(tmp_path):
    instance = Logger(CalculatorConfig(base_dir=tmp_path))
    instance.close()
    instance.info("after close")
    assert "after close" not in instance.log_file.read_text(encoding="utf-8")


def test_the_configured_encoding_is_used(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "utf-16")
    instance = Logger(CalculatorConfig(base_dir=tmp_path))
    instance.info("caf\u00e9")
    instance.close()
    assert "caf\u00e9" in instance.log_file.read_text(encoding="utf-16")