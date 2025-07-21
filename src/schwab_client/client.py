"""Module providing a Schwab API client."""

import httpx
from authlib.integrations.base_client.errors import InvalidTokenError, TokenExpiredError  # type: ignore
from typing import Any, Dict

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

    # TODO: Implementing HTTP request methods, but this seems very reapetitive?.
    # Use a wrapper/polymorphic request to handle the logic?
    async def _get(self, path: str, data: dict) -> dict[str, Any]:
        """Send GET request to endpoint."""
        url = settings.SCHWAB_API_BASE_URL + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if expired
        if self.auth.is_token_expired:
            await self.auth.get_token()

        try:
            resp: httpx.Response = await self.auth._client.session.get(
                url=url, params=data
            )
            resp.raise_for_status()
        except (InvalidTokenError, TokenExpiredError):
            await self.auth.get_token()
        return resp.json()

    async def _post(self, path: str, data: dict) -> dict[str, Any]:
        """Send POST request to endpoint."""
        url = settings.SCHWAB_API_BASE_URL + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if expired
        if self.auth.is_token_expired:
            await self.auth.get_token()

        try:
            resp: httpx.Response = await self.auth._client.session.post(
                url=url, params=data
            )
            resp.raise_for_status()
            return resp.json()
        except (InvalidTokenError, TokenExpiredError):
            await self.auth.get_token()
        return resp.json()

    async def _put(self, path: str, data: dict) -> dict[str, Any]:
        """Send PUT request to endpoint."""
        url = settings.SCHWAB_API_BASE_URL + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if expired
        if self.auth.is_token_expired:
            await self.auth.get_token()

        try:
            resp: httpx.Response = await self.auth._client.session.put(
                url=url, params=data
            )
            resp.raise_for_status()
            return resp.json()
        except (InvalidTokenError, TokenExpiredError):
            await self.auth.get_token()
        return resp.json()

    async def _delete(self, path: str, data: dict) -> dict[str, Any]:
        """Send DELETE request to endpoint."""
        url = settings.SCHWAB_API_BASE_URL + path
        # TODO: Add some logging to debug? Need to protect sensitive data

        # Check token and refresh if expired
        if self.auth.is_token_expired:
            await self.auth.get_token()

        try:
            resp: httpx.Response = await self.auth._client.session.delete(
                url=url, params=data
            )
            resp.raise_for_status()
            return resp.json()
        except (InvalidTokenError, TokenExpiredError):
            await self.auth.get_token()
        return resp.json()
