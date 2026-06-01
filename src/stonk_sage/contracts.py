"""Pydantic v2 contracts shared between the six committee agents.

These models are the *only* data structures that cross agent boundaries.
Every field bound here (string lengths, list lengths, integer ranges) is
load-bearing for the token budget (duck I5) and the no-look-ahead /
hard-rule invariants (multi-agent-finance-patterns).

This module is intentionally pure schema:
    * No LLM client imports.
    * No data-fetching imports (yfinance, edgartools, ...).
    * No business logic beyond pydantic validators.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Shared literal types
# ---------------------------------------------------------------------------

SourceOfEdge = Literal[
    "informational",
    "analytical",
    "time_horizon",
    "structural",
    "behavioral",
]
"""The five canonical sources of edge (multi-agent-finance-patterns)."""

Recommendation = Literal["BUY", "HOLD", "TRIM", "AVOID", "NO_ACTION"]
SizingBand = Literal["NONE", "STARTER_1_PCT", "STANDARD_3_PCT", "OVERWEIGHT_5_PCT"]
Direction = Literal["BULLISH", "BEARISH", "NEUTRAL"]


# ---------------------------------------------------------------------------
# MarketSnapshot — Data Analyst output, input to Bull / Bear / Risk
# ---------------------------------------------------------------------------


class MarketSnapshot(BaseModel):
    """Point-in-time snapshot of a single ticker.

    The `as_of` field is the no-look-ahead anchor: every other field in this
    object must be derivable from data available at or before `as_of`.
    """

    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=10)
    as_of: datetime
    business_summary: str = Field(max_length=600)
    latest_10k_filing_date: date
    key_financials: dict[str, float | None]
    key_ratios: dict[str, float | None]
    price_summary: dict[str, float]
    news_highlights: list[str] = Field(max_length=5)
    spy_return_same_window: float
    ticker_return_same_window: float
    sector_return_same_window: float | None = None
    pit_assertion: bool = True
    pit_source: dict[str, str] = Field(default_factory=dict)
    """Per-field provenance: dotted keys (e.g. ``key_financials.market_cap``)
    map to a source tag — ``"filing"``, ``"computed"``, ``"missing"``, or
    ``"yfinance_current"``. The last tag means the value is current-as-of-now
    (not as-of ``as_of``) and is incompatible with ``pit_assertion=True``."""

    @field_validator("ticker")
    @classmethod
    def _ticker_upper(cls, v: str) -> str:
        return v.upper()

    @field_validator("news_highlights")
    @classmethod
    def _news_items_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(
                    f"news_highlights[{i}] is {len(item)} chars; max 200"
                )
        return v

    @model_validator(mode="after")
    def _filing_not_after_as_of(self) -> MarketSnapshot:
        # `as_of` is a datetime; compare on the date component.
        if self.latest_10k_filing_date > self.as_of.date():
            raise ValueError(
                "latest_10k_filing_date must be <= as_of (no look-ahead)"
            )
        return self

    @model_validator(mode="after")
    def _pit_source_aligns_with_assertion(self) -> MarketSnapshot:
        # A PIT-asserted snapshot cannot carry values labeled as
        # current-as-of-now. The two are semantically incompatible.
        if self.pit_assertion and any(
            v == "yfinance_current" for v in self.pit_source.values()
        ):
            offending = sorted(
                k for k, v in self.pit_source.items() if v == "yfinance_current"
            )
            raise ValueError(
                "pit_assertion=True but pit_source labels "
                f"{offending!r} as 'yfinance_current' (live, not as-of). "
                "Either drop those fields, mark them 'missing', or set "
                "pit_assertion=False."
            )
        return self


# ---------------------------------------------------------------------------
# Thesis — Bull and Bear share this schema
# ---------------------------------------------------------------------------


class Thesis(BaseModel):
    """A directional thesis from either the Bull or the Bear specialist."""

    model_config = ConfigDict(extra="forbid")

    agent_id: Literal["bull", "bear"]
    recommendation_direction: Direction
    headline: str = Field(max_length=200)
    key_drivers: list[str] = Field(max_length=5)
    dominant_driver: str = Field(max_length=200)
    source_of_edge: SourceOfEdge | None = None
    key_risk: str = Field(max_length=300)
    evidence: list[str] = Field(max_length=5)
    confidence: int = Field(ge=1, le=10)

    @field_validator("key_drivers", "evidence")
    @classmethod
    def _items_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(f"item[{i}] is {len(item)} chars; max 200")
        return v


# ---------------------------------------------------------------------------
# RiskAssessment — Risk Officer output
# ---------------------------------------------------------------------------


class RiskAssessment(BaseModel):
    """Risk Officer's sizing + veto decision."""

    model_config = ConfigDict(extra="forbid")

    recommended_sizing_band: SizingBand
    concentration_flag: bool
    volatility_note: str = Field(max_length=300)
    risk_factors: list[str] = Field(max_length=5)
    veto_reasons: list[str] = Field(max_length=3)

    @field_validator("risk_factors")
    @classmethod
    def _risk_factors_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(f"risk_factors[{i}] is {len(item)} chars; max 200")
        return v

    @field_validator("veto_reasons")
    @classmethod
    def _veto_reasons_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(f"veto_reasons[{i}] is {len(item)} chars; max 200")
        return v


# ---------------------------------------------------------------------------
# DevilsAdvocateCritique — Devil's Advocate output
# ---------------------------------------------------------------------------


class DevilsAdvocateCritique(BaseModel):
    """The Devil's Advocate's structured critique of the bull/bear consensus."""

    model_config = ConfigDict(extra="forbid")

    bull_blind_spots: list[str] = Field(max_length=3)
    bear_blind_spots: list[str] = Field(max_length=3)
    consensus_too_strong: bool
    unanswered_questions: list[str] = Field(max_length=5)
    recommendation_constraint: str = Field(max_length=300)

    @field_validator(
        "bull_blind_spots",
        "bear_blind_spots",
        "unanswered_questions",
    )
    @classmethod
    def _items_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(f"item[{i}] is {len(item)} chars; max 200")
        return v


# ---------------------------------------------------------------------------
# CIOMemo — final CIO output
# ---------------------------------------------------------------------------


class CIOMemo(BaseModel):
    """The CIO's final, structured memo.

    Hard rules enforced structurally (so neither the LLM nor downstream code
    can fake them):

    * If `source_of_edge is None`, the recommendation MUST be `NO_ACTION`.
      Rationale: no identified edge ⇒ no actionable view.
    * If `recommendation == "NO_ACTION"`, `position_size_pct` MUST be `None`.
      Rationale: a sized non-action is incoherent.
    * If `recommendation == "NO_ACTION"`, `time_horizon_months`,
      `expected_return_pct`, and `expected_drawdown_pct` MUST all be `None`.
      Rationale: horizon and return projections on a non-action are incoherent.
    * If `recommendation == "NO_ACTION"`, `conviction` MUST be `<= 2`.
      Rationale: ``conviction`` reads as *investment* conviction; a high value
      on a non-action memo signals the wrong axis.
    """

    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=10)
    as_of: datetime
    recommendation: Recommendation
    conviction: int = Field(ge=1, le=5)
    source_of_edge: SourceOfEdge | None = None
    benchmark_comparison: str = Field(max_length=500)
    bull_summary: str = Field(max_length=500)
    bear_summary: str = Field(max_length=500)
    specialist_disagreements: str = Field(max_length=500)
    da_critique_summary: str = Field(max_length=300)
    position_size_pct: float | None = Field(default=None, ge=0.0, le=10.0)
    time_horizon_months: int | None = Field(default=None, ge=1, le=120)
    expected_return_pct: float | None = None
    expected_drawdown_pct: float | None = None
    falsification_criteria: list[str] = Field(max_length=5)

    @field_validator("ticker")
    @classmethod
    def _ticker_upper(cls, v: str) -> str:
        return v.upper()

    @field_validator("falsification_criteria")
    @classmethod
    def _falsification_bounded(cls, v: list[str]) -> list[str]:
        for i, item in enumerate(v):
            if len(item) > 200:
                raise ValueError(
                    f"falsification_criteria[{i}] is {len(item)} chars; max 200"
                )
        return v

    @model_validator(mode="after")
    def _enforce_hard_rules(self) -> CIOMemo:
        # Hard rule 1: no edge ⇒ no action.
        if self.source_of_edge is None and self.recommendation != "NO_ACTION":
            raise ValueError(
                "source_of_edge is None but recommendation is "
                f"{self.recommendation!r}; must be 'NO_ACTION' "
                "(brain hard rule: no edge ⇒ no action)"
            )
        # Hard rule 2: NO_ACTION ⇒ no sizing.
        if self.recommendation == "NO_ACTION" and self.position_size_pct is not None:
            raise ValueError(
                "recommendation is 'NO_ACTION' but position_size_pct is "
                f"{self.position_size_pct!r}; must be None"
            )
        # Hard rule 3: NO_ACTION ⇒ no horizon / return / drawdown projections.
        # A horizon or return projection on a non-action recommendation is
        # incoherent; CIOs commonly emit 0 ("no horizon") which then trips the
        # ge=1 floor. Force explicit None across all three projection fields.
        if self.recommendation == "NO_ACTION":
            for field_name in (
                "time_horizon_months",
                "expected_return_pct",
                "expected_drawdown_pct",
            ):
                value = getattr(self, field_name)
                if value is not None:
                    raise ValueError(
                        f"recommendation is 'NO_ACTION' but {field_name} is "
                        f"{value!r}; must be None"
                    )
        # Hard rule 4: NO_ACTION ⇒ conviction <= 2.
        # `conviction` reads as investment conviction; a NO_ACTION memo with
        # conviction 4 or 5 implies high confidence in the wrong axis.
        if self.recommendation == "NO_ACTION" and self.conviction > 2:
            raise ValueError(
                f"recommendation is 'NO_ACTION' but conviction is "
                f"{self.conviction}; must be <= 2 (no-action memos cannot "
                "carry high investment conviction)"
            )
        return self


# ---------------------------------------------------------------------------
# Facade types — the only entry/exit shapes the caller sees.
# ---------------------------------------------------------------------------


class CommitteeInput(BaseModel):
    """Input to `run_committee(...)`.

    Accepts either a `date` or a `datetime` for `as_of` and normalizes to
    `datetime` (midnight, tz-naive) so downstream agents have a single type.
    """

    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(min_length=1, max_length=10)
    as_of: datetime

    @field_validator("ticker")
    @classmethod
    def _ticker_upper(cls, v: str) -> str:
        return v.upper()

    @field_validator("as_of", mode="before")
    @classmethod
    def _coerce_as_of(cls, v: object) -> object:
        # Accept date and promote to datetime at midnight; pass datetimes
        # and ISO strings through to pydantic's native parsing.
        if isinstance(v, datetime):
            return v
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day)
        return v


class CommitteeResult(BaseModel):
    """The full result returned by `run_committee(...)`."""

    model_config = ConfigDict(extra="forbid")

    memo: CIOMemo
    memo_markdown: str
    trace_id: str
