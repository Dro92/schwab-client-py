"""Module providing a Schwab API client."""

from httpx import Response, AsyncClient
from typing import Any, Dict, Optional

from schwab_client.config import settings
from schwab_client.protocol import ClientProtocol
from schwab_client.auth import SchwabAuthTokenManager
from schwab_client.quotes.quotes import Quotes
from schwab_client.options.options import Options
from schwab_client.market_hours import MarketHours


class SchwabClient(ClientProtocol):
    """Schwab Client."""

    def __init__(
        self,
        auth: SchwabAuthTokenManager,
    ):
        """Initialize Schwab client.

        This package provides a Python client for the Schwab API, including
        modules for authentication, quotes, options, and more.
        """
        self.auth = auth  # Define auth manager
        self.quotes = Quotes(self)
        self.options = Options(self)
        self.market_hours = MarketHours(self)
        self._client = AsyncClient()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Polymorphic request class for HTTP methods."""
        url = settings.schwab_api_base_url + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if necessary
        self.token = await self.auth.get_token()
        # TODO: User callable to update token?

        # Setup request method with session authentication
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "Accept": "application/json",
        }

        try:
            resp = await self._client.request(method, url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception:  # TODO: Improve exception handling for specific auth errors
            # Handle different types of errors based on OAuth2.
            # Would it just be easier here to implement authlib which has them?
            self.token = await self.auth.get_token()  # Bad token, refresh it
        
            # Retry request with updated token
            resp = await self._client.request(method, url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
