"""Tests for the modulus and integer division operations."""

import pytest

from app.exceptions import OperationError
from app.operations import IntegerDivide, Modulus, OperationFactory


@pytest.mark.parametrize("a, b, expected", [
    (10, 3, 1),
    (9, 3, 0),
    (-7, 3, 2),
    (7, -3, -2),
    (5.5, 2, 1.5),
    (0, 4, 0),
])
def test_modulus(a, b, expected):
    assert Modulus().execute(a, b) == pytest.approx(expected)


def test_modulus_by_zero():
    with pytest.raises(OperationError, match="modulus with zero"):
        Modulus().execute(5, 0)


@pytest.mark.parametrize("a, b, expected", [
    (7, 2, 3),
    (10, 5, 2),
    (-7, 2, -4),
    (7.5, 2, 3.0),
    (0, 3, 0),
])
def test_int_divide(a, b, expected):
    assert IntegerDivide().execute(a, b) == expected


def test_int_divide_by_zero():
    with pytest.raises(OperationError, match="divide by zero"):
        IntegerDivide().execute(5, 0)


@pytest.mark.parametrize("name, expected_class", [
    ("modulus", Modulus),
    ("int_divide", IntegerDivide),
])
def test_factory_creates_the_new_operations(name, expected_class):
    assert isinstance(OperationFactory.create_operation(name), expected_class)