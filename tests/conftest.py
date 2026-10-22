"""Shared fixtures for every test file."""

import pytest

ENV_VARS = [
    "CALCULATOR_LOG_DIR",
    "CALCULATOR_LOG_FILE",
    "CALCULATOR_HISTORY_DIR",
    "CALCULATOR_HISTORY_FILE",
    "CALCULATOR_MAX_HISTORY_SIZE",
    "CALCULATOR_AUTO_SAVE",
    "CALCULATOR_PRECISION",
    "CALCULATOR_MAX_INPUT_VALUE",
    "CALCULATOR_DEFAULT_ENCODING",
]


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    """Give every test a clean environment and stop it reading a real .env file."""
    monkeypatch.setattr("app.calculator_config.load_dotenv", lambda: None)
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)