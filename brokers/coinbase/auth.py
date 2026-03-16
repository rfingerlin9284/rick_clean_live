"""
brokers/coinbase/auth.py – Coinbase Advanced Trade request signing.

Coinbase Advanced Trade uses API key + secret for authentication.
Each REST request is signed with a HMAC-SHA256 signature.
See: https://docs.cdp.coinbase.com/advanced-trade/docs/rest-api-auth
"""

from __future__ import annotations

import hashlib
import hmac
import time


def build_headers(api_key: str, api_secret: str, method: str, path: str, body: str = "") -> dict:
    """Return signed request headers for the Coinbase Advanced Trade REST API."""
    timestamp = str(int(time.time()))
    message = timestamp + method.upper() + path + body
    signature = hmac.new(
        api_secret.encode("utf-8"),
        message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return {
        "CB-ACCESS-KEY": api_key,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json",
    }
