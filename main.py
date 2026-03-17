"""
New_rbtz_phoenix – headless multi-broker trading bot
Entry point: python main.py
"""

import time
import signal
import sys

from config.settings import Settings
from utils.logger import get_logger
from signals.engine import SignalEngine
from brokers.coinbase.client import CoinbaseClient
from brokers.oanda.client import OandaClient
from risk.manager import RiskManager

logger = get_logger(__name__)


def main() -> None:
    settings = Settings.from_env()
    logger.info("starting", paper_mode=settings.paper_mode, log_level=settings.log_level)

    if not settings.paper_mode:
        settings.validate()

    coinbase = CoinbaseClient(settings)
    oanda = OandaClient(settings)
    signal_engine = SignalEngine(settings, coinbase, oanda)
    risk_manager = RiskManager(settings)

    # Verify connectivity before entering the main loop
    coinbase.check_connection()
    oanda.check_connection()
    logger.info("broker_connections_ok")

    def _shutdown(signum, frame):  # noqa: ANN001
        logger.info("shutdown_requested", signum=signum)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info("entering_main_loop", interval_seconds=settings.signal_interval_seconds)
    while True:
        try:
            signals = signal_engine.run()
            for trade_signal in signals:
                if not risk_manager.approve(trade_signal):
                    logger.info("signal_rejected_by_risk", signal=trade_signal)
                    continue
                if settings.paper_mode:
                    logger.info("paper_trade", signal=trade_signal)
                else:
                    broker = coinbase if trade_signal.broker == "coinbase" else oanda
                    result = broker.place_order(trade_signal)
                    logger.info("order_placed", result=result)
        except Exception as exc:  # noqa: BLE001
            logger.error("loop_error", error=str(exc))

        time.sleep(settings.signal_interval_seconds)


if __name__ == "__main__":
    main()
