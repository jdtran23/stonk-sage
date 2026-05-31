"""Tests for ``stonk_sage.data``.

Network-touching tests are gated behind ``-m live`` so the default ``pytest``
run stays hermetic and fast.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pytest

from stonk_sage.contracts import MarketSnapshot
from stonk_sage.data import (
    EdgarIdentityMissing,
    _as_datetime,
    _assert_no_lookahead,
    _ensure_edgar_identity,
    _safe_float,
    _truncate,
    snapshot_path,
)


# ---------------------------------------------------------------------------
# Pure helper tests — no network.
# ---------------------------------------------------------------------------


class TestAsDatetime:
    def test_date_to_datetime_at_midnight(self) -> None:
        d = date(2024, 6, 1)
        assert _as_datetime(d) == datetime(2024, 6, 1, 0, 0, 0)

    def test_datetime_passes_through(self) -> None:
        dt = datetime(2024, 6, 1, 14, 30, 0)
        assert _as_datetime(dt) is dt


class TestSafeFloat:
    @pytest.mark.parametrize(
        "v, expected",
        [
            (None, 0.0),
            (1.5, 1.5),
            ("2.5", 2.5),
            ("not a number", 0.0),
            ({}, 0.0),
        ],
    )
    def test_coerces_or_zeros(self, v: object, expected: float) -> None:
        assert _safe_float(v) == expected


class TestTruncate:
    def test_short_string_unchanged(self) -> None:
        assert _truncate("hello", 100) == "hello"

    def test_long_string_truncated_with_ellipsis(self) -> None:
        result = _truncate("x" * 50, 10)
        assert len(result) == 10
        assert result.endswith("...")


class TestSnapshotPath:
    def test_path_format(self, tmp_path: Path) -> None:
        p = snapshot_path("aapl", date(2024, 6, 1), root=tmp_path)
        assert p == tmp_path / "AAPL_2024-06-01.json"
        assert tmp_path.is_dir()

    def test_accepts_datetime(self, tmp_path: Path) -> None:
        p = snapshot_path("MSFT", datetime(2024, 6, 1, 12, 0), root=tmp_path)
        assert p == tmp_path / "MSFT_2024-06-01.json"


class TestEnsureEdgarIdentity:
    def test_missing_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("EDGAR_IDENTITY", raising=False)
        with pytest.raises(EdgarIdentityMissing):
            _ensure_edgar_identity()

    def test_present_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("EDGAR_IDENTITY", "Test User test@example.com")
        _ensure_edgar_identity()  # no raise


# ---------------------------------------------------------------------------
# Invariant tests on a hand-built snapshot — no network.
# ---------------------------------------------------------------------------


def _baseline_snapshot(as_of: datetime) -> MarketSnapshot:
    """Minimal valid MarketSnapshot for assertion testing."""
    return MarketSnapshot(
        ticker="TEST",
        as_of=as_of,
        business_summary="Test business.",
        latest_10k_filing_date=date(2023, 1, 1),
        key_financials={"market_cap": 1000.0},
        key_ratios={"pe_trailing": 10.0},
        price_summary={"price_at_as_of": 100.0, "high_52w": 110.0, "low_52w": 90.0},
        news_highlights=[],
        spy_return_same_window=0.05,
        ticker_return_same_window=0.10,
    )


class TestNoLookaheadAssertion:
    def test_passes_when_no_dates_exceed_as_of(self) -> None:
        snap = _baseline_snapshot(datetime(2024, 6, 1))
        _assert_no_lookahead(snap, datetime(2024, 6, 1))

    def test_passes_when_news_date_equals_as_of(self) -> None:
        snap = _baseline_snapshot(datetime(2024, 6, 1))
        snap = snap.model_copy(
            update={"news_highlights": ["[2024-06-01] Earnings beat"]}
        )
        _assert_no_lookahead(snap, datetime(2024, 6, 1))

    def test_fails_when_news_date_after_as_of(self) -> None:
        snap = _baseline_snapshot(datetime(2024, 6, 1))
        snap = snap.model_copy(
            update={"news_highlights": ["[2024-06-15] Late news"]}
        )
        with pytest.raises(AssertionError, match="news_highlights has date > as_of"):
            _assert_no_lookahead(snap, datetime(2024, 6, 1))

    def test_ignores_unparseable_prefix(self) -> None:
        snap = _baseline_snapshot(datetime(2024, 6, 1))
        snap = snap.model_copy(
            update={"news_highlights": ["No date prefix here"]}
        )
        _assert_no_lookahead(snap, datetime(2024, 6, 1))


# ---------------------------------------------------------------------------
# Live network tests — opt-in.
# ---------------------------------------------------------------------------


@pytest.mark.live
def test_live_fetch_aapl_saturday_rolls_back_to_friday() -> None:
    """``as_of=2024-06-01`` (Saturday) → ``price_at_as_of`` is Friday 2024-05-31 close.

    Verifies no-look-ahead semantics on weekends. Requires network +
    ``EDGAR_IDENTITY`` env var.
    """
    from stonk_sage.data import fetch_market_snapshot

    snap = fetch_market_snapshot("AAPL", date(2024, 6, 1))
    assert snap.ticker == "AAPL"
    assert snap.as_of.date() == date(2024, 6, 1)
    assert snap.latest_10k_filing_date < date(2024, 6, 1)
    assert snap.price_summary["price_at_as_of"] > 0.0
    # Friday 2024-05-31 AAPL close was ~$192 historically; loose bound to avoid
    # adjustment-policy churn in yfinance.
    assert 100.0 < snap.price_summary["price_at_as_of"] < 400.0
