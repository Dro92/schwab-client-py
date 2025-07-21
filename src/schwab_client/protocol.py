"""Module for implementing HTTP protocol methods."""

from typing import Protocol, Any, runtime_checkable


@runtime_checkable
class ClientProtocol(Protocol):
    """Module implementing custom HTTP protocol methods."""

    # Define custom CRUD to modify URL path based on desired function
    async def _get(self, path: str, data: dict) -> dict[str, Any]:
        """Send GET request to endpoint."""

    async def _post(self, path: str, data: dict) -> dict[str, Any]:
        """Send POST request to endpoint."""

    async def _put(self, path: str, data: dict) -> dict[str, Any]:
        """Send PUT request to endpoint."""

    async def _delete(self, path: str, data: dict) -> dict[str, Any]:
        """Send DELETE request to endpoint."""


# TODO: Consider adding a runtime class with abstract methods?
