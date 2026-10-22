"""Tests for how the history stores Calculation objects and saves them with pandas."""

import pandas as pd
import pytest

from app.calculation import Calculation
from app.exceptions import CalculatorError
from app.history import COLUMNS, History


def make_history(count=2):
    history = History()
    for number in range(1, count + 1):
        history.add(Calculation("add", number, 1))
    return history


def test_history_stores_calculation_objects():
    history = make_history(2)
    assert all(isinstance(item, Calculation) for item in history.calculations)
    assert [item.a for item in history.calculations] == [1, 2]


def test_calculations_returns_a_copy():
    history = make_history(2)
    history.calculations.clear()
    assert len(history) == 2


def test_to_dataframe_has_the_expected_columns_even_when_empty():
    assert list(History().to_dataframe().columns) == COLUMNS


def test_to_dataframe_has_one_row_per_calculation():
    frame = make_history(3).to_dataframe()
    assert isinstance(frame, pd.DataFrame)
    assert len(frame) == 3


def test_saved_csv_has_the_required_columns(tmp_path):
    path = tmp_path / "history.csv"
    make_history(2).save(path)
    expected = ["operation", "a", "b", "result", "timestamp"]
    assert list(pd.read_csv(path).columns) == expected


def test_load_rebuilds_calculation_objects(tmp_path):
    path = tmp_path / "history.csv"
    original = make_history(3)
    original.save(path)
    loaded = History()
    loaded.load(path)
    assert all(isinstance(item, Calculation) for item in loaded.calculations)
    assert [str(item) for item in loaded.calculations] == [
        str(item) for item in original.calculations
    ]


def test_load_keeps_the_saved_timestamps(tmp_path):
    path = tmp_path / "history.csv"
    original = make_history(2)
    original.save(path)
    loaded = History()
    loaded.load(path)
    assert [item.timestamp for item in loaded.calculations] == [
        item.timestamp for item in original.calculations
    ]


@pytest.mark.parametrize("content, message", [
    ("operation,a,b,result,timestamp\nsqrt,1,2,3,2026-01-01T12:00:00\n", "invalid data"),
    ("operation,a,b,result,timestamp\nadd,1,2,3,yesterday\n", "invalid data"),
    ("operation,a,b,result,timestamp\nadd,x,2,3,2026-01-01T12:00:00\n", "invalid data"),
    ("operation,a,b,result,timestamp\nadd,1,,3,2026-01-01T12:00:00\n", "missing values"),
])
def test_load_rejects_bad_rows(tmp_path, content, message):
    path = tmp_path / "bad.csv"
    path.write_text(content)
    with pytest.raises(CalculatorError, match=message):
        History().load(path)


def test_history_uses_the_given_encoding(tmp_path):
    path = tmp_path / "history.csv"
    history = History(encoding="utf-16")
    history.add(Calculation("add", 1, 2))
    history.save(path)
    assert path.read_bytes().startswith((b"\xff\xfe", b"\xfe\xff"))
    loaded = History(encoding="utf-16")
    loaded.load(path)
    assert len(loaded) == 1


def test_loading_with_the_wrong_encoding_is_reported(tmp_path):
    path = tmp_path / "history.csv"
    history = History(encoding="utf-16")
    history.add(Calculation("add", 1, 2))
    history.save(path)
    with pytest.raises(CalculatorError, match="Could not read history file"):
        History(encoding="utf-8").load(path)