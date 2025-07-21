"""Module provides helper functions."""

from enum import Enum
from typing import Type, TypeVar

E = TypeVar("E", bound=Enum)  # Provides mypy proper Enum member typing


def check_enum_value(field: str, enum_cls: Type[E]) -> str:
    """Return the enum value given a string.

    Args:
        field (str | Enum): Either a string or Enum member.
        enum_cls (EnumMeta): Enum class to validate against.

    Returns:
        str: The corresponding enum value as a string.

    Raises:
        ValueError: If the input is not valid.

    """
    # Give user flexibility in input text format
    normalized_field = field.lower()
    valid_values = []

    for member in enum_cls:
        valid_values.append(member.value)
        if normalized_field == member.value:
            return member.value  # Return proper value always

    raise ValueError(
        f"{field!r} is not a valid name or value of enum {enum_cls.__name__}. "
        f"Valid values: {valid_values}"
    )
