"""Module providing a Schwab API client."""

from httpx import Response
from authlib.integrations.base_client.errors import InvalidTokenError, TokenExpiredError  # type: ignore
from typing import Any, Callable, Dict, Optional

from schwab_client.config import settings
from schwab_client.protocol import ClientProtocol
from schwab_client.auth import SchwabAuth
from schwab_client.quotes.quotes import Quotes
from schwab_client.options.options import Options
from schwab_client.market_hours import MarketHours


class SchwabClient(ClientProtocol):
    """Schwab Client."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_url: str,
        token: Dict[str, Any],
        token_updater: Callable,  # TODO: User definable?
    ):
        """Initialize Schwab client.

        This package provides a Python client for the Schwab API, including
        modules for authentication, quotes, options, and more.
        """
        # Define enndpoints
        self.auth = SchwabAuth(client_id, client_secret, token, refresh_url)
        self.quotes = Quotes(self)
        self.options = Options(self)
        self.market_hours = MarketHours(self)
        self.token_updater = token_updater
        return

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Polymorphic request class for HTTP methods."""
        url = settings.SCHWAB_API_BASE_URL + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if necessary
        self.token = await self.auth.get_token()
        # TODO: User callable to update token?

        # Setup request method with session authentication
        request_method = getattr(self.auth._client.session, method.lower())

        try:
            resp: Response = await request_method(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except (InvalidTokenError, TokenExpiredError):
            # Bad token, refresh it
            self.token = await self.auth.get_token()
            # TODO: User callable to update token?

            # Retry request with updated token
            resp = await request_method(url, params=params)
            resp.raise_for_status()
            return resp.json()
