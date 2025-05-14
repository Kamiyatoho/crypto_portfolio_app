from .binance.api_client import BinanceAPIClient
from .db      import SessionLocal, Deposit, Withdrawal, Trade
from .sync_utils import get_last_sync, set_last_sync
from .binance.portfolio import (
    get_current_portfolio_value,
    get_total_invested_capital,
    get_realized_pl,
    get_unrealized_pl,
    get_usdc_balance
)
from .binance.positions import get_open_positions, get_closed_positions
from .binance.transactions import (
    get_deposit_history,
    get_withdrawal_history,
    get_trade_history,
    get_conversion_history
)
from .binance.performance import (
    get_portfolio_distribution,
    get_average_invested_distribution,
    get_performance_metrics
)
from .binance.taxes import (
    calculate_yearly_deposits,
    calculate_yearly_withdrawals,
    calculate_current_portfolio_value,
    calculate_estimated_tax,
    calculate_monthly_deposit_withdrawal
)

def upsert_records(db, model, data, pk_field):
    instance = db.query(model).get(data[pk_field])
    if instance:
        for k,v in data.items():
            setattr(instance, k, v)
    else:
        instance = model(**data)
        db.add(instance)

class BinanceService:
    def __init__(self, api_key, api_secret):
        self.client = BinanceAPIClient(api_key, api_secret)

    def get_dashboard_data(self):
        return {
            "valeur_actuelle": get_current_portfolio_value(self.client),
            "capital_investi": get_total_invested_capital(self.client),
            "pl_realise": get_realized_pl(self.client),
            "pl_latent": get_unrealized_pl(self.client),
            "solde_usdc": get_usdc_balance(self.client),
            "open_positions": get_open_positions(self.client),
            "closed_positions": get_closed_positions(self.client),
            "distribution_actuelle": get_portfolio_distribution(self.client),
            "distribution_investie": get_average_invested_distribution(self.client),
            "performance": get_performance_metrics(self.client),
        }

    def get_transaction_data(self):
        return {
            "deposits": get_deposit_history(self.client),
            "withdrawals": get_withdrawal_history(self.client),
            "trades": get_trade_history(self.client),
            "conversions": get_conversion_history(self.client),
        }

    def get_tax_data(self, year):
        return {
            "totalDeposit": calculate_yearly_deposits(self.client, year),
            "withdrawals": calculate_yearly_withdrawals(self.client, year),
            "currentValue": calculate_current_portfolio_value(self.client),
            "tax": calculate_estimated_tax(self.client, year),
            "monthly_data": calculate_monthly_deposit_withdrawal(self.client, year)
        }

    def sync(self):
            last_ts = get_last_sync()
            # 1. récupérer deltas
            deps   = self.client.get_deposit_history(startTime=last_ts)
            wds    = self.client.get_withdraw_history(startTime=last_ts)
            trades = self.client.get_my_trades(startTime=last_ts)

            db = SessionLocal()
            # 2. upsert
            for d in deps:
                upsert_records(db, Deposit,   {"txId": d["txId"], "asset": d["asset"], "amount": float(d["amount"]), "time": d["time"]}, "txId")
            for w in wds:
                upsert_records(db, Withdrawal,{"txId": w["txId"], "asset": w["asset"], "amount": float(w["amount"]), "time": w["time"]}, "txId")
            for t in trades:
                upsert_records(db, Trade,     {"orderId": t["orderId"], "symbol": t["symbol"], "price": float(t["price"]), "qty": float(t["qty"]), "time": t["time"]}, None)

            db.commit()

            # 3. maj timestamp
            max_ts = max(
                *(d["time"] for d in deps or [last_ts]),
                *(w["time"] for w in wds  or [last_ts]),
                *(t["time"] for t in trades or [last_ts])
            )
            set_last_sync(max_ts)
            db.close()