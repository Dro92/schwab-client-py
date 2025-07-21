"""Module for interacting with the Schwab API Market Hours endpoint."""

from enum import Enum
from typing import Optional, Union

from httpx import Response

from schwab_client.utils import check_enum_value
from schwab_client.protocol import ClientProtocol

# Should this be configured universally with all other endpoints somewhere else?
MARKET_DATA_PATH = "/marketdata/v1"


class Markets:
    """Markets enum class."""

    class MarketType(str, Enum):
        """Market type enum class."""

        BOND = "bond"
        EQUITY = "equity"
        OPTION = "option"
        FUTURE = "future"
        FOREX = "forex"

    class Session(str, Enum):
        """Market session enum class."""

        PRE_MARKET = "preMarket"
        REG_MARKET = "regularMarket"
        POST_MARKET = "postMarket"


class MarketHours:
    """Schwab API endpoint to obtain market hours."""

    def __init__(self, client: ClientProtocol) -> None:
        """Market hours init method."""
        self.client = client

    async def get_market_status(
        self,
        market_id: str = Markets.MarketType.EQUITY,
        date: Optional[Union[str, None]] = None,
    ) -> Response:
        """Get specific market status. Date defaults to today if None provided.

        Args:
            market_id (str): Identification of desired market
            date (str): Desired date in format YYYY-MM-DD

        Returns:
            response: HTTP Response

        """
        params = {}
        if date is not None:
            params["data"] = date
        # Check provided market id is valid
        market_id = check_enum_value(market_id, Markets.MarketType)

        # TODO: Currently the Schwab API only supports the "equity" market_id endpoint.
        #       Remove this in the future if it is corrected in the Schwab API.
        if market_id != Markets.MarketType.EQUITY:
            market_id = Markets.MarketType.EQUITY

        endpoint = "/markets/{}".format(market_id)
        path = MARKET_DATA_PATH + endpoint
        return await self.client._get(path, params)
