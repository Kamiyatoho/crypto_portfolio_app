from .binance.api_client import BinanceAPIClient
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