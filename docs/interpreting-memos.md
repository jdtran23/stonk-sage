# Interpreting a stonk-sage Memo

> A guide for **reading** the memos `/analyze` produces — what every field means, what to trust, what to distrust, and how to spot when the committee is bullshitting you.

This guide complements the [README](../README.md) (which covers how the system runs) and the [brain instruction files](../.github/instructions/) (which cover what each agent *does*). This file covers what to do once you have a memo in your hand.

---

## TL;DR — Read in This Order

1. **The JSON block first.** Everything else is narrative; the JSON is the auditable contract.
2. **`recommendation` + `source_of_edge` + `conviction`** — the three-field summary.
3. **`falsification_criteria`** — if these are vague ("narrative changes"), distrust the whole memo.
4. **`specialist_disagreements`** — where the actual signal lives.
5. **`da_critique_summary`** — the contrarian voice. If DA constrained the CIO, take that seriously.
6. **Bull and Bear summaries** — must differ. If they don't, groupthink.
7. **Benchmark comparison** — "vs SPY" is the mandatory hurdle, not a footnote.

---

## The JSON Block — Field by Field

The CIO emits a structured JSON object first; pydantic re-validates it via `contracts.CIOMemo`. These fields are load-bearing — agents cannot fabricate around them.

### Decision Fields

| Field | Type | What it means |
|---|---|---|
| `ticker` | string | Uppercase ticker symbol |
| `as_of` | ISO datetime | Point-in-time anchor. **Every other field reflects information available at or before this date** (no look-ahead) |
| `recommendation` | `BUY` \| `HOLD` \| `TRIM` \| `AVOID` \| `NO_ACTION` | The action call |
| `conviction` | 1–5 (int) | Investment conviction in the call. **Capped at 2 for NO_ACTION** (a no-action memo can't carry high investment conviction — wrong axis) |
| `source_of_edge` | `informational` \| `analytical` \| `time_horizon` \| `structural` \| `behavioral` \| `null` | The mechanism by which the committee believes it has edge over the market consensus. **`null` ⇒ recommendation MUST be NO_ACTION** (no edge ⇒ no action — structurally enforced) |

### Sizing & Horizon

| Field | Type | What it means |
|---|---|---|
| `position_size_pct` | 0–10 (float) or `null` | Percentage of portfolio. **`null` for NO_ACTION** |
| `time_horizon_months` | 1–120 (int) or `null` | Expected holding period. **`null` for NO_ACTION** |
| `expected_return_pct` | float or `null` | Base-case return over the horizon |
| `expected_drawdown_pct` | float or `null` | Expected worst-case unrealized loss along the way (usually negative) |

**Read the asymmetry.** A 30% expected return at a 10% expected drawdown is a good setup; 5% expected return at 25% drawdown is not.

### The Narrative-Compression Fields

| Field | Max length | What to look for |
|---|---|---|
| `benchmark_comparison` | 500 chars | `ticker_return_same_window` vs `spy_return_same_window` with explicit numbers. This is the **"why not just buy SPY?"** hurdle |
| `bull_summary` | 500 chars | The bull's argument, with snapshot field citations |
| `bear_summary` | 500 chars | The bear's argument, with snapshot field citations |
| `specialist_disagreements` | 500 chars | **Where the real information lives.** The crux of what Bull and Bear disagreed on |
| `da_critique_summary` | 300 chars | The Devil's Advocate's biggest constraint on the decision |

### `falsification_criteria` — The Most Important Field

A list of up to 5 specific events that would **prove the thesis wrong**.

✅ **Good** (observable, dated, specific):
- `"Q3 2024 services revenue growth below 8% YoY"`
- `"EU DMA enforcement triggers >5% App Store revenue cut"`
- `"AAPL closes above price_summary.high_52w=$199.62 while ticker_return_same_window exceeds spy_return_same_window"`

❌ **Bad** (vague, subjective, unobservable):
- `"Narrative shifts"`
- `"AI hype fades"`
- `"Management loses focus"`

If `falsification_criteria` is vague, **the entire memo is suspect** — the thesis can't fail, so it can't be tested, so it isn't a thesis. (`guards.py` doesn't currently fail vague falsifications, but a reader should.)

---

## The Prose Sections

The CIO's prose follows a fixed template after the JSON block. Each section has a specific job.

### `## Recommendation`
One-liner restating the JSON: `BUY/HOLD/SELL/NO_ACTION with conviction N/5. Position sized at X% over an N-month horizon.` For NO_ACTION the prose explicitly says horizon/return/drawdown projections are not applicable.

### `## Source of Edge`
1–2 paragraphs justifying *why* the committee believes it has edge. Should explicitly name the edge type (informational/analytical/time_horizon/structural/behavioral). If `source_of_edge` is `null`, this section explains why no action is taken.

**Reader's check:** does the edge claim survive substitution? Replace the ticker with "any liquid mega-cap" — does the argument still hold? If yes, that's not an edge, that's a description of the asset class.

### `## What the Specialists Said`
A bullet per specialist (Bull, Bear, Risk Officer, Devil's Advocate). Should be **proportional** — Bear shouldn't be a footnote even if you side with Bull. The committee's job is to surface dissent, not synthesize it away.

**Reader's check:** the Bull and Bear paragraphs should disagree on a specific cruxy fact (a number, a filing reference, a structural claim). If they're talking past each other on different aspects, the memo is incoherent.

### `## Falsification`
Expansion of `falsification_criteria` from the JSON. Same standard: observable, specific, dated.

### `## Benchmark Context`
**Mandatory.** Should cite `ticker_return_same_window` and `spy_return_same_window` with their actual numbers. The implicit question every active selection answers: **why not just hold SPY / VTI / cash instead?** If the expected excess return doesn't clear costs + taxes + opportunity cost, the right answer is NO_ACTION.

---

## How to Distrust a Memo (Reader's Skeptic Mode)

The system already has guardrails, but no software catches every form of bullshit. Here are reader-level checks worth running.

### Red flags in the JSON
- `conviction: 5` on a BUY/SELL — be 2x more skeptical
- `source_of_edge: "behavioral"` with no observable falsifier — most "behavioral edge" claims are just "I disagree with the market"
- `expected_return_pct >> 30%` over a < 12-month horizon — almost always overconfident
- `expected_drawdown_pct: 0` — impossible; equity positions always have downside risk
- `falsification_criteria` containing "if the story changes" or any unobservable trigger

### Red flags in the prose
- Bull and Bear say almost the same thing in different valence — committee groupthought
- Numbers in the prose **don't match** numbers in the JSON — drift; trust the JSON
- Specific dated catalysts (e.g., "WWDC June 10 reveal") that **don't appear in the snapshot's `news_highlights`** — agent hallucinated. The Devil's Advocate is supposed to catch this; check that the DA critique addresses it
- Vague phrases without quantitative anchors: "brand strength", "quality compounder", "pricing power", "moat" — `guards.py` blocks these for BUY/SELL memos, but they can slip through on edge cases. For a NO_ACTION memo, the guard is intentionally relaxed
- The "Specialist Disagreements" section is empty or wishy-washy — the committee converged via low-effort consensus, not via actual debate

### When NO_ACTION is correct (counter-intuitive)
- **All fundamentals null** (Stage A data limitation today) — the right call is NO_ACTION, regardless of price action
- **Risk Officer vetoed** — the CIO is bound to NO_ACTION; structural rule
- **Bull source_of_edge = null** and **Bear source_of_edge = null** — no one claims an edge; defaulting to action would be Russian roulette
- **Excess-return vs SPY < 2% annualized** after costs/taxes — the spread doesn't justify single-name risk

### When to trust a BUY/SELL more
- `source_of_edge` is `analytical` or `structural` (the two hardest to fake)
- `falsification_criteria` cite specific numbers / filings / dates
- Bear case is substantive, not perfunctory (the DA pushes back when Bear phones it in)
- Multiple non-overlapping evidence sources (the snapshot + DA's `unanswered_questions` + Risk's `risk_factors` triangulate, not all citing the same one datapoint)

---

## What the Specialists Are Optimizing For

Understanding each agent's incentive helps decode their output.

| Agent | Job | Bias to watch for |
|---|---|---|
| **Data Analyst** | Compresses snapshot into prose; no opinions | Sometimes paraphrases numbers loosely. Trust the snapshot JSON, not the digest |
| **Bull** | Strongest case FOR | Narrative fallacy; confirmation bias; inventing catalysts |
| **Bear** | Strongest case AGAINST | Often defaults to NEUTRAL when data is thin (abdication, not analysis) |
| **Risk Officer** | Position sizing + veto authority | Tends conservative (sizing band NONE/STARTER). Veto reasons should cite **specific** rule violations |
| **Devil's Advocate** | Adversarial reviewer (different model family) | The contrarian role. When DA says NO_ACTION, the CIO is structurally bound. The most expensive dispatch in the pipeline (Opus by default) |
| **CIO** | Final synthesizer | Bound by Risk veto and DA constraints. Cannot recommend BUY/SELL if either rules it out |

---

## Worked Example — Interpreting the AAPL 2024-06-01 Memo

The memo at `examples/AAPL_2024-06-01_latest.md` is a real run. Walking through it as a reader:

**JSON quick-read:**
```json
{
  "recommendation": "NO_ACTION",
  "conviction": 1,
  "source_of_edge": null,
  "position_size_pct": null,
  ...
}
```
→ NO_ACTION at conviction 1/5 with no edge. This is the system saying "we found nothing actionable here." Trust it; don't fight it.

**Why NO_ACTION?**
- `da_critique_summary` mentions "Risk vetoed due to all fundamentals + news missing"
- `bear_summary` mentions `pit_source.key_ratios.operating_margin='missing'`
→ This isn't a real "AAPL is a bad investment" memo. It's a "we don't have the data to take a position" memo. Different signal.

**`falsification_criteria` quality check:**
- ✅ "A PIT snapshot provides non-null key_financials.revenue_ttm and key_ratios.operating_margin for 2024-06-01"
- ✅ "A PIT-consistent return source confirms ticker_return_same_window is total return and dividend-adjusted"
→ Observable, specific. The thesis ("we should not act on this snapshot") is falsifiable by getting better data.

**`benchmark_comparison` quality check:**
- "AAPL ticker_return_same_window was 6.24% versus SPY spy_return_same_window 23.24%"
- AAPL underperformed by 17 pp — a real number, not narrative
→ Passes the "vs SPY" hurdle test (the answer is "SPY clearly won").

**Specialist disagreement (the cruxy bit):**
- Bull framed the 17pp gap as behavioral mispricing (mean-reversion setup)
- Bear and Risk said: no fundamentals available, can't validate that hypothesis
→ The disagreement is **not about AAPL** — it's about whether the available evidence is sufficient. That's an honest disagreement and produces an honest "we don't know yet" answer.

**What would change this to BUY?** Land Stage B of the data fix (XBRL extraction from the 10-K). Then a re-run might surface a real divergent thesis with non-null margins, P/E, and revenue growth to anchor on.

---

## Recurring Questions

### "Why is everything NO_ACTION right now?"
Stage A of the data layer leaves `key_financials` and `key_ratios` all null (the alternative — using current `yfinance.info` values — caused a worse PIT bug). Until Stage B (XBRL extraction from 10-K via edgartools) lands, every run will correctly conclude NO_ACTION. The system is biased toward inaction under sparse data **on purpose**.

### "Can I trust a BUY memo to actually make money?"
No. This is research scaffolding for experimentation, not a recommendation system. Even with perfect data, LLM-generated theses regularly fail. The architecture's value is in producing **structured, falsifiable, dissent-preserving** memos that are easier to argue with and learn from than free-text outputs. Treat it like a research analyst's first draft — useful for narrowing your search, not a substitute for your own work.

### "How often should I re-run for the same ticker?"
- **Same as_of date:** the snapshot is cached; re-running produces different agent text (LLM non-determinism) but same data. Useful for the **3-run acceptance ritual** (3 runs, ≥2 passing).
- **Newer as_of date:** new snapshot, fresh data — meaningful re-analysis.

### "What if the guards fail?"
The skill's Step 9 stops the pipeline. Read the failure output:
- **Contract validation error** — usually a CIO field violating a hard rule (length cap, NO_ACTION + non-null projection). Inspect `<RUN_DIR>/cio_draft.md`. Often re-running with a fresh UUID surfaces a memo that passes; persistent failures point at agent prompts.
- **Risk Officer veto not honored** — the CIO recommended action despite a veto. Should not happen often; if it does, the CIO prompt needs tightening.
- **Vague-edge guard failed** — the prose contained "brand strength" / "quality compounder" / etc. without a quantitative anchor. The CIO needs to cite numbers, not narrative.

### "Why doesn't the memo tell me when to sell?"
It does, indirectly. The `falsification_criteria` are exit triggers — if any of them happens, the thesis is invalidated and the position should be re-evaluated. There's no explicit stop-loss in the contract because price-based stops on fundamental theses are usually wrong (see `behavioral-finance.instructions.md` on loss aversion).

---

## Cross-References to the Brain

If you want to go deeper on what the agents are doing under the hood:

| Topic | Brain file |
|---|---|
| What makes a good investment thesis | `.github/instructions/equity-research.instructions.md` |
| Why NO_ACTION is the default (market-efficiency burden of proof) | `.github/instructions/equity-research.instructions.md` § Edge Identification |
| Position sizing rules behind `recommended_sizing_band` | `.github/instructions/risk-portfolio.instructions.md` |
| Why the committee has the structure it does | `.github/instructions/multi-agent-finance-patterns.instructions.md` |
| What sources of edge are recognized | `.github/instructions/equity-research.instructions.md` § Edge Identification |
| Cognitive biases the committee is designed to counter | `.github/instructions/behavioral-finance.instructions.md` |

---

**This is not financial advice.** stonk-sage is a research scaffolding project. Memos are LLM output. Don't trade on them without doing your own work.
