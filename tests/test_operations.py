"""Tests for the arithmetic operations and the OperationFactory."""

import pytest

from app.exceptions import OperationError
from app.operations import (
    Add,
    Divide,
    Multiply,
    Operation,
    OperationFactory,
    Power,
    Root,
    Subtract,
)


@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
    (2.5, 0.5, 3.0),
    (-5, -5, -10),
])
def test_add(a, b, expected):
    assert Add().execute(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (0, 5, -5),
    (-1, -1, 0),
    (2.5, 0.5, 2.0),
])
def test_subtract(a, b, expected):
    assert Subtract().execute(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (3, 4, 12),
    (-2, 3, -6),
    (0, 5, 0),
    (-3, -3, 9),
    (1.5, 2, 3.0),
])
def test_multiply(a, b, expected):
    assert Multiply().execute(a, b) == expected


@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5),
    (9, 3, 3),
    (-10, 2, -5),
    (1, 4, 0.25),
])
def test_divide(a, b, expected):
    assert Divide().execute(a, b) == pytest.approx(expected)


def test_divide_by_zero():
    with pytest.raises(OperationError, match="divide by zero"):
        Divide().execute(5, 0)


@pytest.mark.parametrize("a, b, expected", [
    (2, 3, 8),
    (2, 0, 1),
    (5, 1, 5),
    (2, -1, 0.5),
    (9, 0.5, 3.0),
    (-2, 3, -8),
    (0, 0, 1),
])
def test_power(a, b, expected):
    assert Power().execute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("a, b, message", [
    (0, -1, "negative power"),
    (10.0, 1000.0, "too large"),
    (-8, 0.5, "not a real number"),
])
def test_power_errors(a, b, message):
    with pytest.raises(OperationError, match=message):
        Power().execute(a, b)


@pytest.mark.parametrize("a, b, expected", [
    (27, 3, 3.0),
    (16, 2, 4.0),
    (100, 2, 10.0),
    (8, 3, 2.0),
    (5, 1, 5.0),
])
def test_root(a, b, expected):
    assert Root().execute(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("a, b, message", [
    (9, 0, "cannot be zero"),
    (-4, 2, "negative number"),
])
def test_root_errors(a, b, message):
    with pytest.raises(OperationError, match=message):
        Root().execute(a, b)


@pytest.mark.parametrize("name, expected_class", [
    ("add", Add),
    ("subtract", Subtract),
    ("multiply", Multiply),
    ("divide", Divide),
    ("power", Power),
    ("root", Root),
])
def test_factory_creates_the_right_operation(name, expected_class):
    assert isinstance(OperationFactory.create_operation(name), expected_class)


def test_factory_ignores_case():
    assert isinstance(OperationFactory.create_operation("ADD"), Add)


def test_factory_rejects_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        OperationFactory.create_operation("modulo")


def test_available_operations_includes_the_original_six():
    assert {
        "add", "subtract", "multiply", "divide", "power", "root",
    } <= set(OperationFactory.available_operations())


@pytest.mark.parametrize("name", OperationFactory.available_operations())
def test_every_strategy_shares_the_same_interface(name):
    operation = OperationFactory.create_operation(name)
    assert isinstance(operation, Operation)
    assert isinstance(operation.execute(6, 2), (int, float))


def test_operation_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Operation()