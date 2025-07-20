"""Module providing a Schwab API client."""

from typing import Any, Dict

from schwabpy_api.auth import SchwabAuth
from schwabpy_api.quotes.quotes import Quotes
from schwabpy_api.options.options import Options
from schwabpy_api.market_hours import MarketHours


class SchwabClient:
    """Schwab Client."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token: Dict[str, Any],
        refresh_url: str,
    ):
        """Initialize Schwab client.

        This package provides a Python client for the Schwab API, including
        modules for authentication, quotes, options, and more.
        """
        # Define enndpoints
        self.auth = SchwabAuth(client_id, client_secret, token, refresh_url)
        self.quotes = Quotes()
        self.options = Options()
        self.market_hours = MarketHours()
        return

    def is_market_open(
        self,
    ) -> bool:
        """Check market status.

        Returns:
            bool: Market status

        """
        return
