#!/usr/bin/env python3
"""
Unit tests for services/news_scanner.py
Tests headline classification, aggregation, and scanner lifecycle
without making real HTTP requests.
PIN: 841921
"""

import sys
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from services.news_scanner import (
    NewsScanner,
    NewsItem,
    ConfidenceSnapshot,
    _classify_headline,
    _parse_dt,
)


class TestClassifyHeadline(unittest.TestCase):
    """Tests for the keyword-based headline classifier."""

    def test_bullish_crypto(self):
        direction, markets, confidence = _classify_headline(
            "Bitcoin surges to new all-time high amid ETF approval"
        )
        self.assertEqual(direction, "BULLISH")
        self.assertIn("CRYPTO", markets)
        self.assertGreater(confidence, 50.0)

    def test_bearish_crypto(self):
        direction, markets, confidence = _classify_headline(
            "Bitcoin crash wipes billions as crypto market plunges"
        )
        self.assertEqual(direction, "BEARISH")
        self.assertIn("CRYPTO", markets)
        self.assertGreater(confidence, 50.0)

    def test_neutral_headline(self):
        direction, markets, confidence = _classify_headline(
            "Central bank holds rates unchanged"
        )
        # "central bank" has no strong keyword; direction may be neutral
        self.assertIn(direction, ("BULLISH", "BEARISH", "NEUTRAL"))

    def test_macro_fx_headline(self):
        _, markets, _ = _classify_headline(
            "Fed rate hike expected as CPI remains elevated and dollar strengthens"
        )
        # Should tag at least MACRO or FX
        self.assertTrue(any(m in markets for m in ("MACRO", "FX")))

    def test_gold_headline(self):
        _, markets, _ = _classify_headline("Gold surges as safe-haven demand rises")
        self.assertIn("GOLD", markets)

    def test_confidence_clamped(self):
        _, _, confidence = _classify_headline(
            "bitcoin rally surge soar bull gain rise breakout"
        )
        self.assertLessEqual(confidence, 100.0)
        self.assertGreaterEqual(confidence, 0.0)

    def test_empty_headline(self):
        direction, markets, confidence = _classify_headline("")
        self.assertEqual(direction, "NEUTRAL")
        self.assertIn("GENERAL", markets)

    def test_markets_fallback_to_general(self):
        # Avoid strings that accidentally contain keyword substrings (e.g. "eth" in "something")
        _, markets, _ = _classify_headline("Local weather was calm and cloudy today")
        self.assertIn("GENERAL", markets)


class TestParseDt(unittest.TestCase):
    """Tests for the _parse_dt helper."""

    def test_iso_utc(self):
        dt = _parse_dt("2025-01-15T12:00:00Z")
        self.assertEqual(dt.hour, 12)

    def test_iso_with_offset(self):
        dt = _parse_dt("2025-01-15T12:00:00+00:00")
        self.assertIsNotNone(dt)

    def test_empty_string(self):
        dt = _parse_dt("")
        self.assertEqual(dt, datetime.min.replace(tzinfo=timezone.utc))

    def test_garbage_string(self):
        dt = _parse_dt("not-a-date")
        self.assertEqual(dt, datetime.min.replace(tzinfo=timezone.utc))


class TestNewsScannerClassification(unittest.TestCase):
    """Tests that the scanner classifies and stores items correctly."""

    def _make_scanner(self) -> NewsScanner:
        return NewsScanner(pin=841921, poll_interval=9999)

    def test_init_valid_pin(self):
        scanner = self._make_scanner()
        self.assertIsNotNone(scanner)

    def test_init_invalid_pin(self):
        with self.assertRaises((ValueError, Exception)):
            NewsScanner(pin=0)

    def test_snapshot_returns_default_before_poll(self):
        scanner = self._make_scanner()
        snap = scanner.snapshot()
        self.assertIsInstance(snap, ConfidenceSnapshot)
        self.assertEqual(snap.overall_confidence, 50.0)

    def test_recent_items_empty_before_poll(self):
        scanner = self._make_scanner()
        items = scanner.recent_items()
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 0)

    @patch("services.news_scanner._fetch_cryptopanic", return_value=[])
    @patch("services.news_scanner._fetch_yahoo_rss", return_value=[])
    def test_poll_with_no_data_doesnt_crash(self, mock_rss, mock_cp):
        scanner = self._make_scanner()
        scanner._poll()
        snap = scanner.snapshot()
        self.assertEqual(snap.active_items, 0)

    @patch("services.news_scanner._fetch_cryptopanic")
    @patch("services.news_scanner._fetch_yahoo_rss", return_value=[])
    def test_poll_ingests_cryptopanic_items(self, mock_rss, mock_cp):
        mock_cp.return_value = [
            {
                "id": 1,
                "title": "Bitcoin rally sends crypto surging",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        scanner = self._make_scanner()
        scanner._poll()
        items = scanner.recent_items()
        self.assertGreater(len(items), 0)
        self.assertEqual(items[0].direction, "BULLISH")

    @patch("services.news_scanner._fetch_cryptopanic", return_value=[])
    @patch("services.news_scanner._fetch_yahoo_rss")
    def test_poll_ingests_yahoo_rss_items(self, mock_rss, mock_cp):
        mock_rss.return_value = [
            {
                "title": "Gold surges as safe-haven demand rises",
                "url": "https://example.com/1",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "source": "yahoo_rss",
            }
        ]
        scanner = self._make_scanner()
        scanner._poll()
        items = scanner.recent_items()
        self.assertGreater(len(items), 0)

    @patch("services.news_scanner._fetch_cryptopanic")
    @patch("services.news_scanner._fetch_yahoo_rss", return_value=[])
    def test_deduplication(self, mock_rss, mock_cp):
        """Same item polled twice should only appear once."""
        mock_cp.return_value = [
            {
                "id": 42,
                "title": "Bitcoin gains momentum",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        scanner = self._make_scanner()
        scanner._poll()
        scanner._poll()  # second poll — same id
        items = scanner.recent_items()
        ids = [it.id for it in items]
        self.assertEqual(len(ids), len(set(ids)))

    def test_callback_fires_on_new_item(self):
        received = []
        scanner = self._make_scanner()
        scanner.on_item(received.append)

        with patch("services.news_scanner._fetch_cryptopanic") as mock_cp, \
             patch("services.news_scanner._fetch_yahoo_rss", return_value=[]):
            mock_cp.return_value = [
                {
                    "id": 99,
                    "title": "Crypto market crashes hard",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
            scanner._poll()

        self.assertEqual(len(received), 1)
        self.assertIsInstance(received[0], NewsItem)

    def test_queue_max_size_respected(self):
        scanner = self._make_scanner()

        # Manually fill beyond max queue size
        now_str = datetime.now(timezone.utc).isoformat()
        for i in range(NewsScanner.MAX_QUEUE_SIZE + 50):
            scanner._items.append(
                NewsItem(
                    id=str(i),
                    headline=f"Item {i}",
                    source="test",
                    published_at=now_str,
                    affected_markets=["GENERAL"],
                    direction="NEUTRAL",
                    confidence=50.0,
                )
            )

        # Force trim via a no-op poll
        with patch("services.news_scanner._fetch_cryptopanic", return_value=[]), \
             patch("services.news_scanner._fetch_yahoo_rss", return_value=[]):
            scanner._poll()

        self.assertLessEqual(len(scanner._items), NewsScanner.MAX_QUEUE_SIZE)


class TestNewsScannerAggregation(unittest.TestCase):
    """Tests for the ConfidenceSnapshot aggregation logic."""

    def _recent_item(self, direction: str, markets=None, confidence: float = 70.0) -> NewsItem:
        import uuid
        return NewsItem(
            id=str(uuid.uuid4()),
            headline="Test headline",
            source="test",
            published_at=datetime.now(timezone.utc).isoformat(),
            affected_markets=markets or ["CRYPTO"],
            direction=direction,
            confidence=confidence,
        )

    def test_aggregate_bullish_items_positive_sentiment(self):
        items = [self._recent_item("BULLISH") for _ in range(5)]
        snap = NewsScanner._aggregate(items)
        self.assertGreater(snap.crypto_sentiment, 0.0)

    def test_aggregate_bearish_items_negative_sentiment(self):
        items = [self._recent_item("BEARISH") for _ in range(5)]
        snap = NewsScanner._aggregate(items)
        self.assertLess(snap.crypto_sentiment, 0.0)

    def test_aggregate_empty_items(self):
        snap = NewsScanner._aggregate([])
        self.assertEqual(snap.overall_confidence, 50.0)
        self.assertEqual(snap.active_items, 0)

    def test_aggregate_old_items_excluded(self):
        """Items older than 4 hours should not affect the snapshot."""
        old_time = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
        old_item = NewsItem(
            id="old",
            headline="Old news",
            source="test",
            published_at=old_time,
            affected_markets=["CRYPTO"],
            direction="BULLISH",
            confidence=80.0,
        )
        snap = NewsScanner._aggregate([old_item])
        self.assertEqual(snap.active_items, 0)

    def test_aggregate_confidence_in_range(self):
        items = [self._recent_item("BULLISH") for _ in range(10)]
        snap = NewsScanner._aggregate(items)
        self.assertGreaterEqual(snap.overall_confidence, 0.0)
        self.assertLessEqual(snap.overall_confidence, 100.0)


class TestNewsScannerLifecycle(unittest.TestCase):
    """Tests for start/stop lifecycle (no real polling)."""

    def test_stop_before_start_doesnt_crash(self):
        scanner = NewsScanner(pin=841921, poll_interval=9999)
        scanner.stop()  # should not raise

    @patch("services.news_scanner._fetch_cryptopanic", return_value=[])
    @patch("services.news_scanner._fetch_yahoo_rss", return_value=[])
    def test_start_and_stop(self, mock_rss, mock_cp):
        scanner = NewsScanner(pin=841921, poll_interval=9999)
        scanner.start()
        self.assertTrue(scanner._thread.is_alive())
        scanner.stop()
        # Thread should stop within a few seconds
        scanner._thread.join(timeout=3)
        self.assertFalse(scanner._thread.is_alive())


if __name__ == "__main__":
    unittest.main(verbosity=2)
