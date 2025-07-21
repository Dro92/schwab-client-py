"""Module providing general configuration for Schwab API client."""

import os


class Settings:
    """Configuration for Schwab API client."""

    SCHWAB_API_BASE_URL: str = os.getenv(
        "SCHWAB_API_BASE_URL", "https://api.schwab.com"
    )
    SCHWAB_CLIENT_ID: str | None = os.environ.get("SCHWAB_CLIENT_ID")
    # Note this variable is sensitive - DO NOT LOG IT
    SCHWAB_CLIENT_SECRET: str | None = os.environ.get("SCHWAB_CLIENT_SECRET")


# Instantiate singleton
settings = Settings()
