"""
config/settings.py – loads all configuration from environment variables.
Copy .env.example to .env and fill in your real values before running.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    # Coinbase Advanced Trade
    coinbase_api_key: str = field(default="")
    coinbase_api_secret: str = field(default="")

    # OANDA v20
    oanda_account_id: str = field(default="")
    oanda_api_token: str = field(default="")
    oanda_environment: str = field(default="practice")  # "practice" | "live"

    # Bot behaviour
    signal_interval_seconds: int = field(default=60)
    min_confidence: float = field(default=0.65)
    max_total_exposure_usd: float = field(default=1000.0)
    paper_mode: bool = field(default=True)

    # Logging
    log_level: str = field(default="INFO")

    # ---------------------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            coinbase_api_key=os.environ.get("COINBASE_API_KEY", ""),
            coinbase_api_secret=os.environ.get("COINBASE_API_SECRET", ""),
            oanda_account_id=os.environ.get("OANDA_ACCOUNT_ID", ""),
            oanda_api_token=os.environ.get("OANDA_API_TOKEN", ""),
            oanda_environment=os.environ.get("OANDA_ENVIRONMENT", "practice"),
            signal_interval_seconds=int(os.environ.get("SIGNAL_INTERVAL_SECONDS", "60")),
            min_confidence=float(os.environ.get("MIN_CONFIDENCE", "0.65")),
            max_total_exposure_usd=float(os.environ.get("MAX_TOTAL_EXPOSURE_USD", "1000.0")),
            paper_mode=os.environ.get("PAPER_MODE", "true").lower() == "true",
            log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        )

    def validate(self) -> None:
        """Raise ValueError if required secrets are missing."""
        if not self.coinbase_api_key:
            raise ValueError("COINBASE_API_KEY is not set")
        if not self.coinbase_api_secret:
            raise ValueError("COINBASE_API_SECRET is not set")
        if not self.oanda_account_id:
            raise ValueError("OANDA_ACCOUNT_ID is not set")
        if not self.oanda_api_token:
            raise ValueError("OANDA_API_TOKEN is not set")
        if self.oanda_environment not in ("practice", "live"):
            raise ValueError("OANDA_ENVIRONMENT must be 'practice' or 'live'")
