"""Tests for the input validators."""

import pytest

from app.exceptions import ValidationError
from app.input_validators import InputValidator

MAX = 1e6


@pytest.mark.parametrize("value, expected", [
    ("5", 5.0),
    ("-2.5", -2.5),
    ("0", 0.0),
    ("1e3", 1000.0),
    ("  7  ", 7.0),
    (7, 7.0),
    ("1000000", 1000000.0),
])
def test_validate_number_accepts_valid_input(value, expected):
    assert InputValidator.validate_number(value, MAX) == expected


@pytest.mark.parametrize("value, message", [
    ("abc", "not a valid number"),
    ("", "not a valid number"),
    (None, "not a valid number"),
    ("nan", "not a finite number"),
    ("inf", "not a finite number"),
    ("-inf", "not a finite number"),
    ("1000001", "exceeds the maximum"),
    ("-1000001", "exceeds the maximum"),
])
def test_validate_number_rejects_bad_input(value, message):
    with pytest.raises(ValidationError, match=message):
        InputValidator.validate_number(value, MAX)


@pytest.mark.parametrize("text, expected", [
    ("add 2 3", ("add", 2.0, 3.0)),
    ("ADD 2 3", ("add", 2.0, 3.0)),
    ("  power   2   3  ", ("power", 2.0, 3.0)),
    ("root 27 3", ("root", 27.0, 3.0)),
    ("divide -4 2.5", ("divide", -4.0, 2.5)),
    ("unknown 1 2", ("unknown", 1.0, 2.0)),
])
def test_parse_calculation_accepts_valid_input(text, expected):
    assert InputValidator.parse_calculation(text, MAX) == expected


@pytest.mark.parametrize("text", [
    "",
    "add",
    "add 2",
    "add 2 3 4",
])
def test_parse_calculation_rejects_wrong_number_of_parts(text):
    with pytest.raises(ValidationError, match="Use the format"):
        InputValidator.parse_calculation(text, MAX)


@pytest.mark.parametrize("text, message", [
    ("add x 3", "not a valid number"),
    ("add 2 y", "not a valid number"),
    ("add 2 inf", "not a finite number"),
    ("add 2 9999999", "exceeds the maximum"),
])
def test_parse_calculation_rejects_bad_numbers(text, message):
    with pytest.raises(ValidationError, match=message):
        InputValidator.parse_calculation(text, MAX)


def test_parse_calculation_respects_the_max_value_argument():
    with pytest.raises(ValidationError, match="exceeds the maximum"):
        InputValidator.parse_calculation("add 5 5", 3)