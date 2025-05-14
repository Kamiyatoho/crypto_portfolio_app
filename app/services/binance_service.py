from .db import SessionLocal
from .sync_utils import get_last_sync, set_last_sync
from .binance.api_client import BinanceClient
from .binance.portfolio import PortfolioCalculator
from .binance.transaction import TransactionService
from .binance.position import PositionService
from .binance.performance import PerformanceService
from .binance.taxes import TaxService


class BinanceService:
    """
    High-level wrapper for Binance portfolio operations:
    - Incremental sync of deposits, withdrawals, and trades
    - Portfolio summary (balances, P/L)
    - Performance metrics
    - Tax reporting
    """

    def __init__(self, api_key=None, api_secret=None, db_url=None):
        # Initialize Binance REST client
        self.client = BinanceClient(api_key=api_key, api_secret=api_secret)
        # Prepare database session
        self.db = SessionLocal()
        # Initialize sub-services
        self.transactions = TransactionService(self.db, self.client)
        self.positions = PositionService(self.db, self.client)
        self.portfolio = PortfolioCalculator(self.db)
        self.performance = PerformanceService(self.db)
        self.taxes = TaxService(self.db)

    def sync(self):  # pragma: no cover
        """
        Incremental synchronization of on-chain events:
        - Deposits
        - Withdrawals
        - Trades

        Uses the last sync timestamp to fetch only new records.
        """
        # Retrieve last sync timestamp
        last_ts = get_last_sync()

        # Fetch deltas from Binance
        deposits = self.client.get_deposit_history(startTime=last_ts)
        withdrawals = self.client.get_withdraw_history(startTime=last_ts)
        trades = self.client.get_my_trades(startTime=last_ts)

        # Upsert into database
        self.transactions.upsert_deposits(deposits)
        self.transactions.upsert_withdrawals(withdrawals)
        self.transactions.upsert_trades(trades)

        # Optionally upsert open positions
        self.positions.upsert_current_positions()

        # Compute new max timestamp for next sync
        all_times = [last_ts]
        all_times += [d.get('time', 0) for d in deposits or []]
        all_times += [w.get('time', 0) for w in withdrawals or []]
        all_times += [t.get('time', 0) for t in trades or []]
        max_ts = max(all_times)

        # Update sync marker
        set_last_sync(max_ts)

    def get_portfolio_data(self, year: int = None) -> dict:
        """
        Returns current portfolio summary:
        - Balances per asset
        - Total invested capital
        - Current market value
        - Unrealized P/L

        :param year: filter deposits/trades by year for invested capital
        """
        balances = self.portfolio.compute_balances()
        invested = self.portfolio.calculate_invested(year=year)
        current_value = self.portfolio.calculate_current_value()
        pl = current_value - invested

        return {
            "balances": balances,
            "invested": invested,
            "current_value": current_value,
            "profit_loss": pl,
        }

    def get_performance_data(self, start_date=None, end_date=None) -> dict:
        """
        Compute performance metrics over a time range:
        - Returns series (daily, weekly, monthly)
        - Max drawdown, CAGR, sharpe ratio, etc.
        """
        return self.performance.compute_metrics(start_date=start_date, end_date=end_date)

    def get_tax_report(self, year: int) -> dict:
        """
        Generates a tax report for the given fiscal year.
        Includes realized gains/losses and taxable amount per French regulations.
        """
        return self.taxes.generate_report(year)