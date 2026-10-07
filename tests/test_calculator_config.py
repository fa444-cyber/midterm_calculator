"""Tests for the configuration manager."""

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

ENV_VARS = [
    "CALCULATOR_HISTORY_DIR",
    "CALCULATOR_MAX_HISTORY_SIZE",
    "CALCULATOR_AUTO_SAVE",
    "CALCULATOR_PRECISION",
    "CALCULATOR_MAX_INPUT_VALUE",
]


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Start every test with no calculator settings and no .env loading."""
    monkeypatch.setattr("app.calculator_config.load_dotenv", lambda: None)
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_defaults(tmp_path):
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.base_dir == tmp_path
    assert config.history_dir == tmp_path / "history"
    assert config.history_file == tmp_path / "history" / "calculation_history.csv"
    assert config.max_history_size == 100
    assert config.auto_save is True
    assert config.precision == 4
    assert config.max_input_value == 1e6


def test_base_dir_defaults_to_current_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert CalculatorConfig().base_dir.resolve() == tmp_path.resolve()


@pytest.mark.parametrize("name, value, attribute, expected", [
    ("CALCULATOR_MAX_HISTORY_SIZE", "50", "max_history_size", 50),
    ("CALCULATOR_PRECISION", "0", "precision", 0),
    ("CALCULATOR_PRECISION", "8", "precision", 8),
    ("CALCULATOR_MAX_INPUT_VALUE", "250.5", "max_input_value", 250.5),
    ("CALCULATOR_AUTO_SAVE", "false", "auto_save", False),
])
def test_settings_come_from_the_environment(
    tmp_path, monkeypatch, name, value, attribute, expected
):
    monkeypatch.setenv(name, value)
    assert getattr(CalculatorConfig(base_dir=tmp_path), attribute) == expected


def test_history_dir_can_be_overridden(tmp_path, monkeypatch):
    custom = tmp_path / "custom"
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(custom))
    config = CalculatorConfig(base_dir=tmp_path)
    assert config.history_dir == custom
    assert config.history_file == custom / "calculation_history.csv"


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", " Yes "])
def test_auto_save_accepts_true_values(tmp_path, monkeypatch, value):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    assert CalculatorConfig(base_dir=tmp_path).auto_save is True


@pytest.mark.parametrize("value", ["false", "FALSE", "0", "no"])
def test_auto_save_accepts_false_values(tmp_path, monkeypatch, value):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    assert CalculatorConfig(base_dir=tmp_path).auto_save is False


@pytest.mark.parametrize("name, value, message", [
    ("CALCULATOR_MAX_HISTORY_SIZE", "many", "must be an integer"),
    ("CALCULATOR_PRECISION", "2.5", "must be an integer"),
    ("CALCULATOR_MAX_INPUT_VALUE", "big", "must be a number"),
    ("CALCULATOR_AUTO_SAVE", "maybe", "must be true or false"),
    ("CALCULATOR_MAX_HISTORY_SIZE", "0", "must be positive"),
    ("CALCULATOR_MAX_HISTORY_SIZE", "-5", "must be positive"),
    ("CALCULATOR_PRECISION", "-1", "cannot be negative"),
    ("CALCULATOR_MAX_INPUT_VALUE", "0", "must be positive"),
    ("CALCULATOR_MAX_INPUT_VALUE", "-10", "must be positive"),
])
def test_bad_settings_raise_configuration_error(
    tmp_path, monkeypatch, name, value, message
):
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigurationError, match=message):
        CalculatorConfig(base_dir=tmp_path)