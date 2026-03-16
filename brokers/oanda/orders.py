"""
brokers/oanda/orders.py – order-related helpers for OANDA v20.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderResult:
    order_id: str
    instrument: str
    units: float
    price: Optional[float] = None
    status: str = ""

    @classmethod
    def from_response(cls, data: dict) -> "OrderResult":
        fill = data.get("orderFillTransaction", {})
        return cls(
            order_id=fill.get("orderID", ""),
            instrument=fill.get("instrument", ""),
            units=float(fill.get("units", 0)),
            price=float(fill["price"]) if fill.get("price") else None,
            status="filled" if fill else "pending",
        )
