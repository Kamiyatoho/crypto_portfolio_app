import os
import time
import hmac
import hashlib
from urllib.parse import urlencode
import requests


class BinanceClient:
    """
    Low-level Binance REST client for signed and unsigned requests.

    Provides methods to interact with Binance API endpoints, handling
    authentication, request signing, and error handling.
    """

    BASE_URL = "https://api.binance.com"

    def __init__(self, api_key: str = None, api_secret: str = None, timeout: int = 10):
        """
        Initialize the client with API key/secret and request timeout.
        Keys default to environment variables BINANCE_API_KEY and BINANCE_API_SECRET.
        """
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.timeout = timeout

    def _public_request(self, method: str, path: str, params: dict = None) -> dict:
        """
        Send a public (unsigned) request.
        """
        url = f"{self.BASE_URL}{path}"
        try:
            response = requests.request(method, url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Binance public request error: {e}")

    def _signed_request(self, method: str, path: str, params: dict = None) -> dict:
        """
        Send a signed request to the Binance API (requires API key & secret).

        :param method: HTTP method ("GET", "POST", etc.)
        :param path: Endpoint path (e.g., "/api/v3/account").
        :param params: Query parameters.
        :return: Parsed JSON response.
        """
        if params is None:
            params = {}
        # Add timestamp
        params['timestamp'] = int(time.time() * 1000)
        # Create query string
        query_string = urlencode(params)
        # Signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        # Final URL
        url = f"{self.BASE_URL}{path}?{query_string}&signature={signature}"
        headers = {
            'X-MBX-APIKEY': self.api_key
        }
        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Binance signed request error: {e}")

    def get_server_time(self) -> dict:
        """
        Fetch the Binance server time.
        """
        return self._public_request('GET', '/api/v3/time')

    def get_deposit_history(self, startTime: int = None, endTime: int = None, **kwargs) -> list:
        """
        Get deposit history for the account.

        :param startTime: Filter records after this timestamp (ms).
        :param endTime: Filter records before this timestamp (ms).
        :return: List of deposit records.
        """
        params = {}
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        # Add any other optional params passed via kwargs
        params.update(kwargs)
        return self._signed_request('GET', '/sapi/v1/capital/deposit/hisrec', params)

    def get_withdraw_history(self, startTime: int = None, endTime: int = None, **kwargs) -> list:
        """
        Get withdrawal history for the account.

        :param startTime: Filter records after this timestamp (ms).
        :param endTime: Filter records before this timestamp (ms).
        :return: List of withdrawal records.
        """
        params = {}
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        params.update(kwargs)
        return self._signed_request('GET', '/sapi/v1/capital/withdraw/history', params)

    def get_my_trades(self, symbol: str, startTime: int = None, endTime: int = None, **kwargs) -> list:
        """
        Get trades for the account and symbol.

        :param symbol: Trading pair symbol, e.g., 'BTCUSDT'.
        :param startTime: Filter trades after this timestamp (ms).
        :param endTime: Filter trades before this timestamp (ms).
        :return: List of trade records.
        """
        if not symbol:
            raise ValueError("Symbol parameter is required for getting trades.")
        params = {'symbol': symbol}
        if startTime is not None:
            params['startTime'] = startTime
        if endTime is not None:
            params['endTime'] = endTime
        params.update(kwargs)
        return self._signed_request('GET', '/api/v3/myTrades', params)

    def get_account_info(self) -> dict:
        """
        Get current account information, including balances.
        """
        return self._signed_request('GET', '/api/v3/account')