"""Tests for the history (pandas and CSV) and the observers."""

import logging

import pytest

from app.calculation import Calculation
from app.exceptions import CalculatorError
from app.history import AutoSaveObserver, History, LoggingObserver, Observer


def make_history(count=2):
    history = History()
    for number in range(1, count + 1):
        history.add(Calculation("add", number, 1))
    return history


def test_new_history_is_empty():
    assert len(History()) == 0


@pytest.mark.parametrize("count", [1, 2, 5])
def test_add_grows_the_history(count):
    assert len(make_history(count)) == count


def test_add_records_the_calculation_details():
    history = History()
    history.add(Calculation("add", 2, 3))
    row = history.to_dataframe().iloc[0]
    assert row["operation"] == "add"
    assert row["a"] == 2
    assert row["b"] == 3
    assert row["result"] == 5


@pytest.mark.parametrize("max_size, added, expected", [
    (2, 3, [2, 3]),
    (3, 3, [1, 2, 3]),
    (1, 4, [4]),
])
def test_history_keeps_only_the_newest_rows(max_size, added, expected):
    history = History(max_size=max_size)
    for number in range(1, added + 1):
        history.add(Calculation("add", number, 1))
    assert history.to_dataframe()["a"].tolist() == expected


def test_clear_empties_the_history():
    history = make_history(3)
    history.clear()
    assert len(history) == 0


def test_to_dataframe_returns_a_copy():
    history = make_history(1)
    frame = history.to_dataframe()
    frame.loc[0, "a"] = 99
    assert history.to_dataframe()["a"].tolist() == [1]


def test_display_of_an_empty_history():
    assert History().display() == "No calculations yet."


def test_display_shows_the_calculations():
    text = make_history(2).display()
    assert "operation" in text
    assert "add" in text


def test_snapshot_is_a_copy():
    history = make_history(1)
    snapshot = history.snapshot()
    snapshot.clear()
    assert len(history) == 1


def test_restore_replaces_the_history():
    history = make_history(1)
    snapshot = history.snapshot()
    history.add(Calculation("add", 5, 5))
    history.restore(snapshot)
    assert len(history) == 1


def test_save_and_load_round_trip(tmp_path):
    path = tmp_path / "nested" / "history.csv"
    make_history(3).save(path)
    loaded = History()
    loaded.load(path)
    assert len(loaded) == 3
    assert loaded.to_dataframe()["a"].tolist() == [1, 2, 3]
    assert loaded.to_dataframe()["result"].tolist() == [2, 3, 4]


def test_load_applies_the_size_limit(tmp_path):
    path = tmp_path / "history.csv"
    make_history(3).save(path)
    small = History(max_size=2)
    small.load(path)
    assert small.to_dataframe()["a"].tolist() == [2, 3]


def test_save_reports_files_it_cannot_write(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("not a folder")
    with pytest.raises(CalculatorError, match="Could not save history"):
        make_history(1).save(blocker / "history.csv")


def test_load_reports_a_missing_file(tmp_path):
    with pytest.raises(CalculatorError, match="not found"):
        History().load(tmp_path / "missing.csv")


@pytest.mark.parametrize("content", [
    "",
    "operation,a\n1,2\n1,2,3,4,5\n",
])
def test_load_reports_unreadable_files(tmp_path, content):
    path = tmp_path / "bad.csv"
    path.write_text(content)
    with pytest.raises(CalculatorError, match="Could not read history file"):
        History().load(path)


def test_load_rejects_unexpected_columns(tmp_path):
    path = tmp_path / "wrong.csv"
    path.write_text("x,y\n1,2\n")
    with pytest.raises(CalculatorError, match="unexpected columns"):
        History().load(path)


def test_observer_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        Observer()


def test_logging_observer_writes_to_the_log(caplog):
    with caplog.at_level(logging.INFO, logger="calculator"):
        LoggingObserver().update(Calculation("add", 2, 3))
    assert "Calculation performed: add(2, 3) = 5" in caplog.messages


def test_auto_save_observer_saves_the_history(tmp_path):
    path = tmp_path / "auto.csv"
    AutoSaveObserver(make_history(2), path).update(Calculation("add", 9, 9))
    assert path.exists()


def test_auto_save_observer_is_an_observer(tmp_path):
    assert isinstance(AutoSaveObserver(History(), tmp_path / "x.csv"), Observer)