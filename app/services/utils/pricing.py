import time
from typing import Optional

from services.binance_client import BinanceClient

# Shared Binance client instance
_client = BinanceClient()


def get_current_price(symbol: str) -> float:
    """
    Fetches the latest market price for a given trading pair (e.g., 'BTCUSDT').

    :param symbol: Symbol string, e.g., 'ETHUSDT'
    :return: Current price as float
    """
    # Binance’s public endpoint for current price
    data = _client._signed_request(
        method="GET",
        path="/api/v3/ticker/price",
        params={"symbol": symbol}
    )
    return float(data.get("price", 0.0))


def get_price_at(symbol: str, timestamp: int) -> Optional[float]:
    """
    Retrieves the closing price for the 1-minute candle in which the given timestamp falls.

    :param symbol: Symbol string, e.g., 'BTCUSDT'
    :param timestamp: Epoch time in milliseconds
    :return: Closing price as float, or None if unavailable
    """
    # Query Binance Klines endpoint with interval=1m starting at the timestamp
    params = {
        "symbol": symbol,
        "interval": "1m",
        "startTime": timestamp,
        "limit": 1
    }
    klines = _client._signed_request(
        method="GET",
        path="/api/v3/klines",
        params=params
    )
    if not klines:
        return None
    # Kline format: [openTime, open, high, low, close, ...]
    close_price = float(klines[0][4])
    return close_price