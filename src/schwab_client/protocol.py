"""Module for implementing HTTP protocol methods."""

from typing import Protocol, Any, Optional, Dict, runtime_checkable


@runtime_checkable
class ClientProtocol(Protocol):
    """Module implementing custom HTTP protocol methods."""

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Polymorphic request class for HTTP methods."""

    async def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
    ) -> dict[str, Any]:
        """Send GET request to endpoint."""

    async def _post(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
    ) -> dict[str, Any]:
        """Send POST request to endpoint."""

    async def _put(self, path: str, params: Optional[Dict[str, Any]]) -> dict[str, Any]:
        """Send PUT request to endpoint."""

    async def _delete(
        self, path: str, params: Optional[Dict[str, Any]]
    ) -> dict[str, Any]:
        """Send DELETE request to endpoint."""


# TODO: Consider adding a runtime class with abstract methods?
