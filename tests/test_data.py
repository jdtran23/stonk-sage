"""Tests for ``stonk_sage.data``.

Network-touching tests are gated behind ``-m live`` so the default ``pytest``
run stays hermetic and fast.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from stonk_sage.contracts import MarketSnapshot
from stonk_sage import data as data_module
from stonk_sage.data import (
    EdgarIdentityMissing,
    PriceHistoryEmpty,
    _as_datetime,
    _assert_no_lookahead,
    _bars_metrics,
    _ensure_edgar_identity,
    _load_alpaca_prices,
    _news_from_alpaca,
    _parse_bar_date,
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
# Alpaca price-file parsing tests — no network.
# ---------------------------------------------------------------------------


def _bar(d: str, o: float, h: float, low: float, c: float) -> dict:
    """An Alpaca-native daily bar (single-letter keys, RFC-3339 timestamp)."""
    return {"t": f"{d}T04:00:00Z", "o": o, "h": h, "l": low, "c": c, "v": 1000}


class TestParseBarDate:
    def test_alpaca_t_key(self) -> None:
        assert _parse_bar_date({"t": "2024-05-31T04:00:00Z"}) == date(2024, 5, 31)

    def test_canonical_date_key(self) -> None:
        assert _parse_bar_date({"date": "2024-05-31"}) == date(2024, 5, 31)

    def test_missing_raises(self) -> None:
        with pytest.raises(ValueError, match="missing a date field"):
            _parse_bar_date({"c": 1.0})


class TestBarsMetrics:
    def _bars(self) -> list[dict]:
        # Deliberately unsorted; includes one bar AFTER as_of to prove filtering.
        return [
            _bar("2024-05-31", 118, 121, 117, 120),  # last <= as_of → price_at
            _bar("2023-06-02", 100, 105, 95, 100),  # TTM start → return base
            _bar("2023-12-01", 110, 130, 90, 110),  # sets high_52w=130, low_52w=90
            _bar("2024-06-15", 900, 1000, 800, 999),  # AFTER as_of → must be excluded
        ]

    def test_metrics_filter_and_compute(self) -> None:
        price_at, high, low, ret = _bars_metrics(self._bars(), date(2024, 6, 1))
        assert price_at == 120.0  # 2024-06-15 bar excluded
        assert high == 130.0
        assert low == 90.0
        assert ret == pytest.approx(0.20)  # 120 / 100 - 1

    def test_bar_on_as_of_is_included(self) -> None:
        bars = [
            _bar("2023-06-05", 100, 100, 100, 100),
            _bar("2024-06-01", 150, 150, 150, 150),  # exactly as_of
        ]
        price_at, _, _, ret = _bars_metrics(bars, date(2024, 6, 1))
        assert price_at == 150.0
        assert ret == pytest.approx(0.50)

    def test_empty_after_filter_raises(self) -> None:
        bars = [_bar("2024-07-01", 1, 1, 1, 1)]  # all after as_of
        with pytest.raises(PriceHistoryEmpty):
            _bars_metrics(bars, date(2024, 6, 1))

    def test_canonical_long_keys(self) -> None:
        bars = [
            {"date": "2023-06-05", "open": 10, "high": 10, "low": 10, "close": 10},
            {"date": "2024-05-31", "open": 20, "high": 25, "low": 18, "close": 20},
        ]
        price_at, high, low, ret = _bars_metrics(bars, date(2024, 6, 1))
        assert (price_at, high, low) == (20.0, 25.0, 10.0)
        assert ret == pytest.approx(1.0)


class TestNewsFromAlpaca:
    def test_filters_future_and_formats(self) -> None:
        raw = [
            {"created_at": "2024-05-20T10:00:00Z", "headline": "MSFT up"},
            {"created_at": "2024-06-30T10:00:00Z", "headline": "future news"},
            {"title": "no date here"},
            {"created_at": "2024-05-21", "headline": "   "},  # empty title
        ]
        out = _news_from_alpaca(raw, date(2024, 6, 1))
        assert out == ["[2024-05-20] MSFT up"]

    def test_caps_at_five(self) -> None:
        raw = [
            {"created_at": f"2024-05-0{i}", "headline": f"item {i}"}
            for i in range(1, 8)
        ]
        out = _news_from_alpaca(raw, date(2024, 6, 1))
        assert len(out) == 5

    def test_none_input(self) -> None:
        assert _news_from_alpaca(None, date(2024, 6, 1)) == []


class TestLoadAlpacaPrices:
    def _write(self, tmp_path: Path, payload: dict) -> Path:
        import json

        p = tmp_path / "alpaca_prices.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return p

    def _payload(self) -> dict:
        return {
            "bars": {
                "msft": [  # lowercase to prove case-insensitive lookup
                    _bar("2023-06-02", 100, 105, 95, 100),
                    _bar("2024-05-31", 118, 121, 117, 120),
                ],
                "SPY": [
                    _bar("2023-06-02", 400, 405, 395, 400),
                    _bar("2024-05-31", 438, 441, 437, 440),
                ],
            },
            "news": [{"created_at": "2024-05-20T10:00:00Z", "headline": "MSFT up"}],
        }

    def test_loads_ticker_spy_and_news(self, tmp_path: Path) -> None:
        path = self._write(tmp_path, self._payload())
        price_at, high, low, tret, sret, news = _load_alpaca_prices(
            path, "MSFT", date(2024, 6, 1)
        )
        assert price_at == 120.0
        assert (high, low) == (121.0, 95.0)  # TTM window is inclusive of 2023-06-02
        assert tret == pytest.approx(0.20)
        assert sret == pytest.approx(0.10)  # 440 / 400 - 1
        assert news == ["[2024-05-20] MSFT up"]

    def test_symbols_alias_accepted(self, tmp_path: Path) -> None:
        payload = self._payload()
        payload["symbols"] = payload.pop("bars")
        path = self._write(tmp_path, payload)
        price_at, *_ = _load_alpaca_prices(path, "MSFT", date(2024, 6, 1))
        assert price_at == 120.0

    def test_missing_ticker_raises(self, tmp_path: Path) -> None:
        payload = self._payload()
        del payload["bars"]["msft"]
        path = self._write(tmp_path, payload)
        with pytest.raises(PriceHistoryEmpty, match="no bars for MSFT"):
            _load_alpaca_prices(path, "MSFT", date(2024, 6, 1))

    def test_missing_spy_raises(self, tmp_path: Path) -> None:
        payload = self._payload()
        del payload["bars"]["SPY"]
        path = self._write(tmp_path, payload)
        with pytest.raises(PriceHistoryEmpty, match="no bars for SPY"):
            _load_alpaca_prices(path, "MSFT", date(2024, 6, 1))


# ---------------------------------------------------------------------------
# fetch_market_snapshot — Alpaca prices branch (hermetic via monkeypatch).
#
# The only network/EDGAR touchpoints are `_ensure_edgar_identity` and
# `_pick_10k_before`; patching both lets the whole Alpaca-file branch run
# offline so we cover provenance, the summary fallback, news filtering, and the
# snapshot-level no-look-ahead assertion.
# ---------------------------------------------------------------------------


class TestFetchMarketSnapshotPricesBranch:
    @pytest.fixture
    def patched(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(data_module, "_ensure_edgar_identity", lambda: None)
        monkeypatch.setattr(
            data_module,
            "_pick_10k_before",
            lambda ticker, as_of_date: (object(), date(2023, 7, 28)),
        )
        return data_module

    def _write(self, tmp_path: Path, payload: dict) -> Path:
        import json

        p = tmp_path / "alpaca_prices.json"
        p.write_text(json.dumps(payload), encoding="utf-8")
        return p

    def _payload(self) -> dict:
        return {
            "bars": {
                "MSFT": [
                    _bar("2023-06-02", 100, 105, 95, 100),
                    _bar("2024-05-31", 118, 121, 117, 120),
                ],
                "SPY": [
                    _bar("2023-06-02", 400, 405, 395, 400),
                    _bar("2024-05-31", 438, 441, 437, 440),
                ],
            },
            "news": [{"created_at": "2024-05-20T10:00:00Z", "headline": "MSFT up"}],
        }

    def test_builds_snapshot_from_alpaca_file(self, patched, tmp_path: Path) -> None:
        path = self._write(tmp_path, self._payload())
        snap = patched.fetch_market_snapshot("MSFT", date(2024, 6, 1), prices_path=path)
        assert snap.ticker == "MSFT"
        assert snap.price_summary["price_at_as_of"] == 120.0
        assert snap.price_summary["high_52w"] == 121.0
        assert snap.price_summary["low_52w"] == 95.0
        assert snap.ticker_return_same_window == pytest.approx(0.20)
        assert snap.spy_return_same_window == pytest.approx(0.10)
        # Provenance must record Alpaca as the price source.
        assert snap.pit_source["price_summary"] == "alpaca"
        assert snap.latest_10k_filing_date == date(2023, 7, 28)
        # Alpaca carries no business prose → filing-anchored fallback summary.
        assert "10-K filed 2023-07-28" in snap.business_summary
        assert snap.news_highlights == ["[2024-05-20] MSFT up"]
        # Financials/ratios remain unfilled (Alpaca has no fundamentals).
        assert all(v is None for v in snap.key_financials.values())
        assert snap.pit_source["key_financials.market_cap"] == "missing"

    def test_lookahead_bar_excluded_at_snapshot_level(
        self, patched, tmp_path: Path
    ) -> None:
        payload = self._payload()
        # A bar dated AFTER as_of must never become price_at_as_of.
        payload["bars"]["MSFT"].append(_bar("2024-06-20", 900, 999, 880, 950))
        path = self._write(tmp_path, payload)
        snap = patched.fetch_market_snapshot("MSFT", date(2024, 6, 1), prices_path=path)
        assert snap.price_summary["price_at_as_of"] == 120.0  # not 950

    def test_missing_spy_raises(self, patched, tmp_path: Path) -> None:
        payload = self._payload()
        del payload["bars"]["SPY"]
        path = self._write(tmp_path, payload)
        with pytest.raises(PriceHistoryEmpty, match="no bars for SPY"):
            patched.fetch_market_snapshot("MSFT", date(2024, 6, 1), prices_path=path)

    def test_feed_tag_recorded_in_pit_source(self, patched, tmp_path: Path) -> None:
        payload = self._payload()
        payload["feed"] = "iex"  # the /analyze skill records which feed it used
        path = self._write(tmp_path, payload)
        snap = patched.fetch_market_snapshot("MSFT", date(2024, 6, 1), prices_path=path)
        assert snap.pit_source["price_summary"] == "alpaca"
        assert snap.pit_source["price_feed"] == "iex"

    def test_no_feed_tag_omits_price_feed(self, patched, tmp_path: Path) -> None:
        path = self._write(tmp_path, self._payload())  # no "feed" key
        snap = patched.fetch_market_snapshot("MSFT", date(2024, 6, 1), prices_path=path)
        assert "price_feed" not in snap.pit_source


# ---------------------------------------------------------------------------
# EDGAR 403 translation — a bad EDGAR_IDENTITY must become a clear error,
# not a leaked httpx stack trace. Hermetic: httpx.Response is built locally,
# `_edgar_company` is monkeypatched, no socket is opened.
# ---------------------------------------------------------------------------


class TestEdgarAccessDenied:
    def _http_error(self, status: int):
        import httpx

        req = httpx.Request("GET", "https://data.sec.gov/submissions/CIK0000789019.json")
        resp = httpx.Response(status, request=req)
        return httpx.HTTPStatusError(f"{status}", request=req, response=resp)

    def test_403_becomes_access_denied(self, monkeypatch: pytest.MonkeyPatch) -> None:
        err = self._http_error(403)

        def boom(_ticker):
            raise err

        monkeypatch.setattr(data_module, "_edgar_company", boom)
        with pytest.raises(data_module.EdgarAccessDenied, match="403 Forbidden"):
            data_module._pick_10k_before("MSFT", date(2024, 6, 1))

    def test_403_message_names_noreply(self, monkeypatch: pytest.MonkeyPatch) -> None:
        err = self._http_error(403)
        monkeypatch.setattr(
            data_module, "_edgar_company", lambda _t: (_ for _ in ()).throw(err)
        )
        monkeypatch.setenv("EDGAR_IDENTITY", "x@users.noreply.github.com")
        with pytest.raises(data_module.EdgarAccessDenied, match="noreply"):
            data_module._pick_10k_before("MSFT", date(2024, 6, 1))

    def test_non_403_http_error_propagates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import httpx

        err = self._http_error(500)
        monkeypatch.setattr(
            data_module, "_edgar_company", lambda _t: (_ for _ in ()).throw(err)
        )
        # A 500 is not an identity problem — it must NOT be masked as AccessDenied.
        with pytest.raises(httpx.HTTPStatusError):
            data_module._pick_10k_before("MSFT", date(2024, 6, 1))


# ---------------------------------------------------------------------------
# CLI contract tests — lock the stdout shape so the `SNAPSHOT_PATH=` drift
# (docs once claimed the CLI prints that prefix; it prints a bare path) can't
# silently come back, and confirm --prices threads through to the fetcher.
# ---------------------------------------------------------------------------


class TestCliFetch:
    def test_prints_bare_snapshot_path(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys
    ) -> None:
        out_file = tmp_path / "MSFT_2024-06-01.json"
        monkeypatch.setattr(data_module, "snapshot_path", lambda t, a: out_file)
        baseline = _baseline_snapshot(datetime(2024, 6, 1))
        monkeypatch.setattr(
            data_module,
            "fetch_market_snapshot",
            lambda ticker, as_of, prices_path=None: baseline,
        )
        rc = data_module._cli(["fetch", "MSFT", "--as-of", "2024-06-01"])
        assert rc == 0
        printed = capsys.readouterr().out.strip().splitlines()[-1]
        # Contract: a BARE path, never the legacy "SNAPSHOT_PATH=" prefix.
        assert printed == out_file.as_posix()
        assert "SNAPSHOT_PATH" not in printed
        assert out_file.is_file()  # snapshot JSON was actually written

    def test_prices_flag_forwarded(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        out_file = tmp_path / "snap.json"
        monkeypatch.setattr(data_module, "snapshot_path", lambda t, a: out_file)
        captured: dict[str, object] = {}

        def fake_fetch(ticker, as_of, prices_path=None):
            captured.update(ticker=ticker, as_of=as_of, prices_path=prices_path)
            return _baseline_snapshot(datetime(2024, 6, 1))

        monkeypatch.setattr(data_module, "fetch_market_snapshot", fake_fetch)
        rc = data_module._cli(
            ["fetch", "MSFT", "--as-of", "2024-06-01", "--prices", "run/p.json"]
        )
        assert rc == 0
        assert captured["prices_path"] == "run/p.json"
        assert captured["as_of"] == date(2024, 6, 1)

    def test_no_prices_flag_passes_none(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr(
            data_module, "snapshot_path", lambda t, a: tmp_path / "s.json"
        )
        captured: dict[str, object] = {}

        def fake_fetch(ticker, as_of, prices_path=None):
            captured["prices_path"] = prices_path
            return _baseline_snapshot(datetime(2024, 6, 1))

        monkeypatch.setattr(data_module, "fetch_market_snapshot", fake_fetch)
        data_module._cli(["fetch", "MSFT", "--as-of", "2024-06-01"])
        assert captured["prices_path"] is None

    def test_domain_error_prints_clean_line_no_traceback(
        self, monkeypatch: pytest.MonkeyPatch, capsys
    ) -> None:
        def boom(ticker, as_of, prices_path=None):
            raise data_module.EdgarAccessDenied("SEC EDGAR returned 403 Forbidden. ...")

        monkeypatch.setattr(data_module, "fetch_market_snapshot", boom)
        rc = data_module._cli(["fetch", "MSFT", "--as-of", "2024-06-01"])
        assert rc == 1
        out = capsys.readouterr()
        # Clean one-line message on stderr; no traceback; nothing on stdout.
        assert "EdgarAccessDenied: SEC EDGAR returned 403" in out.err
        assert "Traceback" not in out.err
        assert out.out.strip() == ""


# ---------------------------------------------------------------------------
# Live network tests — opt-in.
# ---------------------------------------------------------------------------


@pytest.mark.live
def test_live_fetch_aapl_saturday_rolls_back_to_friday() -> None:
    """``as_of=2024-06-01`` (Saturday) → ``price_at_as_of`` is Friday 2024-05-31 close.

    Verifies no-look-ahead semantics on weekends. Requires network +
    ``EDGAR_IDENTITY`` env var (self-skips when the identity is absent).
    """
    if not os.getenv("EDGAR_IDENTITY"):
        pytest.skip("EDGAR_IDENTITY not set (needed for the 10-K lookup)")

    from stonk_sage.data import fetch_market_snapshot

    snap = fetch_market_snapshot("AAPL", date(2024, 6, 1))
    assert snap.ticker == "AAPL"
    assert snap.as_of.date() == date(2024, 6, 1)
    assert snap.latest_10k_filing_date < date(2024, 6, 1)
    assert snap.price_summary["price_at_as_of"] > 0.0
    # Friday 2024-05-31 AAPL close was ~$192 historically; loose bound to avoid
    # adjustment-policy churn in yfinance.
    assert 100.0 < snap.price_summary["price_at_as_of"] < 400.0


# ---------------------------------------------------------------------------
# Live Alpaca MCP tests — opt-in.
#
# These exercise the real Alpaca MCP server (launched via ``uvx`` over stdio,
# the same way the /analyze skill does) feeding the ``--prices`` branch of
# ``data.py``. Gated behind ``-m live`` and self-skip when prerequisites
# (uvx, Alpaca keys, EDGAR_IDENTITY) are missing, so they never break a normal
# or CI run that lacks credentials.
# ---------------------------------------------------------------------------


def _resolve_alpaca_keys() -> dict[str, str] | None:
    """Alpaca keys from env, falling back to ``.vscode/mcp.json``. None if absent."""
    key = os.getenv("ALPACA_API_KEY")
    secret = os.getenv("ALPACA_SECRET_KEY")
    if key and secret:
        return {"ALPACA_API_KEY": key, "ALPACA_SECRET_KEY": secret}
    cfg_path = Path(".vscode/mcp.json")
    if cfg_path.is_file():
        try:
            env = json.loads(cfg_path.read_text(encoding="utf-8"))["servers"]["alpaca"][
                "env"
            ]
        except (KeyError, json.JSONDecodeError):
            return None
        if env.get("ALPACA_API_KEY") and env.get("ALPACA_SECRET_KEY"):
            return {
                "ALPACA_API_KEY": env["ALPACA_API_KEY"],
                "ALPACA_SECRET_KEY": env["ALPACA_SECRET_KEY"],
            }
    return None


def _alpaca_get_stock_bars(
    symbols: str,
    start: str,
    end: str,
    keys: dict[str, str],
    timeout: float = 120.0,
) -> dict:
    """Call the live Alpaca MCP ``get_stock_bars`` tool over stdio.

    Launches ``uvx alpaca-mcp-server``, performs the MCP initialize handshake,
    and returns the parsed tool result (a dict with a ``bars`` key). Skips the
    test (rather than failing) if ``uvx`` is missing or the server never
    responds — those are environment problems, not regressions in our code.
    """
    import shutil
    import subprocess
    import threading
    import time

    uvx = shutil.which("uvx")
    if uvx is None:
        pytest.skip("uvx not on PATH (install uv to run the live Alpaca MCP tests)")

    env = dict(os.environ)
    env.update(keys)
    proc = subprocess.Popen(
        [uvx, "alpaca-mcp-server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=env,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    responses: dict[int, dict] = {}

    def _reader() -> None:
        out = proc.stdout
        assert out is not None
        for line in out:
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "id" in msg:
                responses[msg["id"]] = msg

    threading.Thread(target=_reader, daemon=True).start()

    def _send(obj: dict) -> None:
        stdin = proc.stdin
        assert stdin is not None
        stdin.write(json.dumps(obj) + "\n")
        stdin.flush()

    def _wait(req_id: int) -> dict | None:
        t0 = time.time()
        while req_id not in responses and time.time() - t0 < timeout:
            if proc.poll() is not None:
                break
            time.sleep(0.2)
        return responses.get(req_id)

    try:
        _send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "pytest", "version": "1"},
                },
            }
        )
        if not _wait(1):
            pytest.skip("Alpaca MCP did not complete the initialize handshake")
        _send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        _send(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_stock_bars",
                    "arguments": {
                        "symbols": symbols,
                        "timeframe": "1Day",
                        "start": start,
                        "end": end,
                        "limit": 10000,
                        "sort": "asc",
                    },
                },
            }
        )
        resp = _wait(2)
        if not resp or "result" not in resp:
            pytest.skip(f"Alpaca get_stock_bars returned no result: {resp!r}")
        return json.loads(resp["result"]["content"][0]["text"])
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.live
def test_live_alpaca_mcp_bars_feed_load_alpaca_prices() -> None:
    """Live Alpaca MCP bars → ``_load_alpaca_prices`` (no EDGAR needed).

    Isolates the Alpaca MCP integration + price-file parser from EDGAR so it can
    run with only Alpaca keys + uvx. ``as_of=2024-06-01`` (Saturday) ⇒ the last
    bar at or before it must be Friday 2024-05-31.
    """
    keys = _resolve_alpaca_keys()
    if keys is None:
        pytest.skip("ALPACA_API_KEY/SECRET unavailable (env or .vscode/mcp.json)")

    as_of = date(2024, 6, 1)
    start = (as_of - timedelta(days=400)).isoformat()
    payload = _alpaca_get_stock_bars("MSFT,SPY", start, as_of.isoformat(), keys)
    bars = payload.get("bars", {})
    if len(bars.get("MSFT", [])) < 100 or len(bars.get("SPY", [])) < 100:
        counts = {k: len(v) for k, v in bars.items()}
        pytest.skip(f"Alpaca returned too few bars for the window: {counts}")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        prices_file = Path(tmp) / "alpaca_prices.json"
        prices_file.write_text(json.dumps({"bars": bars}), encoding="utf-8")
        price_at, high, low, tret, sret, _news = _load_alpaca_prices(
            prices_file, "MSFT", as_of
        )

    # PIT: last MSFT bar at or before the Saturday as_of is Friday 2024-05-31.
    msft_sorted = sorted(bars["MSFT"], key=lambda b: b["t"])
    last_le = [b for b in msft_sorted if b["t"][:10] <= as_of.isoformat()][-1]
    assert last_le["t"][:10] == "2024-05-31"
    assert price_at == pytest.approx(float(last_le["c"]), rel=1e-6)
    assert low <= price_at <= high
    assert isinstance(tret, float)
    assert isinstance(sret, float)


@pytest.mark.live
def test_live_alpaca_prices_end_to_end() -> None:
    """Full path: live Alpaca MCP bars → ``data.py --prices`` → ``MarketSnapshot``.

    Requires Alpaca keys + uvx **and** ``EDGAR_IDENTITY`` (for the 10-K
    filing-date lookup). Mirrors exactly what the /analyze skill's Step 3 does.
    """
    keys = _resolve_alpaca_keys()
    if keys is None:
        pytest.skip("ALPACA_API_KEY/SECRET unavailable (env or .vscode/mcp.json)")
    if not os.getenv("EDGAR_IDENTITY"):
        pytest.skip("EDGAR_IDENTITY not set (needed for the 10-K lookup)")

    from stonk_sage.data import fetch_market_snapshot

    as_of = date(2024, 6, 1)
    start = (as_of - timedelta(days=400)).isoformat()
    payload = _alpaca_get_stock_bars("AAPL,SPY", start, as_of.isoformat(), keys)
    bars = payload.get("bars", {})
    if len(bars.get("AAPL", [])) < 100 or len(bars.get("SPY", [])) < 100:
        counts = {k: len(v) for k, v in bars.items()}
        pytest.skip(f"Alpaca returned too few bars for the window: {counts}")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        prices_file = Path(tmp) / "alpaca_prices.json"
        prices_file.write_text(
            json.dumps({"bars": bars, "news": payload.get("news", [])}),
            encoding="utf-8",
        )
        snap = fetch_market_snapshot("AAPL", as_of, prices_path=prices_file)

    assert snap.ticker == "AAPL"
    assert snap.as_of.date() == as_of
    # Provenance must record Alpaca (this is the whole point of the new path).
    assert snap.pit_source["price_summary"] == "alpaca"
    assert snap.latest_10k_filing_date < as_of

    price = snap.price_summary["price_at_as_of"]
    aapl_sorted = sorted(bars["AAPL"], key=lambda b: b["t"])
    last_le = [b for b in aapl_sorted if b["t"][:10] <= as_of.isoformat()][-1]
    assert last_le["t"][:10] == "2024-05-31"  # weekend rollback to Friday
    assert price == pytest.approx(float(last_le["c"]), rel=1e-6)
    assert snap.price_summary["low_52w"] <= price <= snap.price_summary["high_52w"]
    assert isinstance(snap.ticker_return_same_window, float)
    assert isinstance(snap.spy_return_same_window, float)
