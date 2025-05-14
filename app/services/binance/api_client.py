import requests, time, hmac, hashlib
from urllib.parse import urlencode

class BinanceAPIClient:
    BASE_URL = "https://api.binance.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def signed_request(self, method, path, params=None):
        if params is None:
            params = {}
        params['timestamp'] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode(), query_string.encode(), hashlib.sha256
        ).hexdigest()
        headers = {"X-MBX-APIKEY": self.api_key}
        response = requests.request(
            method, f"{self.BASE_URL}{path}?{query_string}&signature={signature}", headers=headers
        )
        response.raise_for_status()
        return response.json()

    def public_request(self, method, path, params=None):
        response = requests.request(
            method, f"{self.BASE_URL}{path}", params=params
        )
        response.raise_for_status()
        return response.json()