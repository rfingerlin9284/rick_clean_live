"""
brokers/oanda/client.py – OANDA v20 REST client.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import requests

from brokers.oanda.auth import build_headers
from utils.logger import get_logger

if TYPE_CHECKING:
    from config.settings import Settings
    from signals.engine import TradeSignal

logger = get_logger(__name__)

_BASE_URLS = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}


class OandaClient:
    def __init__(self, settings: "Settings") -> None:
        self._account_id = settings.oanda_account_id
        self._api_token = settings.oanda_api_token
        self._base_url = _BASE_URLS.get(settings.oanda_environment, _BASE_URLS["practice"])
        self._paper_mode = settings.paper_mode

    # ------------------------------------------------------------------
    # Connectivity
    # ------------------------------------------------------------------

    def check_connection(self) -> None:
        """Verify credentials by fetching account summary."""
        if not self._api_token or not self._account_id:
            logger.warning("oanda_credentials_not_set_skipping_check")
            return
        url = f"{self._base_url}/v3/accounts/{self._account_id}/summary"
        try:
            response = requests.get(url, headers=build_headers(self._api_token), timeout=10)
            response.raise_for_status()
            logger.info("oanda_connection_ok")
        except requests.RequestException as exc:
            logger.error("oanda_connection_failed", error=str(exc))

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------

    def get_candles(self, instrument: str, granularity: str = "H1", count: int = 100) -> list:
        """Return recent OHLCV candles for *instrument* (e.g. 'EUR_USD')."""
        url = f"{self._base_url}/v3/instruments/{instrument}/candles"
        params = {"granularity": granularity, "count": count, "price": "M"}
        response = requests.get(
            url, headers=build_headers(self._api_token), params=params, timeout=10
        )
        response.raise_for_status()
        return response.json().get("candles", [])

    def get_price(self, instrument: str) -> dict:
        """Return the latest bid/ask price for *instrument*."""
        url = f"{self._base_url}/v3/accounts/{self._account_id}/pricing"
        params = {"instruments": instrument}
        response = requests.get(
            url, headers=build_headers(self._api_token), params=params, timeout=10
        )
        response.raise_for_status()
        prices = response.json().get("prices", [])
        return prices[0] if prices else {}

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def place_order(self, trade_signal: "TradeSignal") -> dict:
        """Submit a market order to OANDA."""
        if self._paper_mode:
            logger.info("paper_order_skipped_oanda", signal=str(trade_signal))
            return {"status": "paper"}

        url = f"{self._base_url}/v3/accounts/{self._account_id}/orders"
        payload = {
            "order": {
                "type": "MARKET",
                "instrument": trade_signal.symbol,
                "units": str(trade_signal.units if trade_signal.side == "buy" else -trade_signal.units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
            }
        }
        body = json.dumps(payload)
        response = requests.post(
            url, headers=build_headers(self._api_token), data=body, timeout=10
        )
        response.raise_for_status()
        return response.json()
