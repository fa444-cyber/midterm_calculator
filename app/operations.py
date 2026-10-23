"""Arithmetic operations (Strategy pattern) and the OperationFactory."""

from abc import ABC, abstractmethod

from app.exceptions import OperationError


class Operation(ABC):
    """Strategy interface: every operation takes two numbers and returns a result."""

    name = ""
    description = ""

    @abstractmethod
    def execute(self, a, b):
        """Compute the result for a and b."""
        pass  # pragma: no cover


class Add(Operation):
    """Addition strategy."""

    name = "add"
    description = "Add two numbers"

    def execute(self, a, b):
        return a + b


class Subtract(Operation):
    """Subtraction strategy."""

    name = "subtract"
    description = "Subtract the second number from the first"

    def execute(self, a, b):
        return a - b


class Multiply(Operation):
    """Multiplication strategy."""

    name = "multiply"
    description = "Multiply two numbers"

    def execute(self, a, b):
        return a * b


class Divide(Operation):
    """Division strategy."""

    name = "divide"
    description = "Divide the first number by the second"

    def execute(self, a, b):
        # LBYL: check for the problem before dividing
        if b == 0:
            raise OperationError("Cannot divide by zero")
        return a / b


class Power(Operation):
    """Exponentiation strategy."""

    name = "power"
    description = "Raise the first number to the power of the second"

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
    description = "Take the root of the first number (the second is the degree)"

    def execute(self, a, b):
        if b == 0:
            raise OperationError("Root degree cannot be zero")
        if a < 0:
            raise OperationError("Cannot take the root of a negative number")
        return a ** (1 / b)


class Modulus(Operation):
    """Modulus strategy: the remainder when a is divided by b."""

    name = "modulus"
    description = "Remainder after dividing the first number by the second"

    def execute(self, a, b):
        # LBYL: the remainder of a division by zero is undefined
        if b == 0:
            raise OperationError("Cannot take the modulus with zero")
        return a % b


class IntegerDivide(Operation):
    """Integer division strategy: a divided by b, rounded down to a whole number."""

    name = "int_divide"
    description = "Divide and round down to a whole number"

    def execute(self, a, b):
        # LBYL: check for the problem before dividing
        if b == 0:
            raise OperationError("Cannot divide by zero")
        return a // b


class Percentage(Operation):
    """Percentage strategy: what percent a is of b, calculated as (a / b) * 100."""

    name = "percent"
    description = "What percent the first number is of the second"

    def execute(self, a, b):
        # LBYL: b is the whole amount, so it cannot be zero
        if b == 0:
            raise OperationError("Cannot calculate a percentage of zero")
        return (a / b) * 100


class AbsoluteDifference(Operation):
    """Absolute difference strategy: the distance between a and b."""

    name = "abs_diff"
    description = "Distance between the two numbers"

    def execute(self, a, b):
        return abs(a - b)


class OperationFactory:
    """Factory that creates Operation objects from the name a user types."""

    _operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntegerDivide,
        "percent": Percentage,
        "abs_diff": AbsoluteDifference,
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

    @classmethod
    def describe_operations(cls):
        """Return (name, description) pairs, so the help menu can list every operation."""
        return [
            (name, operation_class.description)
            for name, operation_class in cls._operations.items()
        ]