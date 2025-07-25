"""Module for implementing HTTP protocol methods."""

from typing import Protocol, Any, Optional, Dict
from httpx import Response


class ClientProtocol(Protocol):
    """Module implementing custom HTTP protocol methods."""

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Polymorphic request class for HTTP methods."""

    async def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
    ) -> Response:
        """Send GET request to endpoint."""
        return await self._request("GET", path, params=params)

    async def _post(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
    ) -> Response:
        """Send POST request to endpoint."""
        return await self._request("POST", path, params=params)

    async def _put(self, path: str, params: Optional[Dict[str, Any]]) -> Response:
        """Send PUT request to endpoint."""
        return await self._request("PUT", path, params=params)

    async def _delete(self, path: str, params: Optional[Dict[str, Any]]) -> Response:
        """Send DELETE request to endpoint."""
        return await self._request("DELETE", path, params=params)


# TODO: Consider adding a runtime class with abstract methods?
