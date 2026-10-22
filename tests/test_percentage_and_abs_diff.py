"""Tests for the percentage and absolute difference operations."""

import pytest

from app.exceptions import OperationError
from app.operations import AbsoluteDifference, OperationFactory, Percentage


@pytest.mark.parametrize("a, b, expected", [
    (50, 200, 25.0),
    (1, 4, 25.0),
    (3, 4, 75.0),
    (200, 100, 200.0),
    (0, 5, 0.0),
    (-10, 40, -25.0),
    (1, 3, 33.333333),
])
def test_percentage(a, b, expected):
    assert Percentage().execute(a, b) == pytest.approx(expected)


def test_percentage_of_zero():
    with pytest.raises(OperationError, match="percentage of zero"):
        Percentage().execute(5, 0)


@pytest.mark.parametrize("a, b, expected", [
    (10, 4, 6),
    (4, 10, 6),
    (-3, 3, 6),
    (-3, -8, 5),
    (2.5, 1.0, 1.5),
    (7, 7, 0),
])
def test_absolute_difference(a, b, expected):
    assert AbsoluteDifference().execute(a, b) == expected


@pytest.mark.parametrize("name, expected_class", [
    ("percent", Percentage),
    ("abs_diff", AbsoluteDifference),
])
def test_factory_creates_the_new_operations(name, expected_class):
    assert isinstance(OperationFactory.create_operation(name), expected_class)