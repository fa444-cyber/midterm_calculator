"""Arithmetic operations using the Strategy and Factory design patterns."""

from abc import ABC, abstractmethod

from app.exceptions import OperationError


class Operation(ABC):
    """Strategy interface: every operation knows how to execute itself."""

    name = ""

    @abstractmethod
    def execute(self, a, b):
        """Perform the operation on a and b and return the result."""
        pass  # pragma: no cover


class Add(Operation):
    """Addition strategy."""

    name = "add"

    def execute(self, a, b):
        return a + b


class Subtract(Operation):
    """Subtraction strategy."""

    name = "subtract"

    def execute(self, a, b):
        return a - b


class Multiply(Operation):
    """Multiplication strategy."""

    name = "multiply"

    def execute(self, a, b):
        return a * b


class Divide(Operation):
    """Division strategy."""

    name = "divide"

    def execute(self, a, b):
        # LBYL: check for the problem before dividing
        if b == 0:
            raise OperationError("Cannot divide by zero")
        return a / b


class Power(Operation):
    """Exponentiation strategy."""

    name = "power"

    def execute(self, a, b):
        # LBYL: zero to a negative power is undefined
        if a == 0 and b < 0:
            raise OperationError("Zero cannot be raised to a negative power")
        # EAFP: just try it, and handle the failure if it happens
        try:
            result = a ** b
        except OverflowError:
            raise OperationError("Result is too large to compute")
        if isinstance(result, complex):
            raise OperationError("Result is not a real number")
        return result


class Root(Operation):
    """Root strategy: the b-th root of a."""

    name = "root"

    def execute(self, a, b):
        if b == 0:
            raise OperationError("Root degree cannot be zero")
        if a < 0:
            raise OperationError("Cannot take the root of a negative number")
        return a ** (1 / b)


class OperationFactory:
    """Factory that creates Operation objects from the name a user types."""

    _operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
    }

    @classmethod
    def create_operation(cls, name):
        """Return an instance of the operation matching name."""
        operation_class = cls._operations.get(name.lower())
        if operation_class is None:
            raise OperationError(f"Unknown operation: '{name}'")
        return operation_class()

    @classmethod
    def available_operations(cls):
        """Return the list of supported operation names."""
        return list(cls._operations)