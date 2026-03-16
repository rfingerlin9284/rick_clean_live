"""
brokers/coinbase/orders.py – order-related helpers for Coinbase Advanced Trade.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderResult:
    order_id: str
    status: str
    product_id: str
    side: str
    filled_size: Optional[float] = None
    average_filled_price: Optional[float] = None

    @classmethod
    def from_response(cls, data: dict) -> "OrderResult":
        order = data.get("order", data)
        return cls(
            order_id=order.get("order_id", ""),
            status=order.get("status", ""),
            product_id=order.get("product_id", ""),
            side=order.get("side", ""),
            filled_size=float(order["filled_size"]) if order.get("filled_size") else None,
            average_filled_price=(
                float(order["average_filled_price"])
                if order.get("average_filled_price")
                else None
            ),
        )
