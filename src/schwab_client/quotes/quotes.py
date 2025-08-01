"""Module for interacting with the Schwab quotes endpoint."""

from enum import Enum
from typing import Any, Iterable, Optional, Union
from urllib.parse import quote

from httpx import Response

from schwab_client.protocol import ClientProtocol
from schwab_client.utils import (
    normalize_ticker,
    validate_enums_iterable,
)
from schwab_client.config import settings

# Define market data path
MARKET_DATA_PATH = settings.schwab_market_data_path


class QuoteFields(str, Enum):
    """Quote field types."""

    QUOTE = "quote"
    FUNDAMENTAL = "fundamental"
    EXTENDED = "extended"
    REFERENCE = "reference"
    REGULAR = "regular"


class Quotes:
    """Schwab API equities stock quotes class."""

    def __init__(self, client: ClientProtocol) -> None:
        """Quotes init method."""
        self.client = client

    async def get_quotes(
        self,
        tickers: Union[str, list[str]],
        fields: Optional[Iterable[Union[str, Enum]]] = None,
    ) -> Response:
        """Get quote for the provided ticker symbols of symbols.

        Args:
            tickers (str or list[str]): Single or list of ticker symbols.
            fields (list(str | Enum)): Request subsets of data. By default, none will return all.

        Returns:
            HTTP Response

        Raises:
            TypeError: If tickers is neither str nor list of str.

        Examples:
            >>> quotes.get_quotes("BRK/B")
            <Response [200]>
            >>> quotes.get_quotes(["AAPL", "GOOG"])
            <Response [200]>

        """
        params: dict[str, Any] = {}  # Initialize parameters

        # Check fields first
        validated_fields = validate_enums_iterable(QuoteFields, fields)
        if fields:
            params["fields"] = ",".join(validated_fields)

        # Check whether single ticker was given and use proper endpoint
        if isinstance(tickers, str):
            ticker_normalized = normalize_ticker(tickers)
            # Encode ticker so / is not reated as a subpath
            ticker_encoded = quote(ticker_normalized, safe="")
            path = MARKET_DATA_PATH + "/{}/quotes".format(ticker_encoded)
        # Check whether list of tickers was given and use proper endpoint
        elif isinstance(tickers, list):
            tickers_normalized = [normalize_ticker(t) for t in tickers]
            params["symbols"] = tickers_normalized
            path = MARKET_DATA_PATH + "/quotes"
        else:
            raise TypeError(f"{tickers} must be either str or list of str.")

        return await self.client._get(path, params)
