"""Tests for `stonk_sage.contracts`.

These verify:
    * round-trip JSON serialization for every contract,
    * list/string length bounds (token-budget invariant),
    * integer range bounds,
    * the two CIO hard rules (no edge ⇒ no action; no action ⇒ no size).
"""

from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from stonk_sage import (
    CIOMemo,
    CommitteeInput,
    CommitteeResult,
    DevilsAdvocateCritique,
    MarketSnapshot,
    RiskAssessment,
    Thesis,
)


# ---------------------------------------------------------------------------
# Fixtures: minimal valid instances for each contract.
# ---------------------------------------------------------------------------


def _valid_snapshot() -> MarketSnapshot:
    return MarketSnapshot(
        ticker="aapl",  # lowercased on purpose; validator should upper
        as_of=datetime(2024, 6, 30, 0, 0, 0),
        business_summary="Apple designs consumer electronics.",
        latest_10k_filing_date=date(2023, 11, 3),
        key_financials={"revenue": 383_000.0, "net_income": 97_000.0},
        key_ratios={"pe": 30.0, "ev_ebitda": 22.0},
        price_summary={"price_at_as_of": 193.0, "high_52w": 200.0, "low_52w": 165.0},
        news_highlights=["iPhone 15 launch", "Services revenue at record"],
        spy_return_same_window=0.15,
        ticker_return_same_window=0.08,
        sector_return_same_window=0.12,
    )


def _valid_thesis(agent: str = "bull") -> Thesis:
    return Thesis(
        agent_id=agent,  # type: ignore[arg-type]
        recommendation_direction="BULLISH" if agent == "bull" else "BEARISH",
        headline="Services margin expansion is durable.",
        key_drivers=["Services mix", "Buybacks", "Vision Pro optionality"],
        dominant_driver="Services mix",
        source_of_edge="analytical",
        key_risk="China demand softness.",
        evidence=["Services gross margin 70%+", "Buybacks $90B/yr"],
        confidence=7,
    )


def _valid_risk() -> RiskAssessment:
    return RiskAssessment(
        recommended_sizing_band="STANDARD_3_PCT",
        concentration_flag=False,
        volatility_note="Beta ~1.2; drawdowns in 2022 around 30%.",
        risk_factors=["China exposure", "Regulatory"],
        veto_reasons=[],
    )


def _valid_da() -> DevilsAdvocateCritique:
    return DevilsAdvocateCritique(
        bull_blind_spots=["Ignores AI capex risk"],
        bear_blind_spots=["Underweights buyback floor"],
        consensus_too_strong=False,
        unanswered_questions=["What if Services growth decelerates to 5%?"],
        recommendation_constraint="Cap sizing at STANDARD unless conviction >= 4.",
    )


def _valid_memo(**overrides: object) -> CIOMemo:
    base: dict[str, object] = dict(
        ticker="AAPL",
        as_of=datetime(2024, 6, 30),
        recommendation="BUY",
        conviction=4,
        source_of_edge="analytical",
        benchmark_comparison=(
            "AAPL +8% vs SPY +15% trailing 12m; underperformance reflects "
            "China overhang now in the price."
        ),
        bull_summary="Services mix + buybacks compound steadily.",
        bear_summary="China + multiple compression risk.",
        specialist_disagreements="Bull and Bear disagree on China severity.",
        da_critique_summary="DA flags AI capex blind spot.",
        position_size_pct=3.0,
        time_horizon_months=24,
        expected_return_pct=0.12,
        expected_drawdown_pct=-0.25,
        falsification_criteria=["Services growth < 5% for 2 quarters"],
    )
    base.update(overrides)
    return CIOMemo(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# 1. Round-trip JSON for every contract.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "instance,model_cls",
    [
        (_valid_snapshot(), MarketSnapshot),
        (_valid_thesis("bull"), Thesis),
        (_valid_thesis("bear"), Thesis),
        (_valid_risk(), RiskAssessment),
        (_valid_da(), DevilsAdvocateCritique),
        (_valid_memo(), CIOMemo),
    ],
)
def test_roundtrip_json(instance, model_cls) -> None:
    raw = instance.model_dump_json()
    restored = model_cls.model_validate_json(raw)
    assert restored == instance


def test_ticker_uppercased() -> None:
    snap = _valid_snapshot()
    assert snap.ticker == "AAPL"


# ---------------------------------------------------------------------------
# 2-3. MarketSnapshot bounds.
# ---------------------------------------------------------------------------


def test_news_highlights_too_many() -> None:
    with pytest.raises(ValidationError):
        MarketSnapshot(
            **{
                **_valid_snapshot().model_dump(),
                "news_highlights": [f"item {i}" for i in range(6)],
            }
        )


def test_news_item_too_long() -> None:
    with pytest.raises(ValidationError):
        MarketSnapshot(
            **{
                **_valid_snapshot().model_dump(),
                "news_highlights": ["x" * 250],
            }
        )


def test_filing_after_as_of_rejected() -> None:
    with pytest.raises(ValidationError):
        MarketSnapshot(
            **{
                **_valid_snapshot().model_dump(),
                "latest_10k_filing_date": date(2025, 1, 1),
            }
        )


# ---------------------------------------------------------------------------
# 4. Thesis bounds.
# ---------------------------------------------------------------------------


def test_thesis_confidence_out_of_range() -> None:
    with pytest.raises(ValidationError):
        Thesis(
            **{
                **_valid_thesis().model_dump(),
                "confidence": 11,
            }
        )


# ---------------------------------------------------------------------------
# 5-8. CIO hard rules.
# ---------------------------------------------------------------------------


def test_cio_valid_buy_with_edge() -> None:
    # Positive control: edge + BUY is allowed.
    memo = _valid_memo(source_of_edge="analytical", recommendation="BUY")
    assert memo.recommendation == "BUY"


def test_cio_buy_without_edge_rejected() -> None:
    with pytest.raises(ValidationError):
        _valid_memo(source_of_edge=None, recommendation="BUY")


def test_cio_no_action_with_size_rejected() -> None:
    with pytest.raises(ValidationError):
        _valid_memo(
            source_of_edge=None,
            recommendation="NO_ACTION",
            position_size_pct=2.0,
        )


def test_cio_no_action_with_horizon_rejected() -> None:
    """NO_ACTION may not carry a time_horizon_months projection."""
    with pytest.raises(ValidationError, match="time_horizon_months"):
        _valid_memo(
            source_of_edge=None,
            recommendation="NO_ACTION",
            position_size_pct=None,
            conviction=2,
            time_horizon_months=12,
            expected_return_pct=None,
            expected_drawdown_pct=None,
        )


def test_cio_no_action_with_expected_return_rejected() -> None:
    """NO_ACTION may not carry an expected_return_pct projection."""
    with pytest.raises(ValidationError, match="expected_return_pct"):
        _valid_memo(
            source_of_edge=None,
            recommendation="NO_ACTION",
            position_size_pct=None,
            conviction=2,
            time_horizon_months=None,
            expected_return_pct=0.10,
            expected_drawdown_pct=None,
        )


def test_cio_no_action_with_high_conviction_rejected() -> None:
    """NO_ACTION caps conviction at 2 (investment conviction, not decision)."""
    with pytest.raises(ValidationError, match="conviction"):
        _valid_memo(
            source_of_edge=None,
            recommendation="NO_ACTION",
            position_size_pct=None,
            conviction=4,
            time_horizon_months=None,
            expected_return_pct=None,
            expected_drawdown_pct=None,
        )


def test_cio_valid_no_action() -> None:
    memo = _valid_memo(
        source_of_edge=None,
        recommendation="NO_ACTION",
        position_size_pct=None,
        conviction=2,
        time_horizon_months=None,
        expected_return_pct=None,
        expected_drawdown_pct=None,
    )
    assert memo.recommendation == "NO_ACTION"
    assert memo.position_size_pct is None
    assert memo.time_horizon_months is None
    assert memo.expected_return_pct is None
    assert memo.expected_drawdown_pct is None
    assert memo.conviction == 2


# ---------------------------------------------------------------------------
# CommitteeInput / CommitteeResult facades.
# ---------------------------------------------------------------------------


def test_committee_input_accepts_date_and_datetime() -> None:
    from_date = CommitteeInput(ticker="msft", as_of=date(2024, 6, 30))
    from_dt = CommitteeInput(ticker="MSFT", as_of=datetime(2024, 6, 30, 0, 0))
    assert from_date.as_of == from_dt.as_of
    assert from_date.ticker == "MSFT"


def test_committee_result_roundtrip() -> None:
    result = CommitteeResult(
        memo=_valid_memo(),
        memo_markdown="# AAPL memo\n...",
        trace_id="trace-abc-123",
    )
    restored = CommitteeResult.model_validate_json(result.model_dump_json())
    assert restored == result
