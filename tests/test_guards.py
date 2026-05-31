"""Tests for ``stonk_sage.guards``.

Covers the 11 pytest cases called for in Plan 003 §1.4:
1.  PASS — clean BUY memo with risk alignment + quant-anchored prose.
2.  FAIL — Risk veto present but CIO recommended BUY.
3.  FAIL — position_size exceeds risk sizing band cap.
4.  PASS — Risk banded NONE and CIO is NO_ACTION (correctly).
5.  FAIL — JSON block missing.
6.  FAIL — JSON block present but CIOMemo validation fails (no edge with BUY).
7.  FAIL — vague phrase ("brand strength") with no quant anchor on a BUY memo.
8.  PASS — Rescue case: "Pricing power drove FY24 320bps per 10-K" has anchor.
9.  PASS — NO_ACTION memo is exempt from vague-edge scan.
10. FAIL — Prose has zero quantitative anchors anywhere.
11. FAIL — Risk file missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from stonk_sage.guards import (
    SIZING_CAP_PCT,
    VAGUE_PHRASES,
    check_run_dir,
    extract_cio_json_block,
    scan_vague_edges,
)


# ---------------------------------------------------------------------------
# Memo + risk JSON fixtures.
# ---------------------------------------------------------------------------


_CLEAN_MEMO_JSON = """{
  "ticker": "AAPL",
  "as_of": "2024-06-01T00:00:00",
  "recommendation": "BUY",
  "conviction": 4,
  "source_of_edge": "analytical",
  "benchmark_comparison": "AAPL ticker_return_same_window 0.18 vs spy_return_same_window 0.27 (TTM ending 2024-06-01).",
  "bull_summary": "Operating_margin of 0.32 expanded 200bps; services revenue +14% YoY per Q2 2024.",
  "bear_summary": "China revenue -10% per Q2 2024; pe_trailing of 30 prices in unlikely services growth.",
  "specialist_disagreements": "Bull cites margin expansion (key_ratios.operating_margin 0.32); Bear cites multiple compression risk (pe_trailing 30).",
  "da_critique_summary": "Consensus_too_strong false; DA flagged unanswered question on services regulatory risk.",
  "position_size_pct": 3.0,
  "time_horizon_months": 12,
  "expected_return_pct": 15.0,
  "expected_drawdown_pct": -25.0,
  "falsification_criteria": [
    "Q3 2024 services revenue growth below 8% YoY",
    "EU DMA enforcement triggers >5% App Store revenue cut"
  ]
}"""


def _memo(prose_extra: str = "", **overrides: object) -> str:
    """Build a CIO markdown with the clean memo JSON + optional prose."""
    import json

    payload = json.loads(_CLEAN_MEMO_JSON)
    payload.update(overrides)
    json_block = json.dumps(payload, indent=2)
    prose = prose_extra or (
        "## Recommendation\n"
        "BUY with conviction 4/5. Position sized at 3.0% over a 12-month horizon.\n\n"
        "## Source of Edge\n"
        "Analytical edge: operating_margin of 0.32 expanded 200bps per Q2 2024 10-Q.\n"
    )
    return f"# Investment Memo — AAPL as of 2024-06-01\n\n```json\n{json_block}\n```\n\n{prose}"


def _risk_json(
    sizing: str = "STANDARD_3_PCT",
    vetoes: list[str] | None = None,
) -> str:
    import json

    payload = {
        "recommended_sizing_band": sizing,
        "concentration_flag": False,
        "volatility_note": "price_at_as_of of 192 sits between low_52w 165 and high_52w 198.",
        "risk_factors": [
            "Bull confidence 7 with analytical edge supports STANDARD sizing.",
            "Bear confidence 5 leaves room for STANDARD vs STARTER decision.",
        ],
        "veto_reasons": vetoes or [],
    }
    return json.dumps(payload, indent=2)


def _write_run(
    tmp_path: Path,
    memo_md: str,
    risk_payload: str,
    *,
    skip_risk: bool = False,
) -> Path:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "cio_draft.md").write_text(memo_md, encoding="utf-8")
    if not skip_risk:
        (run_dir / "risk.json").write_text(risk_payload, encoding="utf-8")
    return run_dir


# ---------------------------------------------------------------------------
# 11 cases.
# ---------------------------------------------------------------------------


def test_01_pass_clean_buy(tmp_path: Path) -> None:
    run = _write_run(tmp_path, _memo(), _risk_json())
    result = check_run_dir(run)
    assert result.passed, result.render()


def test_02_fail_risk_veto_but_buy_recommended(tmp_path: Path) -> None:
    run = _write_run(tmp_path, _memo(), _risk_json(sizing="NONE", vetoes=["Bull edge null with confidence 8"]))
    result = check_run_dir(run)
    assert not result.passed
    assert any("Risk Officer issued a veto" in f for f in result.failures)


def test_03_fail_position_size_exceeds_band(tmp_path: Path) -> None:
    run = _write_run(tmp_path, _memo(position_size_pct=5.0), _risk_json(sizing="STANDARD_3_PCT"))
    result = check_run_dir(run)
    assert not result.passed
    assert any("exceeds Risk Officer band" in f for f in result.failures)


def test_04_pass_risk_none_and_no_action(tmp_path: Path) -> None:
    run = _write_run(
        tmp_path,
        _memo(
            recommendation="NO_ACTION",
            source_of_edge=None,
            position_size_pct=None,
            prose_extra="## Source of Edge\nNo identifiable edge; abstaining.",
        ),
        _risk_json(sizing="NONE"),
    )
    result = check_run_dir(run)
    assert result.passed, result.render()


def test_05_fail_json_block_missing(tmp_path: Path) -> None:
    md = "# Investment Memo — AAPL\n\nNo JSON block here. Just prose."
    run = _write_run(tmp_path, md, _risk_json())
    result = check_run_dir(run)
    assert not result.passed
    assert any("CIO JSON block invalid" in f for f in result.failures)


def test_06_fail_no_edge_with_buy_recommendation(tmp_path: Path) -> None:
    # Pydantic CIOMemo validator should reject; guards.py surfaces it.
    run = _write_run(
        tmp_path,
        _memo(source_of_edge=None, recommendation="BUY"),
        _risk_json(),
    )
    result = check_run_dir(run)
    assert not result.passed
    assert any("CIOMemo failed contract validation" in f for f in result.failures)


def test_07_fail_vague_phrase_without_anchor(tmp_path: Path) -> None:
    bad_prose = (
        "## Recommendation\nBUY with conviction 4/5.\n\n"
        "## Source of Edge\n"
        "Apple has unmatched brand strength. Quality compounder with secular growth.\n"
    )
    run = _write_run(tmp_path, _memo(prose_extra=bad_prose), _risk_json())
    result = check_run_dir(run)
    assert not result.passed
    assert any("vague edge" in f for f in result.failures)


def test_08_pass_pricing_power_with_quant_anchor(tmp_path: Path) -> None:
    rescued_prose = (
        "## Recommendation\nBUY with conviction 4/5.\n\n"
        "## Source of Edge\n"
        "Pricing power drove FY24 320bps gross margin expansion per the 10-K.\n"
    )
    run = _write_run(tmp_path, _memo(prose_extra=rescued_prose), _risk_json())
    result = check_run_dir(run)
    assert result.passed, result.render()


def test_09_pass_no_action_exempt_from_vague_scan(tmp_path: Path) -> None:
    vague_prose = (
        "## Recommendation\nNO_ACTION.\n\n"
        "## Source of Edge\n"
        "No actionable edge — brand strength and quality compounder narratives are unsupported.\n"
    )
    run = _write_run(
        tmp_path,
        _memo(
            recommendation="NO_ACTION",
            source_of_edge=None,
            position_size_pct=None,
            prose_extra=vague_prose,
        ),
        _risk_json(sizing="NONE"),
    )
    result = check_run_dir(run)
    assert result.passed, result.render()


def test_10_fail_zero_anchors_anywhere(tmp_path: Path) -> None:
    bare_prose = (
        "## Recommendation\nBuy with strong conviction.\n\n"
        "## Source of Edge\n"
        "We like the story. Management is experienced. Compelling opportunity.\n"
    )
    run = _write_run(tmp_path, _memo(prose_extra=bare_prose), _risk_json())
    result = check_run_dir(run)
    assert not result.passed
    assert any("No quantitative anchor" in f for f in result.failures)


def test_11_fail_risk_file_missing(tmp_path: Path) -> None:
    run = _write_run(tmp_path, _memo(), _risk_json(), skip_risk=True)
    result = check_run_dir(run)
    assert not result.passed
    assert any("Risk assessment unreadable" in f for f in result.failures)


# ---------------------------------------------------------------------------
# Sanity unit tests for the public helpers.
# ---------------------------------------------------------------------------


class TestExtractCIOJsonBlock:
    def test_extracts_first_fenced_block(self) -> None:
        md = 'before\n```json\n{"a": 1}\n```\nafter\n```json\n{"b": 2}\n```'
        assert extract_cio_json_block(md) == {"a": 1}

    def test_raises_on_missing(self) -> None:
        with pytest.raises(ValueError):
            extract_cio_json_block("no fences here")


class TestScanVagueEdges:
    def test_phrase_with_anchor_passes(self) -> None:
        assert scan_vague_edges("Pricing power drove FY24 320bps gross margin expansion.") == []

    def test_phrase_without_anchor_flagged(self) -> None:
        offenses = scan_vague_edges("Apple has unmatched brand strength.")
        assert any("brand strength" in o for o in offenses)

    def test_zero_anchors_anywhere_flagged(self) -> None:
        offenses = scan_vague_edges("We like the story. Compelling opportunity.")
        assert any("No quantitative anchor" in o for o in offenses)

    def test_dollar_ticker_counts_as_anchor(self) -> None:
        assert scan_vague_edges("$AAPL has pricing power across services.") == []


def test_sizing_caps_match_contract_literal() -> None:
    """SIZING_CAP_PCT keys cover every SizingBand literal."""
    assert set(SIZING_CAP_PCT.keys()) == {
        "NONE",
        "STARTER_1_PCT",
        "STANDARD_3_PCT",
        "OVERWEIGHT_5_PCT",
    }


def test_vague_phrases_are_lowercase() -> None:
    """Denylist is matched case-insensitively against lowered prose."""
    assert all(p == p.lower() for p in VAGUE_PHRASES)
