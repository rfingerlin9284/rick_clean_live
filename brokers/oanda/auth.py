"""
brokers/oanda/auth.py – OANDA v20 authentication helpers.

OANDA uses a simple Bearer token.  The token is included in the
Authorization header of every request.
See: https://developer.oanda.com/rest-live-v20/introduction/
"""

from __future__ import annotations


def build_headers(api_token: str, content_type: str = "application/json") -> dict:
    """Return request headers for the OANDA v20 REST API."""
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": content_type,
        "Accept-Datetime-Format": "RFC3339",
    }
