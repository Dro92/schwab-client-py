"""Module for interacting with the Schwab Options endpoint."""

from enum import Enum
from typing import Any, Optional
from httpx import Response

from schwab_client.protocol import ClientProtocol
from schwab_client.utils import normalize_ticker, resolve_enum
from schwab_client.config import settings

MARKET_DATA_PATH = settings.schwab_market_data_path


class OptionNamespace:
    """Namespace for option-related enums."""

    class ContractType(str, Enum):
        """Namespace for contract types."""

        CALL = "CALL"
        PUT = "PUT"
        ALL = "ALL"

    class Strategy(str, Enum):
        """Namespace for strategies."""

        SINGLE = "SINGLE"
        ANALYTICAL = "ANALYTICAL"
        COVERED = "COVERED"
        VERTICAL = "VERTICAL"
        CALENDAR = "CALENDAR"
        STRANGLE = "STRANGLE"
        STRADDLE = "STRADDLE"
        BUTTERFLY = "BUTTERFLY"
        CONDOR = "CONDOR"
        DIAGONAL = "DIAGONAL"
        COLLAR = "COLLAR"
        ROLL = "ROLL"

    class ExpMonth(str, Enum):
        """Namespace for months."""

        JAN = "JAN"
        FEB = "FEB"
        MAR = "MAR"
        APR = "APR"
        MAY = "MAY"
        JUN = "JUN"
        JUL = "JUL"
        AUG = "AUG"
        SEP = "SEP"
        OCT = "OCT"
        NOV = "NOV"
        DEC = "DEC"
        ALL = "ALL"

    class Entitlement(str, Enum):
        """Namespace for entitlements."""

        PN = "PN"  # NonPayingPro
        NP = "NP"  # NonPro
        PP = "PP"  # PayingPro

    class Type(str, Enum):
        """Namespace for option types."""

        ALL = "ALL"
        STANDARD = "S"
        NON_STANDARD = "NS"

    class Moneyness(str, Enum):
        """Namespace for option moneyness.

        Rather than using the word range we use moneyness here to avoid issues.
        """

        ALL = "ALL"
        IN_THE_MONEY = "ITM"
        NEAR_THE_MONEY = "NTM"
        OUT_OF_THE_MONEY = "OTM"
        STRIKE_ABOVE_MARKET = "SAK"
        STRIKE_NEAR_MARKET = "SNK"
        STRIKE_BELOW_MARKET = "SBK"


class Options:
    """Schwab API equity options endpoint class."""

    def __init__(self, client: ClientProtocol) -> None:
        """Options init method."""
        self.client = client

    async def get_chain(
        self,
        symbol: str,
        *,
        contract_type: Optional[OptionNamespace.ContractType] = None,
        strike_count: Optional[int] = None,
        include_underlying_quote: Optional[bool] = None,
        strategy: Optional[OptionNamespace.Strategy] = None,
        interval: Optional[float] = None,
        strike: Optional[float] = None,
        option_range: Optional[
            str
        ] = None,  # "moneyness" - do not use range for attribute name
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        volatility: Optional[float] = None,
        underlying_price: Optional[float] = None,
        interest_rate: Optional[float] = None,
        days_to_expiration: Optional[int] = None,
        exp_month: Optional[OptionNamespace.ExpMonth] = None,
        option_type: Optional[str] = None,
        entitlement: Optional[OptionNamespace.Entitlement] = None,
    ) -> Response:
        """Get option chain data for the provided symbol.

        Args:
            symbol (str): Ticker symbol (e.g. "AAPL").
            contract_type (OptionNamespace.ContractType, optional): Option contract type.
            strike_count (int, optional): Number of strikes above/below ATM.
            include_underlying_quote (bool, optional): Include quote of the underlying asset.
            strategy (OptionNamespace.Strategy, optional): Option chain strategy.
            interval (float, optional): Strike interval for spread strategy chains.
            strike (float, optional): Specific strike price.
            option_range (str, optional): Range filter (e.g. ITM, NTM, OTM).
            from_date (str, optional): Start expiration date (yyyy-MM-dd).
            to_date (str, optional): End expiration date (yyyy-MM-dd).
            volatility (float, optional): Volatility for ANALYTICAL strategies.
            underlying_price (float, optional): Override for underlying price.
            interest_rate (float, optional): Override for interest rate.
            days_to_expiration (int, optional): Days to expiration override.
            exp_month (OptionNamespace.ExpMonth, optional): Expiration month.
            option_type (str, optional): Type of option.
            entitlement (OptionNamespace.Entitlement, optional): Entitlement class.

        Returns:
            Response: HTTP response from the server.

        """
        params: dict[str, Any] = {}  # Initialize parameters

        normalized_ticker = normalize_ticker(symbol)  # Validate ticker

        # Build params dicitionary.
        # Might need more validation for other fields.
        params = {
            "symbol": normalized_ticker,
            "contractType": resolve_enum(
                contract_type,
                OptionNamespace.ContractType,
                default=OptionNamespace.ContractType.ALL,
            ),
            "strikeCount": strike_count,
            "includeUnderlyingQuote": include_underlying_quote,
            "strategy": strategy,
            "interval": interval,
            "strike": strike,
            "range": resolve_enum(
                option_range,
                OptionNamespace.Moneyness,
                default=OptionNamespace.Moneyness.ALL,
            ),
            "fromDate": from_date,
            "toDate": to_date,
            "volatility": volatility,
            "underlyingPrice": underlying_price,
            "interestRate": interest_rate,
            "daysToExpiration": days_to_expiration,
            "expMonth": resolve_enum(
                exp_month,
                OptionNamespace.ExpMonth,
                default=OptionNamespace.ExpMonth.ALL,
            ),
            "optionType": resolve_enum(
                option_type, OptionNamespace.Type, default=OptionNamespace.Type.ALL
            ),
            "entitlement": entitlement,
        }

        path = MARKET_DATA_PATH + "/chains"
        return await self.client._get(path, params)
