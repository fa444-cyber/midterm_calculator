"""A single calculation record."""

from datetime import datetime

from app.operations import OperationFactory


class Calculation:
    """One executed operation: its inputs, its result, and when it ran."""

    def __init__(self, operation_name, a, b, precision=None, timestamp=None):
        self.operation_name = operation_name
        self.a = a
        self.b = b
        self.timestamp = timestamp or datetime.now()
        operation = OperationFactory.create_operation(operation_name)
        result = operation.execute(a, b)
        self.result = round(result, precision) if precision is not None else result

    def to_dict(self):
        """Return the calculation as a dictionary (one row of the history)."""
        return {
            "operation": self.operation_name,
            "a": self.a,
            "b": self.b,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, row):
        """Rebuild a calculation from one history row (the reverse of to_dict)."""
        calculation = cls(
            row["operation"],
            row["a"],
            row["b"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
        )
        # Keep the result that was saved, so rounding is not applied twice
        calculation.result = row["result"]
        return calculation

    def __str__(self):
        return f"{self.operation_name}({self.a}, {self.b}) = {self.result}"