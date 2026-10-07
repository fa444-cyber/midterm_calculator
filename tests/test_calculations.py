"""Tests for the Calculation record."""

from datetime import datetime

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError


@pytest.mark.parametrize("operation, a, b, expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 3, 4, 12),
    ("divide", 10, 2, 5.0),
    ("power", 2, 3, 8),
    ("root", 27, 3, 3.0),
])
def test_calculation_computes_the_result(operation, a, b, expected):
    assert Calculation(operation, a, b).result == pytest.approx(expected)


@pytest.mark.parametrize("a, b, precision, expected", [
    (1, 3, 2, 0.33),
    (1, 3, 4, 0.3333),
    (2, 3, 0, 1.0),
])
def test_calculation_rounds_to_the_given_precision(a, b, precision, expected):
    assert Calculation("divide", a, b, precision).result == expected


def test_calculation_keeps_full_precision_by_default():
    assert Calculation("divide", 1, 3).result == 1 / 3


def test_calculation_uses_a_given_timestamp():
    moment = datetime(2026, 1, 1, 12, 0, 0)
    assert Calculation("add", 1, 1, timestamp=moment).timestamp == moment


def test_calculation_creates_a_timestamp_when_none_is_given():
    assert isinstance(Calculation("add", 1, 1).timestamp, datetime)


def test_to_dict_returns_one_history_row():
    moment = datetime(2026, 1, 1, 12, 0, 0)
    row = Calculation("add", 2, 3, timestamp=moment).to_dict()
    assert row == {
        "operation": "add",
        "a": 2,
        "b": 3,
        "result": 5,
        "timestamp": "2026-01-01T12:00:00",
    }


def test_str_describes_the_calculation():
    assert str(Calculation("add", 2, 3)) == "add(2, 3) = 5"


def test_unknown_operation_is_rejected():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation("modulo", 1, 2)


@pytest.mark.parametrize("operation, a, b", [
    ("divide", 1, 0),
    ("root", -4, 2),
    ("power", 0, -1),
])
def test_operation_errors_pass_through(operation, a, b):
    with pytest.raises(OperationError):
        Calculation(operation, a, b)