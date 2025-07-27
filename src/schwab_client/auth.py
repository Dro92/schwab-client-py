"""Module providing basic access token refresh logic for Schwab API client."""

import asyncio
import time
from enum import Enum
from contextlib import AbstractAsyncContextManager
import base64
from abc import ABC, abstractmethod

import httpx

from typing import Optional, Awaitable, Callable

from schwab_client.config import settings
from schwab_client.utils import OAuth2Token

# Schwab OAuth2 Overview
# https://developer.schwab.com/products/trader-api--individual/details/documentation/Retail%20Trader%20API%20Production
#
# Access Token:
# To enhance API security, used in place of username+password combination and
# is valid for 30 minutes after creation.

# Bearer Token:
# A Bearer token is the Access Token in the context of an API call for Protected Resource data.
# It is passed in the Authorization header as "Bearer {access_token_value}."

# Refresh Token:
# Renews access to a User's Protected Resources. This may be done before, or at
# any point after the current, valid access_token expires. When they do expire,
# the corresponding Refresh Token is used to request a new Access Token as opposed
# to repeating the entire Flow. This token should be stored for later use and is
# valid for 7 days after creation.
#
# Upon expiration, a new set refresh token must be recreated using the authorization_code Grant Type authentication flow (CAG/LMS).


class Token(str, Enum):
    """Token enumeration."""

    EXPIRES_IN = "expires_in"
    EXPIRES_AT = "expires_at"
    REFRESH_TOKEN = "refresh_token"
    ACCESS_TOKEN = "access_token"


class TokenStorageProtocol(ABC):
    """Token storage protocl for the user to implement."""

    @abstractmethod
    async def read_token(
        self, client: Callable[..., Awaitable[None]]
    ) -> Optional[OAuth2Token]:
        """Read a token from somewhere."""
        raise NotImplementedError

    @abstractmethod
    async def write_token(
        self, client: Callable[..., Awaitable[None]], data: OAuth2Token
    ) -> None:
        """Write a token somewhere."""
        raise NotImplementedError


class LockProtocol(ABC):
    """Lock protocol for the user to implement."""

    @abstractmethod
    def __call__(
        self, client: Callable[..., Awaitable[None]], timeout: int = 3
    ) -> AbstractAsyncContextManager[bool]:
        """Type hint call to Lock."""
        raise NotImplementedError


class SchwabAuthTokenManager(ABC):
    """Schwab OAuth2 access token refresher.

    This class only refreshes access tokens utilizing a valid refresh token.
    """

    def __init__(
        self,
        db_client: Callable[..., Awaitable[None]],
        db_lock: LockProtocol,
        token_storage: TokenStorageProtocol,
        client_id: str = settings.schwab_client_id,
        client_secret: str = settings.schwab_client_secret.get_sensitive_value(),
        refresh_url: str = settings.schwab_token_url,
    ):
        """Initialize Schwab authentication manager."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_url = refresh_url
        self.db_client = db_client
        self.token_storage = token_storage
        self.lock = db_lock

    async def is_token_expired(self, buffer: int = 0) -> bool:
        """Check if token has expired.

        Args:
            buffer (int): Seconds left before access token expires.

        Returns:
            bool

        """
        token = await self.token_storage.read_token(self.db_client)

        if not token:
            return True

        expires_at = token.get(Token.EXPIRES_AT)

        if not isinstance(expires_at, (int, float)):  # Verify not malformed
            return True
        
        return not expires_at or time.time() >= (expires_at - buffer)

    async def _refresh_token(self, refresh_token: str) -> OAuth2Token:
        """Refresh the access token using a valid refresh token.

        Args:
            refresh_token (str): Valid refresh token for Schwab

        Returns:
            dict: OAuth2Token formatted dict

        """
        # Build payload request type
        payload = {
            "grant_type": Token.REFRESH_TOKEN.value,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        # Base64 encode the basic auth
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Authorization": f"Basic {auth_b64}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.refresh_url, data=payload, headers=headers
            )
            response.raise_for_status()
            return response.json()  # type: ignore[return-value]
        
    async def _retry_get_valid_token(
        self,
        attempts: int = 3,
        delay: float = 1.0
    ) -> OAuth2Token:
        """Retry getting a valid token from database.

        Returns:
            dict: OAuth2Token dictionary

        Raises:
            RuntimeError: If failed to obtain a valid token.

        """
        for _ in range(attempts):
            await asyncio.sleep(delay)  # Wait before re-checking
            token_data = await self.token_storage.read_token(self.db_client)

            if not token_data:
                continue

            if token_data and not await self.is_token_expired():  # Check if new token is valid
                self._token = token_data  # Update internal token state
                return token_data
        
        raise RuntimeError("Failed to get a valid token.")


    async def get_token(self, buffer: int = 60, lock_attempts: int = 3) -> OAuth2Token:
        """Get a valid token.

        Returns:
            dict: OAuth2Token dictionary

        Raises:
            ValueError: If no token is found in the database.

        """
        token_data = await self.token_storage.read_token(self.db_client)

        if not token_data:
            raise ValueError("Token not found.")
        
        if token_data and not await self.is_token_expired(buffer):
            # TODO: Need to add error handling here.
            self._token = token_data  # Update internal token state
            return token_data

        # Get lock before updating token
        async with self.lock(self.db_client) as acquired:
            if acquired:
                refreshed_token = await self._refresh_token(
                    token_data[Token.REFRESH_TOKEN.value]
                )
                self._token = token_data  # Update internal token state
                await self.token_storage.write_token(
                    self.db_client, refreshed_token
                )  # Write updated token to database
                return refreshed_token

            # Another client may be updating the token, retry
            return await self._retry_get_valid_token(lock_attempts)

