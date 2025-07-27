"""Module providing basic access token refresh logic for Schwab API client."""

import asyncio
import time
from enum import Enum
from contextlib import AbstractAsyncContextManager
import base64

import httpx

from typing import Any, TypedDict, Optional, Awaitable, Protocol, Callable

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

class OAuth2Token(TypedDict, total=False):
    """OAuth2 token template."""

    access_token: str
    refresh_token: str
    expires_in: int
    id_token: str
    expires_at: float
    token_type: str
    scope: str

class TokenStorageProtocol(Protocol):
    """Token storage protocl for the user to implement."""

    async def read_token(self) -> Optional[dict]:
        """Read a token from somewhere."""
        ...

    async def write_token(self, data: dict) -> None: 
        """Write a token somewhere."""
        ...

class LockProtocol(Protocol):
    """Lock protocol for the user to implement."""

    def __call__(self) -> AbstractAsyncContextManager[bool]:
        """Type hint call to Lock."""
        ...


class SchwabAuth:
    """Schwab OAuth2 access token refresher.

    This class only refreshes access tokens utilizing a valid refresh token.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_url: str,
        db_client: Callable[..., Awaitable[None]],
        db_read_token: Callable[[], Awaitable[Optional[OAuth2Token]]],
        db_write_token: Callable[[OAuth2Token], Awaitable[None]],
        db_lock: Callable[[], AbstractAsyncContextManager[bool]]
    ):
        """Initialize Schwab authentication manager."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_url = refresh_url
        self._refresh_lock = asyncio.Lock()  # Coroutine lock safety
        self.lock = db_lock
        self.read_token = db_read_token
        self.write_token = db_write_token
        self.db_client = db_client

    async def is_token_expired(self, buffer: int = 0) -> bool:
        """Check if token has expired.

        Args:
            buffer (int): Seconds left before access token expires.

        Returns:
            bool

        """
        token = await self.read_token(self.db_client)

        if not token:
            return True
        
        expires_at = token.get(Token.EXPIRES_AT)
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
            'grant_type': Token.REFRESH_TOKEN.value,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token
        }
        # Base64 encode the basic auth
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_str.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Authorization": f"Basic {auth_b64}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.refresh_url, data=payload, headers=headers)
            response.raise_for_status()
            return response.json()  # type: ignore[return-value]
    
    async def get_token(self, buffer: int = 60, lock_attempts: int = 3) -> OAuth2Token:
        """Get a valid token from Schwab.

        Returns:
            dict: OAuth2Token dictionary

        """
        token_data = await self.read_token(self.db_client)

        if not await self.is_token_expired(60):
            # TODO: Need to add error handling here.
            self._token = token_data  # Update internal token state
            return token_data

        # Get lock before updating token
        async with self.lock(self.db_client) as acquired:
            if acquired:
                token_data = await self.read_token(self.db_client)  # Re-sync latest

                # Refresh access token
                refreshed_token = await self._refresh_token(token_data[Token.REFRESH_TOKEN])
                self._token = token_data  # Update internal token state
                await self.write_token(self.db_client, refreshed_token)  # Write updated token to database
                return refreshed_token

            # Assume another client is updating the token
            for _ in range(lock_attempts):
                await asyncio.sleep(1)  # Wait a second before re-checking
                token_data = await self.read_token(self.db_client)
                if not await self.is_token_expired():  # Check if new token is valid
                    self._token = token_data  # Update internal token state
                    return token_data
                    
            raise RuntimeError("Failed to get a valid token.")
        

    # TODO: Need to have a check for the refresh token to notify user
    # Must include a timestamp or some sort of check for the refresh token.
