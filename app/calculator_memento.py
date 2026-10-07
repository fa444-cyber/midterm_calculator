"""Memento pattern: save and restore calculator state for undo and redo."""

from app.exceptions import CalculatorError


class Memento:
    """A snapshot of the calculator history at one moment in time."""

    def __init__(self, state):
        self._state = state.copy()

    @property
    def state(self):
        """Return a copy of the saved state."""
        return self._state.copy()


class Caretaker:
    """Manages the undo and redo stacks of mementos."""

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    @property
    def can_undo(self):
        """True when there is something to undo."""
        return bool(self._undo_stack)

    @property
    def can_redo(self):
        """True when there is something to redo."""
        return bool(self._redo_stack)

    def save(self, memento):
        """Record a new state. A fresh change invalidates the redo stack."""
        self._undo_stack.append(memento)
        self._redo_stack.clear()

    def undo(self, current):
        """Return the previous state, remembering current for redo."""
        # LBYL: check that there is something to undo first
        if not self._undo_stack:
            raise CalculatorError("Nothing to undo")
        self._redo_stack.append(current)
        return self._undo_stack.pop()

    def redo(self, current):
        """Return the next state, remembering current for undo."""
        # LBYL: check that there is something to redo first
        if not self._redo_stack:
            raise CalculatorError("Nothing to redo")
        self._undo_stack.append(current)
        return self._redo_stack.pop()

    def clear(self):
        """Forget all saved states."""
        self._undo_stack.clear()
        self._redo_stack.clear()