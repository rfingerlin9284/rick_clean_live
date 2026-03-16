#!/usr/bin/env python3
"""
News Scanner Background Service - RBOTzilla Multi-Broker Phase 5
Polls public news/headline APIs, classifies each item by market/direction/confidence,
and maintains a scored event queue consumed by the signal engine and execution adapters.

Data sources (no API key required for basic tier):
  - CryptoPanic public API (crypto news)
  - Yahoo Finance RSS headlines (fallback)
  - Forex Factory calendar JSON (macro events)

PIN: 841921
"""

from __future__ import annotations

import logging
import os
import sys
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List, Optional

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class NewsItem:
    """A single scored news or calendar event."""
    id: str
    headline: str
    source: str
    published_at: str
    affected_markets: List[str]     # e.g. ["BTC", "CRYPTO", "RISK"]
    direction: str                  # "BULLISH" | "BEARISH" | "NEUTRAL"
    confidence: float               # 0-100
    raw: Dict = field(default_factory=dict)


@dataclass
class ConfidenceSnapshot:
    """Aggregated confidence snapshot across all recent news."""
    timestamp: str
    overall_confidence: float       # 0-100
    crypto_sentiment: float         # -1 to +1
    macro_risk_level: float         # 0-100 (higher = more risky)
    active_items: int
    top_headline: Optional[str] = None


# ---------------------------------------------------------------------------
# Keyword-based classification
# ---------------------------------------------------------------------------

_BULLISH_KEYWORDS = frozenset([
    "rally", "surge", "soar", "bull", "gain", "rise", "up", "growth",
    "breakout", "all-time high", "ath", "approve", "adoption", "etf approval",
    "rate cut", "dovish", "stimulus", "positive", "buy",
])

_BEARISH_KEYWORDS = frozenset([
    "crash", "drop", "plunge", "bear", "loss", "fall", "down", "decline",
    "ban", "regulation", "hack", "breach", "failure", "sell-off",
    "rate hike", "hawkish", "recession", "negative", "sell", "liquidation",
])

_CRYPTO_KEYWORDS = frozenset(["bitcoin", "btc", "ethereum", "eth", "crypto", "defi", "nft", "blockchain"])
_MACRO_KEYWORDS  = frozenset(["fed", "ecb", "fomc", "nfp", "cpi", "gdp", "inflation", "rate", "treasury"])
_GOLD_KEYWORDS   = frozenset(["gold", "xau", "silver", "precious metal", "safe haven"])
_FX_KEYWORDS     = frozenset(["dollar", "usd", "dxy", "euro", "eur", "pound", "gbp", "forex", "fx"])


def _classify_headline(text: str) -> tuple[str, List[str], float]:
    """
    Returns (direction, affected_markets, confidence) for a headline string.
    Simple keyword scoring — production systems should replace this with an
    embedding-based or fine-tuned NLP classifier.
    """
    lower = text.lower()

    # Direction
    bull_hits = sum(1 for kw in _BULLISH_KEYWORDS if kw in lower)
    bear_hits = sum(1 for kw in _BEARISH_KEYWORDS if kw in lower)
    if bull_hits > bear_hits:
        direction = "BULLISH"
        confidence = min(100.0, 50.0 + bull_hits * 10)
    elif bear_hits > bull_hits:
        direction = "BEARISH"
        confidence = min(100.0, 50.0 + bear_hits * 10)
    else:
        direction = "NEUTRAL"
        confidence = 30.0

    # Markets
    markets: List[str] = []
    if any(kw in lower for kw in _CRYPTO_KEYWORDS):
        markets.append("CRYPTO")
    if any(kw in lower for kw in _MACRO_KEYWORDS):
        markets.append("MACRO")
    if any(kw in lower for kw in _GOLD_KEYWORDS):
        markets.append("GOLD")
    if any(kw in lower for kw in _FX_KEYWORDS):
        markets.append("FX")
    if not markets:
        markets.append("GENERAL")

    return direction, markets, confidence


# ---------------------------------------------------------------------------
# Source adapters
# ---------------------------------------------------------------------------

def _fetch_cryptopanic(api_key: Optional[str] = None) -> List[Dict]:
    """
    Fetch news from CryptoPanic public endpoint.
    Returns a list of raw items or empty list on failure.
    """
    import requests

    base_url = "https://cryptopanic.com/api/v1/posts/"
    params: Dict[str, str] = {"public": "true", "kind": "news"}
    if api_key:
        params["auth_token"] = api_key

    try:
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception as exc:
        logger.debug("CryptoPanic fetch failed: %s", exc)
        return []


def _fetch_yahoo_rss(symbol: str = "BTC-USD") -> List[Dict]:
    """
    Fetch headlines from Yahoo Finance RSS feed.
    Returns a list of simplified dicts or empty list on failure.
    """
    import requests
    import xml.etree.ElementTree as ET

    url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for item in root.findall(".//item"):
            title_el = item.find("title")
            link_el  = item.find("link")
            pub_el   = item.find("pubDate")
            if title_el is not None:
                items.append({
                    "title": title_el.text or "",
                    "url":   (link_el.text if link_el is not None else ""),
                    "published_at": (pub_el.text if pub_el is not None else ""),
                    "source": "yahoo_rss",
                })
        return items
    except Exception as exc:
        logger.debug("Yahoo RSS fetch failed for %s: %s", symbol, exc)
        return []


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

class NewsScanner:
    """
    Background news scanner.

    Start with scanner.start() — it spawns a daemon thread that polls
    headlines on a configurable interval.  Call scanner.stop() to halt it.

    Retrieve the latest aggregated snapshot via scanner.snapshot().
    Subscribe to new items via scanner.on_item(callback).

    Usage::

        scanner = NewsScanner(pin=841921, poll_interval=120)
        scanner.start()
        ...
        snap = scanner.snapshot()
        print(snap.overall_confidence, snap.crypto_sentiment)
        scanner.stop()
    """

    DEFAULT_POLL_INTERVAL = 120   # seconds
    MAX_QUEUE_SIZE        = 200   # keep last N scored items

    def __init__(
        self,
        pin: int = 841921,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        cryptopanic_api_key: Optional[str] = None,
    ):
        self._validate_pin(pin)
        self._poll_interval   = poll_interval
        self._cp_api_key      = cryptopanic_api_key or os.getenv("CRYPTOPANIC_API_KEY")
        self._items: List[NewsItem] = []
        self._lock            = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._stop_event      = threading.Event()
        self._callbacks: List[Callable[[NewsItem], None]] = []
        self._seen_ids: set   = set()
        self._snapshot: Optional[ConfidenceSnapshot] = None
        logger.info("NewsScanner initialised (poll_interval=%ds).", poll_interval)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background polling thread (daemon)."""
        if self._thread and self._thread.is_alive():
            logger.warning("NewsScanner already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run, name="NewsScanner", daemon=True
        )
        self._thread.start()
        logger.info("NewsScanner started.")

    def stop(self) -> None:
        """Signal the background thread to stop and wait for it."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("NewsScanner stopped.")

    def on_item(self, callback: Callable[[NewsItem], None]) -> None:
        """Register a callback to receive each new NewsItem as it arrives."""
        self._callbacks.append(callback)

    def snapshot(self) -> ConfidenceSnapshot:
        """Return the most recent aggregated confidence snapshot."""
        with self._lock:
            if self._snapshot:
                return self._snapshot
            return ConfidenceSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                overall_confidence=50.0,
                crypto_sentiment=0.0,
                macro_risk_level=0.0,
                active_items=0,
            )

    def recent_items(self, n: int = 20) -> List[NewsItem]:
        """Return the most recent *n* scored items."""
        with self._lock:
            return list(self._items[-n:])

    # ------------------------------------------------------------------
    # Background loop
    # ------------------------------------------------------------------

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._poll()
            except Exception as exc:
                logger.warning("NewsScanner poll error: %s", exc)
            self._stop_event.wait(timeout=self._poll_interval)

    def _poll(self) -> None:
        new_raw: List[Dict] = []

        # Source 1: CryptoPanic
        cp_items = _fetch_cryptopanic(self._cp_api_key)
        for item in cp_items:
            new_raw.append({
                "id":    str(item.get("id", "")),
                "title": item.get("title", ""),
                "source": "cryptopanic",
                "published_at": item.get("published_at", ""),
                "raw": item,
            })

        # Source 2: Yahoo Finance RSS for BTC and EUR/USD
        for rss_sym in ("BTC-USD", "EURUSD=X"):
            for item in _fetch_yahoo_rss(rss_sym):
                new_raw.append({
                    "id":    item.get("url", "") or item.get("title", ""),
                    "title": item.get("title", ""),
                    "source": "yahoo_rss",
                    "published_at": item.get("published_at", ""),
                    "raw": item,
                })

        scored: List[NewsItem] = []
        for raw in new_raw:
            item_id = raw.get("id") or raw.get("title", "")[:80]
            if item_id in self._seen_ids:
                continue
            self._seen_ids.add(item_id)

            direction, markets, confidence = _classify_headline(raw["title"])
            news_item = NewsItem(
                id=item_id,
                headline=raw["title"],
                source=raw["source"],
                published_at=raw.get("published_at", datetime.now(timezone.utc).isoformat()),
                affected_markets=markets,
                direction=direction,
                confidence=confidence,
                raw=raw.get("raw", {}),
            )
            scored.append(news_item)
            for cb in self._callbacks:
                try:
                    cb(news_item)
                except Exception as exc:
                    logger.debug("NewsScanner callback error: %s", exc)

        with self._lock:
            self._items.extend(scored)
            # Trim to max queue size
            if len(self._items) > self.MAX_QUEUE_SIZE:
                self._items = self._items[-self.MAX_QUEUE_SIZE:]
            self._snapshot = self._aggregate(self._items)

        if scored:
            logger.info("NewsScanner: ingested %d new item(s).", len(scored))

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    @staticmethod
    def _aggregate(items: List[NewsItem]) -> ConfidenceSnapshot:
        """
        Build a ConfidenceSnapshot from the current item list.
        Only considers items from the last 4 hours.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=4)
        recent = [
            it for it in items
            if _parse_dt(it.published_at) >= cutoff
        ]

        if not recent:
            return ConfidenceSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                overall_confidence=50.0,
                crypto_sentiment=0.0,
                macro_risk_level=0.0,
                active_items=0,
            )

        # Crypto sentiment: average directional score for CRYPTO items
        crypto_items = [it for it in recent if "CRYPTO" in it.affected_markets]
        if crypto_items:
            scores = [
                (it.confidence / 100.0) * (1 if it.direction == "BULLISH" else -1 if it.direction == "BEARISH" else 0)
                for it in crypto_items
            ]
            crypto_sentiment = sum(scores) / len(scores)
        else:
            crypto_sentiment = 0.0

        # Macro risk: average confidence of MACRO / BEARISH items
        macro_bearish = [it for it in recent if "MACRO" in it.affected_markets and it.direction == "BEARISH"]
        macro_risk    = (sum(it.confidence for it in macro_bearish) / len(macro_bearish)) if macro_bearish else 0.0

        # Overall confidence (higher = clearer directional signal)
        overall = (abs(crypto_sentiment) * 50 + (100 - macro_risk) * 0.5)
        overall = round(max(0.0, min(100.0, overall)), 2)

        top = recent[-1].headline if recent else None

        return ConfidenceSnapshot(
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_confidence=overall,
            crypto_sentiment=round(crypto_sentiment, 4),
            macro_risk_level=round(macro_risk, 2),
            active_items=len(recent),
            top_headline=top,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_pin(pin: int) -> None:
        try:
            from foundation.rick_charter import validate_pin as _vp
            _vp(pin)
        except ImportError:
            if pin != 841921:
                raise ValueError(f"Invalid PIN: {pin}")


def _parse_dt(dt_str: str) -> datetime:
    """Best-effort parse of an ISO-8601 or RFC-2822 datetime string."""
    if not dt_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    # Try Python's fromisoformat (handles most ISO-8601 variants in 3.7+)
    # Replace trailing Z with +00:00 for compatibility before Python 3.11
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        pass
    # RFC-2822 style (from RSS feeds)
    try:
        import email.utils
        tup = email.utils.parsedate(dt_str)
        if tup:
            return datetime(*tup[:6], tzinfo=timezone.utc)
    except Exception:
        pass
    return datetime.min.replace(tzinfo=timezone.utc)
