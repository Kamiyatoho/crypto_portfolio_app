# app/services/binance/api_client.py

import time
from typing import Any, Dict, List, Optional

from ..binance_service import BinanceClient


class BinanceAPIClient:
    """
    Low‐level wrapper for the Binance REST API.
    Uses the existing BinanceClient (signing, error‐handling) under the hood.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        timeout: int = 10,
    ):
        """
        :param api_key: Binance API key, or pulled from env in BinanceClient
        :param api_secret: Binance API secret, or pulled from env
        :param timeout: request timeout in seconds
        """
        self._client = BinanceClient(api_key=api_key, api_secret=api_secret, timeout=timeout)

    def get_deposit_history(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Fetch deposit history.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#deposit-history-supporting-network-user_data
        """
        params: Dict[str, Any] = {"limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        return self._client._signed_request(
            method="GET",
            path="/sapi/v1/capital/deposit/hisrec",
            params=params,
        )

    def get_withdraw_history(
        self,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Fetch withdrawal history.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#withdraw-history-supporting-network-user_data
        """
        params: Dict[str, Any] = {"limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        return self._client._signed_request(
            method="GET",
            path="/sapi/v1/capital/withdraw/history",
            params=params,
        )

    def get_my_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """
        Fetch trade history for a symbol.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#account-trade-list-user_data
        """
        params: Dict[str, Any] = {"symbol": symbol, "limit": limit}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        return self._client._signed_request(
            method="GET",
            path="/api/v3/myTrades",
            params=params,
        )

    def get_account_info(self) -> Dict[str, Any]:
        """
        Fetch account information (balances, permissions, etc.).
        Docs: https://binance-docs.github.io/apidocs/spot/en/#account-information-user_data
        """
        return self._client._signed_request(
            method="GET",
            path="/api/v3/account",
            params={}
        )

    def get_symbol_price(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch current price ticker for a single symbol.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#symbol-price-ticker-market_data
        """
        return self._client._signed_request(
            method="GET",
            path="/api/v3/ticker/price",
            params={"symbol": symbol},
        )

    def get_exchange_info(self) -> Dict[str, Any]:
        """
        Fetch exchange trading rules and symbol information.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#exchange-information
        """
        return self._client._signed_request(
            method="GET",
            path="/api/v3/exchangeInfo",
            params={}
        )