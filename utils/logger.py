"""
utils/logger.py – structured logging helper built on structlog.
"""

from __future__ import annotations

import logging
import structlog

_configured = False


def _configure_once() -> None:
    global _configured
    if _configured:
        return
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
    )
    _configured = True


def get_logger(name: str) -> structlog.BoundLogger:
    """Return a structlog logger bound to *name*."""
    _configure_once()
    return structlog.get_logger(name)
