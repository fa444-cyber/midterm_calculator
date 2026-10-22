"""Tests for turning a Calculation into a row and back again."""

from datetime import datetime

import pytest

from app.calculation import Calculation
from app.exceptions import OperationError

MOMENT = datetime(2026, 1, 1, 12, 0, 0)


@pytest.mark.parametrize("operation, a, b", [
    ("add", 2, 3),
    ("divide", 1, 3),
    ("modulus", 10, 3),
    ("percent", 1, 4),
])
def test_from_dict_reverses_to_dict(operation, a, b):
    original = Calculation(operation, a, b, precision=4, timestamp=MOMENT)
    rebuilt = Calculation.from_dict(original.to_dict())
    assert rebuilt.to_dict() == original.to_dict()


def test_from_dict_keeps_the_saved_result():
    row = {
        "operation": "divide",
        "a": 1,
        "b": 3,
        "result": 0.3333,
        "timestamp": MOMENT.isoformat(),
    }
    assert Calculation.from_dict(row).result == 0.3333


def test_from_dict_rejects_an_unknown_operation():
    row = {
        "operation": "sqrt",
        "a": 1,
        "b": 2,
        "result": 3,
        "timestamp": MOMENT.isoformat(),
    }
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation.from_dict(row)


def test_from_dict_rejects_a_bad_timestamp():
    row = {"operation": "add", "a": 1, "b": 2, "result": 3, "timestamp": "yesterday"}
    with pytest.raises(ValueError):
        Calculation.from_dict(row)