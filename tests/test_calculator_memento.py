"""Tests for the Memento pattern (undo and redo)."""

import pandas as pd
import pytest

from app.calculator_memento import Caretaker, Memento
from app.exceptions import CalculatorError


def make_memento(value):
    return Memento(pd.DataFrame({"x": [value]}))


def values(memento):
    return memento.state["x"].tolist()


def test_memento_stores_a_copy_of_the_state():
    frame = pd.DataFrame({"x": [1, 2]})
    memento = Memento(frame)
    frame.loc[0, "x"] = 99
    assert values(memento) == [1, 2]


def test_memento_state_returns_a_copy():
    memento = make_memento(1)
    state = memento.state
    state.loc[0, "x"] = 99
    assert values(memento) == [1]


def test_new_caretaker_has_nothing_to_undo_or_redo():
    caretaker = Caretaker()
    assert caretaker.can_undo is False
    assert caretaker.can_redo is False


def test_save_makes_undo_available():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    assert caretaker.can_undo is True
    assert caretaker.can_redo is False


def test_undo_returns_the_previous_state_and_enables_redo():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    previous = caretaker.undo(make_memento(2))
    assert values(previous) == [1]
    assert caretaker.can_undo is False
    assert caretaker.can_redo is True


def test_redo_returns_the_state_that_was_undone():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    caretaker.undo(make_memento(2))
    restored = caretaker.redo(make_memento(1))
    assert values(restored) == [2]
    assert caretaker.can_undo is True
    assert caretaker.can_redo is False


def test_saving_a_new_state_clears_the_redo_stack():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    caretaker.undo(make_memento(2))
    assert caretaker.can_redo is True
    caretaker.save(make_memento(3))
    assert caretaker.can_redo is False


def test_undo_and_redo_walk_through_the_states_in_order():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    caretaker.save(make_memento(2))
    assert values(caretaker.undo(make_memento(3))) == [2]
    assert values(caretaker.undo(make_memento(2))) == [1]
    assert values(caretaker.redo(make_memento(1))) == [2]
    assert values(caretaker.redo(make_memento(2))) == [3]


def test_undo_with_nothing_saved_raises():
    with pytest.raises(CalculatorError, match="Nothing to undo"):
        Caretaker().undo(make_memento(1))


def test_redo_with_nothing_undone_raises():
    with pytest.raises(CalculatorError, match="Nothing to redo"):
        Caretaker().redo(make_memento(1))


def test_clear_forgets_everything():
    caretaker = Caretaker()
    caretaker.save(make_memento(1))
    caretaker.undo(make_memento(2))
    caretaker.clear()
    assert caretaker.can_undo is False
    assert caretaker.can_redo is False