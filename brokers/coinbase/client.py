"""
brokers/coinbase/client.py – Coinbase Advanced Trade REST client.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import requests

from brokers.coinbase.auth import build_headers
from utils.logger import get_logger

if TYPE_CHECKING:
    from config.settings import Settings
    from signals.engine import TradeSignal

logger = get_logger(__name__)

_BASE_URL = "https://api.coinbase.com"


class CoinbaseClient:
    def __init__(self, settings: "Settings") -> None:
        self._api_key = settings.coinbase_api_key
        self._api_secret = settings.coinbase_api_secret
        self._paper_mode = settings.paper_mode

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    def check_connection(self) -> None:
        """Verify credentials by fetching the account list."""
        path = "/api/v3/brokerage/accounts"
        headers = build_headers(self._api_key, self._api_secret, "GET", path)
        if not self._api_key or not self._api_secret:
            logger.warning("coinbase_credentials_not_set_skipping_check")
            return
        try:
            response = requests.get(_BASE_URL + path, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info("coinbase_connection_ok")
        except requests.RequestException as exc:
            logger.error("coinbase_connection_failed", error=str(exc))

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_candles(self, product_id: str, granularity: str = "ONE_HOUR", limit: int = 100) -> list:
        """Return recent OHLCV candles for *product_id* (e.g. 'BTC-USD')."""
        path = f"/api/v3/brokerage/products/{product_id}/candles"
        headers = build_headers(self._api_key, self._api_secret, "GET", path)
        params = {"granularity": granularity, "limit": limit}
        response = requests.get(_BASE_URL + path, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("candles", [])

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def place_order(self, trade_signal: "TradeSignal") -> dict:
        """Submit a market order to Coinbase Advanced Trade."""
        if self._paper_mode:
            logger.info("paper_order_skipped_coinbase", signal=str(trade_signal))
            return {"status": "paper"}

        path = "/api/v3/brokerage/orders"
        payload = {
            "client_order_id": trade_signal.signal_id,
            "product_id": trade_signal.symbol,
            "side": trade_signal.side.upper(),
            "order_configuration": {
                "market_market_ioc": {
                    "quote_size": str(trade_signal.notional_usd),
                },
            },
        }
        body = json.dumps(payload)
        headers = build_headers(self._api_key, self._api_secret, "POST", path, body)
        response = requests.post(_BASE_URL + path, headers=headers, data=body, timeout=10)
        response.raise_for_status()
        return response.json()
