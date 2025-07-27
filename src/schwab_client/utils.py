"""Module provides helper functions."""

from enum import Enum
from typing import Type, TypedDict, TypeVar, Union, Optional, Iterable
import re

E = TypeVar("E", bound=Enum)  # Provides mypy proper Enum member typing


class OAuth2Token(TypedDict, total=False):
    """OAuth2 token template."""

    access_token: str
    refresh_token: str
    expires_in: int
    id_token: str
    expires_at: float
    token_type: str
    scope: str

def normalize_ticker(ticker: str) -> str:
    """Normalize a ticker and validate its format.

    Args:
        ticker (str): Company publicly listed ticker symbol.
    
    Returns:
        str: Noramlized ticker in all caps.

    Raises:
        ValueError: If ticker contains invalid characters.
    
    """
    normalized = ticker.upper()
    # if not normalized.isalnum():
    allowed_symbols = r"^[A-Za-z0-9./\s$_-]+$"
    if not re.fullmatch(allowed_symbols, normalized):
        raise ValueError(
            f"{ticker} contains invalid characters. "
            "Only alphanumeric, dot, slash, space, $, - or _ are allowed."
        )
    return normalized

def check_enum_value(field: Union[str, Enum], enum_cls: Type[Enum]) -> str:
    """Return the enum value based on string or Enum member.

    Args:
        field: A string or Enum member.
        enum_cls: Enum class to validate against.

    Returns:
        The string value of the enum member.

    Raises:
        ValueError: If field is not a valid enum member or value.

    """
    if isinstance(field, enum_cls):
        return field.value
    elif isinstance(field, str):
        if field in {member.value for member in enum_cls}:
            return field
        raise ValueError(
            f"'{field}' is not a valid value of {enum_cls.__name__}. "
            f"Expected one of: {[m.value for m in enum_cls]}"
        )
    raise ValueError(
        f"'{field}' is neither a string nor a member of {enum_cls.__name__}."
    )

def validate_enums_iterable(
    iterable: Optional[Iterable[Union[str, Enum]]],
    enum_cls: Type[Enum]
) -> list[str]:
    """Validate that provided values are part of an enum class.

    Args:
        iterable: List of strings or Enum members.
        enum_cls: Enum class to validate against.

    Returns:
        List of validated enum string values.

    Raises:
        ValueError: If any element is not a valid enum value/member.
        
    """
    if iterable is None:
        return []

    return [check_enum_value(val, enum_cls) for val in iterable]