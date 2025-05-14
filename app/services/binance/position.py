# app/services/binance/position.py

from .api_client import BinanceClient
from app.utils.pricing import get_current_price


class PositionService:
    """
    Manage and compute spot positions from a Binance account.
    """

    def __init__(self, client: BinanceClient):
        """
        :param client: an instance of your low-level BinanceClient
        """
        self.client = client

    def get_balances(self) -> list[dict]:
        """
        Fetch raw balances from Binance account endpoint.
        Returns the 'balances' list from /api/v3/account.
        """
        account_info = self.client.get_account()
        return account_info.get("balances", [])

    def get_open_positions(self) -> list[dict]:
        """
        Returns a list of all assets with non-zero total quantity,
        enriched with current price and USD value.

        Each dict has:
          - asset: symbol (e.g. "BTC")
          - quantity: free + locked
          - price: price in USDT (None if unavailable)
          - value: quantity * price (None if price is None)
        """
        positions = []
        for bal in self.get_balances():
            asset = bal["asset"]
            qty_free = float(bal.get("free", 0))
            qty_locked = float(bal.get("locked", 0))
            total_qty = qty_free + qty_locked
            if total_qty <= 0:
                continue

            # Attempt to fetch price vs USDT
            symbol = f"{asset}USDT"
            try:
                price = get_current_price(symbol)
            except Exception:
                price = None

            positions.append({
                "asset": asset,
                "quantity": total_qty,
                "price": price,
                "value": total_qty * price if price is not None else None,
            })

        return positions

    def get_position(self, asset: str) -> dict | None:
        """
        Get a single position by asset symbol, or None if not held.
        """
        for pos in self.get_open_positions():
            if pos["asset"] == asset:
                return pos
        return None

    def total_portfolio_value(self) -> float:
        """
        Sum of all individual position values (ignores those without price).
        """
        return sum(p["value"] for p in self.get_open_positions() if p["value"] is not None)