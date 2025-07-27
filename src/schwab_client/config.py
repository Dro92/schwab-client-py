"""Module providing general configuration for Schwab API client."""

from dataclasses import dataclass
import os
from typing import Any


class Sensitive:
    """Protects sensitive variables from being accidentally printed."""

    def __init__(self, value: str):
        """Initialize sensitive variables.

        Args:
            value (str): Sensitive variable to protect.

        """
        self._value = value

    def get_sensitive_value(self) -> str:
        """Return sensitive variable.

        Returns:
            str

        """
        return self._value

    def __repr__(self) -> str:
        """Return hidden string if accidentally called.

        Returns:
            str

        """
        return "***SUPPRESSED***" if self._value else "None"

    def __str__(self) -> str:
        """Human friendly string representation.

        Returns:
            str

        """
        return self.__repr__()

    def __eq__(self, other: Any) -> bool:
        """Return boolean comparison.

        Returns:
            bool

        """
        if isinstance(other, Sensitive):
            return self._value == other._value
        return self._value == other


@dataclass(frozen=True)
class Settings:
    """Configuration for Schwab API client.

    Environment Variables:
        - SCHWAB_API_BASE_URL
        - SCHWAB_CLIENT_ID
        - SCHWAB_CLIENT_SECRET
        - SCHWAB_TOKEN_URL

    Examples:
    >>> settings = load_settings()
    >>> print(settings.schwab_client_id)
    'your-actual-client-id'
    >>> print(settings.schwab_client_secret)
    '***SUPPRESSED***'
    >>> print(settings.schwab_client_secret.get_sensitive_value())
    'your-actual-secret'

    """

    schwab_client_id: str
    schwab_client_secret: Sensitive
    schwab_api_base_url: str
    schwab_token_url: str


def load_settings() -> Settings:
    """Load runtime settings."""

    def get_env(name: str) -> str:
        """Import environment variable or raise error if missing.

        Returns:
            str

        Raises:
            RuntimeError

        """
        value = os.getenv(name)
        if value is None:
            raise RuntimeError(f"Missing required environmen variable: {name}")
        return value

    return Settings(
        schwab_client_id=get_env("SCHWAB_CLIENT_ID"),
        schwab_client_secret=Sensitive(get_env("SCHWAB_CLIENT_SECRET")),
        schwab_api_base_url=os.getenv("SCHWAB_API_BASE_URL", "https://api.schwab.com"),
        schwab_token_url=os.getenv(
            "SCHWAB_TOKEN_URL", "https://api.schwabapi.com/v1/oauth/token"
        ),
    )


# Instantiate singleton
settings = load_settings()
