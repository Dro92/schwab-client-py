# Schwab Client (Unofficial)

An asynchronous python client for interacting with the Schwab Trader API. Currently supports the following APIs:

- Accounts and Trading Production
- Market Data Production

## Overview

The client exposes the following endpoints:

*Account and Trading*
- In Work

*Market Data*
- `.quotes` : Quotes Web Service.
- `.options`: Option Chains Web Service.
- `.market_hours`: MarketHours Web Service.


## Examples

This section is in progress and will be updated soon.

```python
  # Instantiate Schwab client
    client = SchwabClient(token_manager)

    hours = await client.market_hours.get_market_status()

    quote = await client.quotes.get_quotes("BRK/A")

    quotes = await client.quotes.get_quotes(["$BKX", "BRK/B"])

    options = await client.options.get_chain("AAPL")
```