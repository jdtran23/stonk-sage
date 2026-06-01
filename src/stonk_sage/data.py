"""Point-in-time market data fetcher.

Builds a :class:`stonk_sage.contracts.MarketSnapshot` for a single ticker as of
a specific date, enforcing the no-look-ahead invariant at every layer:

* 10-K filing chosen is the most recent with ``filing_date < as_of``.
* Price history is sliced to rows with ``date <= as_of``.
* News items are filtered to publish dates ``<= as_of``.
* A final structural assertion scans every dated field before returning.

There is no LLM call anywhere in this module. It is a pure data layer that the
``/analyze`` slash command runs once per invocation; the resulting
``snapshot.json`` is then handed to the agent committee.

CLI
---
``python -m stonk_sage.data fetch AAPL --as-of 2024-06-01``
prints the path to the written snapshot JSON.
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from stonk_sage.contracts import MarketSnapshot

__all__ = [
    "EdgarIdentityMissing",
    "PriceHistoryEmpty",
    "NoFilingBeforeAsOf",
    "fetch_market_snapshot",
    "snapshot_path",
]


# ---------------------------------------------------------------------------
# Domain exceptions — distinct types so callers can react precisely.
# ---------------------------------------------------------------------------


class EdgarIdentityMissing(RuntimeError):
    """``EDGAR_IDENTITY`` env var is required by SEC fair-access policy."""


class PriceHistoryEmpty(ValueError):
    """yfinance returned no rows at or before ``as_of``."""


class NoFilingBeforeAsOf(ValueError):
    """No 10-K filing on EDGAR has ``filing_date < as_of``."""


# ---------------------------------------------------------------------------
# Pure helpers (no network, no I/O).
# ---------------------------------------------------------------------------


def _as_datetime(d: date | datetime) -> datetime:
    """Promote ``date`` to a tz-naive midnight ``datetime``; pass datetimes through."""
    if isinstance(d, datetime):
        return d
    return datetime(d.year, d.month, d.day)


def _safe_float(v: Any) -> float:
    """Coerce to float; return 0.0 on None / unparseable. yfinance.info is flaky."""
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _truncate(s: str, n: int) -> str:
    return s[: n - 3] + "..." if len(s) > n else s


def _ensure_edgar_identity() -> None:
    if not os.getenv("EDGAR_IDENTITY"):
        raise EdgarIdentityMissing(
            "EDGAR_IDENTITY env var is required by SEC fair-access policy. "
            "Set it in .env (see .env.example) or your shell environment."
        )


def _assert_no_lookahead(snapshot: MarketSnapshot, as_of: datetime) -> None:
    """Final invariant check: every dated field must be <= as_of."""
    cutoff = as_of.date()
    if snapshot.latest_10k_filing_date > cutoff:
        raise AssertionError(
            f"latest_10k_filing_date={snapshot.latest_10k_filing_date} > {cutoff}"
        )
    for item in snapshot.news_highlights:
        # Items are formatted "[YYYY-MM-DD] title" by fetch_market_snapshot.
        if item.startswith("[") and len(item) >= 12 and item[11] == "]":
            try:
                d = date.fromisoformat(item[1:11])
            except ValueError:
                continue
            if d > cutoff:
                raise AssertionError(f"news_highlights has date > as_of: {item!r}")


def snapshot_path(
    ticker: str,
    as_of: date | datetime,
    root: Path | None = None,
) -> Path:
    """Where the snapshot JSON for ``(ticker, as_of)`` is written."""
    root = root or Path("data/snapshots")
    root.mkdir(parents=True, exist_ok=True)
    d = as_of.date() if isinstance(as_of, datetime) else as_of
    return root / f"{ticker.upper()}_{d.isoformat()}.json"


# ---------------------------------------------------------------------------
# Network-touching helpers.
# ---------------------------------------------------------------------------


def _close_at_or_before(hist: Any, as_of_dt: datetime) -> float:
    """From a yfinance history DataFrame, return Close on most recent date <= as_of."""
    cutoff = as_of_dt.date()
    filtered = hist[hist.index.date <= cutoff]
    if filtered.empty:
        raise PriceHistoryEmpty(f"No trading day in price history at or before {cutoff}")
    return float(filtered["Close"].iloc[-1])


def _slice_window(hist: Any, start_d: date, end_d: date) -> Any:
    return hist[(hist.index.date >= start_d) & (hist.index.date <= end_d)]


def _fetch_history(ticker: str, as_of_date: date) -> Any:
    import yfinance as yf

    yt = yf.Ticker(ticker)
    hist = yt.history(
        start=(as_of_date - timedelta(days=400)).isoformat(),
        end=(as_of_date + timedelta(days=1)).isoformat(),
        auto_adjust=False,
    )
    if hist.empty:
        raise PriceHistoryEmpty(f"yfinance returned no rows for {ticker}")
    return hist


def _fetch_info(ticker: str) -> dict[str, Any]:
    """Best-effort yfinance.info; degrades silently when rate-limited."""
    import yfinance as yf

    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


def _fetch_news(ticker: str, as_of_date: date) -> list[str]:
    """Stubbed news fetch via yfinance.news, filtered by ``date <= as_of``."""
    import yfinance as yf

    items: list[str] = []
    try:
        raw_news = yf.Ticker(ticker).news or []
    except Exception:
        return items
    for item in raw_news:
        ts = item.get("providerPublishTime")
        if not ts:
            continue
        pub = datetime.fromtimestamp(int(ts), tz=timezone.utc).date()
        if pub > as_of_date:
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        items.append(f"[{pub.isoformat()}] {title}"[:200])
        if len(items) >= 5:
            break
    return items


def _pick_10k_before(ticker: str, as_of_date: date):
    """Return the most recent 10-K Filing with ``filing_date < as_of_date``."""
    from edgar import Company

    company = Company(ticker)
    filings = company.get_filings(form="10-K")
    for f in filings:  # edgartools yields newest first
        f_date = getattr(f, "filing_date", None)
        if f_date is None:
            continue
        if isinstance(f_date, datetime):
            f_date = f_date.date()
        if f_date < as_of_date:
            return f, f_date
    raise NoFilingBeforeAsOf(
        f"No 10-K with filing_date < {as_of_date} for {ticker}"
    )


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def fetch_market_snapshot(ticker: str, as_of: date | datetime) -> MarketSnapshot:
    """Build a :class:`MarketSnapshot` for ``ticker`` as of ``as_of``.

    Enforces no-look-ahead at every layer; final assertion runs before return.
    """
    _ensure_edgar_identity()
    as_of_dt = _as_datetime(as_of)
    as_of_date = as_of_dt.date()
    ticker_upper = ticker.upper()

    hist = _fetch_history(ticker_upper, as_of_date)
    price_at_as_of = _close_at_or_before(hist, as_of_dt)

    ttm_start = as_of_date - timedelta(days=365)
    ttm = _slice_window(hist, ttm_start, as_of_date)
    if ttm.empty:
        raise PriceHistoryEmpty(f"No TTM window for {ticker_upper}")
    ticker_return_ttm = (price_at_as_of / float(ttm["Close"].iloc[0])) - 1.0
    high_52w = float(ttm["High"].max())
    low_52w = float(ttm["Low"].min())

    spy_hist = _fetch_history("SPY", as_of_date)
    spy_at = _close_at_or_before(spy_hist, as_of_dt)
    spy_ttm = _slice_window(spy_hist, ttm_start, as_of_date)
    spy_return_ttm = (spy_at / float(spy_ttm["Close"].iloc[0])) - 1.0

    chosen_filing, chosen_filing_date = _pick_10k_before(ticker_upper, as_of_date)

    info = _fetch_info(ticker_upper)
    raw_summary = info.get("longBusinessSummary") or (
        f"{ticker_upper} most-recent 10-K filed {chosen_filing_date.isoformat()}."
    )
    business_summary = _truncate(str(raw_summary), 600)

    news_highlights = _fetch_news(ticker_upper, as_of_date)

    # ---- PIT integrity ----
    # `yfinance.Ticker(...).info` returns *current-as-of-now* fundamentals,
    # not as-of `as_of`. Surfacing those in a snapshot dated 2024-06-01 would
    # poison every downstream agent with look-ahead values (see brain's
    # backtesting-methodology). Until Stage B lands true PIT extraction from
    # the chosen 10-K's XBRL facts and (preferably) interleaved 10-Qs for
    # true TTM, we emit explicit None + mark provenance "missing" so agents
    # know not to fabricate around the gap.
    # TODO(stage-b): pull PIT financials from `chosen_filing` via edgartools
    # (revenue, gross_profit, shares_outstanding) and compute market_cap,
    # margins, multiples. Optionally interleave 10-Qs filed before `as_of`
    # for a real trailing-twelve-month view; if 10-K only, rename
    # *_ttm fields to *_latest_annual to avoid misleading agents.
    _FINANCIAL_KEYS = ("market_cap", "revenue_ttm", "gross_profit_ttm")
    _RATIO_KEYS = (
        "pe_trailing",
        "ps_trailing",
        "pb",
        "gross_margin",
        "operating_margin",
    )
    key_financials: dict[str, float | None] = {k: None for k in _FINANCIAL_KEYS}
    key_ratios: dict[str, float | None] = {k: None for k in _RATIO_KEYS}
    pit_source: dict[str, str] = {}
    for k in _FINANCIAL_KEYS:
        pit_source[f"key_financials.{k}"] = "missing"
    for k in _RATIO_KEYS:
        pit_source[f"key_ratios.{k}"] = "missing"

    snapshot = MarketSnapshot(
        ticker=ticker_upper,
        as_of=as_of_dt,
        business_summary=business_summary,
        latest_10k_filing_date=chosen_filing_date,
        key_financials=key_financials,
        key_ratios=key_ratios,
        price_summary={
            "price_at_as_of": price_at_as_of,
            "high_52w": high_52w,
            "low_52w": low_52w,
        },
        news_highlights=news_highlights,
        spy_return_same_window=spy_return_ttm,
        ticker_return_same_window=ticker_return_ttm,
        sector_return_same_window=None,
        pit_assertion=True,
        pit_source=pit_source,
    )
    _assert_no_lookahead(snapshot, as_of_dt)
    return snapshot


# ---------------------------------------------------------------------------
# CLI: ``python -m stonk_sage.data fetch <TICKER> --as-of YYYY-MM-DD``
# ---------------------------------------------------------------------------


def _cli(argv: list[str] | None = None) -> int:
    import argparse

    try:  # Best-effort .env load so EDGAR_IDENTITY is picked up automatically.
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:  # python-dotenv missing — proceed with shell env only.
        pass

    parser = argparse.ArgumentParser(prog="stonk_sage.data")
    sub = parser.add_subparsers(dest="cmd", required=True)

    fetch = sub.add_parser("fetch", help="Fetch and write a MarketSnapshot JSON.")
    fetch.add_argument("ticker", help="Ticker symbol, e.g. AAPL")
    fetch.add_argument(
        "--as-of",
        required=True,
        help="ISO date (YYYY-MM-DD). Weekends/holidays roll back to the prior close.",
    )

    args = parser.parse_args(argv)
    if args.cmd == "fetch":
        as_of = date.fromisoformat(args.as_of)
        snapshot = fetch_market_snapshot(args.ticker, as_of)
        out = snapshot_path(args.ticker, as_of)
        out.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
        print(out.as_posix())
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
