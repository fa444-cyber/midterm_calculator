"""Tests for the custom exceptions."""

import pytest

from app.exceptions import (
    CalculatorError,
    ConfigurationError,
    OperationError,
    ValidationError,
)


@pytest.mark.parametrize(
    "error_class", [ValidationError, OperationError, ConfigurationError]
)
def test_specific_errors_inherit_from_calculator_error(error_class):
    assert issubclass(error_class, CalculatorError)


@pytest.mark.parametrize(
    "error_class",
    [CalculatorError, ValidationError, OperationError, ConfigurationError],
)
def test_errors_keep_their_message(error_class):
    with pytest.raises(error_class, match="something went wrong"):
        raise error_class("something went wrong")


@pytest.mark.parametrize(
    "error_class", [ValidationError, OperationError, ConfigurationError]
)
def test_base_class_catches_every_specific_error(error_class):
    with pytest.raises(CalculatorError):
        raise error_class("boom")