# app/services/binance/portfolio.py

from typing import List, Optional, Dict
from datetime import datetime

from ..pricing import get_price_at, get_current_price
from ..utils    import from_timestamp

BASE_ASSETS = {"USDT", "BUSD", "USDC", "EUR", "USD"}


class PortfolioCalculator:
    """
    Compute invested capital, current value and P/L for a Binance account.
    """

    def __init__(self, client, quote_asset: str = "USDT"):
        """
        :param client: an instance of BinanceClient
        :param quote_asset: the asset in which P/L is expressed (e.g. "USDT")
        """
        self.client = client
        self.quote_asset = quote_asset

    def fetch_deposits(self, since_ts: Optional[int] = None) -> List[Dict]:
        """
        Returns list of deposit dicts from Binance (each with keys 'asset','amount','time','txId',…).
        If since_ts is provided, only returns deposits with time >= since_ts.
        """
        return self.client.get_deposit_history(startTime=since_ts) or []

    def fetch_balances(self) -> List[Dict]:
        """
        Returns account balances: each dict has 'asset', 'free', 'locked'.
        """
        acct = self.client.get_account()
        return acct.get("balances", [])

    def calculate_invested(
        self,
        deposits: List[Dict],
        year: Optional[int] = None
    ) -> float:
        """
        Sum of all deposits, converted to quote_asset.
        If year is provided, only includes deposits whose timestamp falls in that year.
        """
        total = 0.0
        for dep in deposits:
            ts = int(dep.get("time", 0))
            dep_dt = from_timestamp(ts)
            if year is not None and dep_dt.year != year:
                continue

            asset = dep.get("asset")
            amt   = float(dep.get("amount", 0))

            if asset in BASE_ASSETS:
                total += amt
            else:
                # e.g. "ETHUSDT"
                sym = f"{asset}{self.quote_asset}"
                price = get_price_at(sym, ts)
                if price is None:
                    raise ValueError(f"Price for {sym} at {ts} not found")
                total += amt * price

        return total

    def calculate_current_value(self, balances: List[Dict]) -> float:
        """
        Sum of (free + locked) for each asset, converted to quote_asset.
        """
        total = 0.0
        for bal in balances:
            asset = bal.get("asset")
            free  = float(bal.get("free",  0))
            locked= float(bal.get("locked",0))
            amt   = free + locked

            if amt == 0:
                continue

            if asset in BASE_ASSETS:
                total += amt
            else:
                sym = f"{asset}{self.quote_asset}"
                price = get_current_price(sym)
                total += amt * price

        return total

    def get_overview(
        self,
        since_ts: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Fetch deposits (since since_ts), balances, then compute:
        - invested: sum of deposits (filtered by year if given)
        - current_value: live portfolio value
        - profit_loss: current_value - invested
        """
        deps     = self.fetch_deposits(since_ts)
        bals     = self.fetch_balances()
        invested = self.calculate_invested(deps, year)
        current  = self.calculate_current_value(bals)
        pl       = current - invested

        return {
            "invested": invested,
            "current_value": current,
            "profit_loss": pl
        }