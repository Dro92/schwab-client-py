"""Module for interacting with the Schwab Options endpoint."""

from enum import Enum

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
        pass

    async def get_quote(self, ticker: str, fields: list[str | Enum] = None) -> Response:
        """Single symbol get quote.

        Args:
            ticker (str)): Publicly listed ticker symbol. Ex. AAPL
            fields (list(str | Enum)): Request subsets of data. By default, none will return all.
        
        Returns:
            HTTP Response 

        Examples:
            >>> quotes.get_quote("AAPL")
            <Response [200]>
            
        """
        params = {}
        ticker = normalize_ticker(ticker)
   
        fields = validate_enums_iterable(fields, QuoteFields)
        if fields:
            params["fields"] = ",".join(fields)

        path = MARKET_DATA_PATH + "/{}/quotes".format(ticker)
        return await self.client._get(path, params)
    
    async def get_quotes(
        self, tickers: list[str], fields: list[str | Enum] = None
    ) -> Response:
        """Get quote for a list of symbols.

        Args:
            tickers (list(str)): Comma separated string of symbol(s) to look up ticker symbol.
            fields (list(str | Enum)): Request subsets of data. By default, none will return all.

        Returns:
            HTTP Response

        Examples:
            >>> quotes.get_quotes(["AAPL", "GOOG"])
            <Response [200]>

        """
        params = {}

        # Normalize list of tickers to proper format
        tickers = [normalize_ticker(t) for t in tickers]

        fields = validate_enums_iterable(fields, QuoteFields)
        if fields:
            params["fields"] = ",".join(fields)

        # TODO: Should catch an error if list entries are not strings?
        if isinstance(tickers, list):
            params["symbols"] = tickers

        path = MARKET_DATA_PATH + "/quotes"
        return await self.client._get(path, params)