"""Module providing a Schwab API client."""

from schwabpy_api.auth import SchwabAuth
from schwabpy_api.quotes.endpoint import Quotes
from schwabpy_api.options.endpoint import Options


class MarketHours:
    """Schwab API endpoint to obtain market hours."""

    pass


class SchwabClient:
    """Schwab Client."""

    def __init__(self,):
        """Initialize Schwab client.
        
        This package provides a Python client for the Schwab API, including
        modules for authentication, quotes, options, and more.
        """
        # Define enndpoints
        self.auth = SchwabAuth()
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
