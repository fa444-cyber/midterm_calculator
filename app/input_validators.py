"""Input validation for the calculator."""

import math

from app.exceptions import ValidationError


class InputValidator:
    """Validates and converts raw user input."""

    @staticmethod
    def validate_number(value, max_value):
        """Convert value to a float and check that it is acceptable."""
        try:  # EAFP: just try the conversion
            number = float(value)
        except (TypeError, ValueError):
            raise ValidationError(f"'{value}' is not a valid number")
        # LBYL: float() accepts nan and inf, but we do not
        if not math.isfinite(number):
            raise ValidationError(f"'{value}' is not a finite number")
        if abs(number) > max_value:
            raise ValidationError(
                f"{value} exceeds the maximum allowed value of {max_value}"
            )
        return number

    @staticmethod
    def parse_calculation(text, max_value):
        """Split 'operation a b' into (operation, a, b), validating each part."""
        parts = text.split()
        # LBYL: check the shape of the input before unpacking it
        if len(parts) != 3:
            raise ValidationError(
                "Use the format: <operation> <number> <number> (e.g. add 2 3)"
            )
        operation, raw_a, raw_b = parts
        a = InputValidator.validate_number(raw_a, max_value)
        b = InputValidator.validate_number(raw_b, max_value)
        return operation.lower(), a, b