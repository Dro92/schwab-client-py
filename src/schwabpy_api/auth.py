"""Module providing basic access token refresh logic for Schwab API client."""
import time
from enum import Enum

from authlib.integrations.httpx_client import AsyncOAuth2Client

from typing import Any, Dict

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



class SchwabAuth:
    """Schwab OAuth2 access token refresher.
    
    This class only refreshes access tokens utilizing a valid refresh token.
    """
    
    def __init__(self,
        client_id: str,
        client_secret: str,
        token: Dict[str, Any],
        refresh_url: str,
    ):
        """Initialize Schwab authentication manager."""
        self._client = AsyncOAuth2Client(
            client_id = client_id,
            client_secret = client_secret,
            token=token
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.refresh_url = refresh_url  

    @property
    def is_token_expired(self,) -> bool:
        """Check if token has expired.
        
        Returns:
            bool

        """
        expires_at = self.token.get(Token.EXPIRES_AT)
        return not expires_at or time.time() >= expires_at
    
    @property
    def is_token_expiring_soon(self, buffer: int = 180) -> bool:
        """Check if token expires soon.
        
        Args:
            buffer (int): Seconds left before access token expires.

        Returns:
            bool

        """
        expires_at = self.token.get(Token.EXPIRES_AT)
        return not expires_at or time.time() >= (expires_at - buffer)
    
    async def get_valid_token(self) -> str:
        """Get a valid token from Schwab.
        
        Returns:
            str: Access Token

        """
        await self.ensure_token_valid()
        return self._client.token[Token.ACCESS_TOKEN]

    async def ensure_token_valid(self) -> None:
        """Check if current token is valid and refresh."""
        if self._token_is_expired():
            await self._client.refresh_token(self.refresh_url)

    # TODO: Need to have a check for the refresh token to notify user
    # Must include a timestamp or some sort of check for the refresh token.