"""
输入参数校验
"""

from typing import Any


class ValidationError(Exception):
    pass


def validate_input(schema: dict[str, Any], params: dict[str, Any]) -> None:
    for name, spec in schema.items():
        required = spec.get("required")
        value = params.get(name)

        if isinstance(required, dict) and required.get("type") == "conditional":
            when = required.get("when", {})
            field_name = when.get("field")
            operator = when.get("operator")
            expected = when.get("value")
            if operator == "equals" and params.get(field_name) == expected and value is None:
                raise ValidationError(f"conditional required field missing: {name}")
            continue

        if required and value is None:
            raise ValidationError(f"required field missing: {name}")

        if value is None:
            continue

        if spec.get("type") == "enum" and value not in spec.get("options", []):
            raise ValidationError(f"invalid enum value for {name}: {value}")

        if spec.get("type") == "number":
            minimum = spec.get("minimum")
            maximum = spec.get("maximum")
            if minimum is not None and value < minimum:
                raise ValidationError(f"{name} below minimum {minimum}: {value}")
            if maximum is not None and value > maximum:
                params[name] = maximum

        if spec.get("type") == "array" and not isinstance(value, list):
            raise ValidationError(f"{name} must be an array")
