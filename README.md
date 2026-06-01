# stonk-sage

A 6-agent AI investment-research committee that runs entirely on top of GitHub Copilot's `task` tool — no third-party LLM API keys required. Built around a versioned brain of finance-domain instruction files; agents dispatch through the Copilot CLI's slash-command surface and produce a structured investment memo with hard guardrails.

> **This is not financial advice.** stonk-sage is a research scaffolding project for experimentation. Memos are LLM output, not professional analysis. Don't trade on its output without doing your own work.

---

## Architecture

```
┌─────────────────┐
│ data.py         │  yfinance + edgartools, no-look-ahead invariant
│ (no LLM)        │  → MarketSnapshot JSON
└────────┬────────┘
         ▼
┌─────────────────┐
│ Data Analyst    │  claude-haiku-4.5 — structured digest
└────────┬────────┘
         ▼
┌────────┴────────┐
│ Bull       Bear │  claude-sonnet-4.6  |  gpt-5.4
│ Risk Officer    │  claude-haiku-4.5    (parallel)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Devil's         │  claude-opus-4.8 (different family from CIO)
│ Advocate        │
└────────┬────────┘
         ▼
┌─────────────────┐
│ CIO             │  gpt-5.5 — final memo (Markdown + embedded JSON)
└────────┬────────┘
         ▼
┌─────────────────┐
│ guards.py       │  hard-rule re-validate + vague-edge scan
└────────┬────────┘
         ▼
   examples/<TICKER>_<DATE>_<UUID>.md   (only on PASS)
```

**Cross-family invariants** (non-negotiable):
- Bull (Claude) ≠ Bear (GPT) — prevents one-family consensus
- Devil's Advocate (Claude) ≠ CIO (GPT) — prevents the synthesizer from rubber-stamping its own critique

**No-edge ⇒ no-action** is enforced structurally by `contracts.CIOMemo`. `guards.py` re-validates after the fact and additionally fails the memo for vague prose ("brand strength", "quality compounder", etc.) without a quantitative anchor.

---

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (Windows ARM64: install via `pip install --user uv` to avoid the broken aarch64 native installer)
- GitHub Copilot subscription (for the `task` tool that dispatches agents)
- An `EDGAR_IDENTITY` for SEC fair-access compliance (`Your Name your.email@example.com`)

### Install
```pwsh
git clone https://github.com/jdtran23/stonk-sage.git
cd stonk-sage
uv sync

cp .env.example .env
# edit .env and set EDGAR_IDENTITY — the CLI auto-loads .env via python-dotenv
```

### Verify
```pwsh
uv run pytest -q
# Expect: 60 passed, 1 deselected   (live network test gated behind -m live)
```

---

## Usage

### One command, in Copilot CLI from this repo

Start Copilot CLI in the `stonk-sage` working directory. Then:

```
/analyze AAPL 2024-06-01
```

That dispatches the full 6-agent pipeline, runs the post-CIO guards, and (on pass) publishes the memo to `examples/AAPL_2024-06-01_<uuid>.md`. The skill prints the memo back to chat so you can read it inline.

**For interpreting the memo it produces, see [`docs/interpreting-memos.md`](docs/interpreting-memos.md).**

`/analyze` is a project skill at `.github/skills/analyze/SKILL.md`. It's loaded by Copilot CLI's `/skills` mechanism. (Prompt files at `.github/prompts/*.prompt.md` are a VS Code Copilot Chat feature and do not work in Copilot CLI — that was the original design and it was wrong.)

### Direct data fetch (no LLM)

```pwsh
python -m stonk_sage.data fetch AAPL --as-of 2024-06-01
# prints: data/snapshots/AAPL_2024-06-01.json
```

The snapshot is point-in-time-safe: every dated field is `<= as_of`. Weekends/holidays roll back to the prior trading day's close.

### Direct guards check

```pwsh
python -m stonk_sage.guards check --run-dir data/runs/AAPL_2024-06-01_abc12345
```

Exit code 0 on PASS, non-zero on FAIL. Failure reasons are printed line by line.

---

## Expected First Run

A clean run on `/analyze AAPL 2024-06-01` should:

1. **Fetch step (~5–15s):** prints `data/snapshots/AAPL_2024-06-01.json`. If `EDGAR_IDENTITY` is missing you'll see an `EdgarIdentityMissing` error here — stop and set the env var.
2. **DA → Bull/Bear/Risk → DA-critique → CIO:** chat trace shows 6 sub-agent dispatches. Run-staging directory `data/runs/AAPL_2024-06-01_<uuid>/` accumulates `da.md`, `bull.json`, `bear.json`, `risk.json`, `da_critique.json`, `cio_draft.md`.
3. **Guards step:** prints either `guards: PASS ✅` or `guards: FAIL ❌` with reasons. **Failure is expected sometimes** — the CIO's prose drifts into vague territory, or the Risk Officer's veto isn't honored. The fix is usually to re-run with a fresh UUID; persistent failures point at the agent prompts.
4. **On PASS:** `examples/AAPL_2024-06-01_<uuid>.md` is written, `examples/AAPL_2024-06-01_latest.md` updated, and the memo is printed back to chat.

### Phase 1 acceptance ritual

Consider the project ready when `/analyze` produces **≥2 passing memos out of 3 runs** on the same ticker + as_of, and each passing memo is coherent: recommendation matches sizing; falsification criteria are observable; specialist disagreements are real; no unsupported claims; benchmark comparison cites numbers; source_of_edge is plausibly that type.

### Model availability probe

Before your first real run, verify all 6 models are dispatchable in your Copilot subscription:

```
Probe each of these via the task tool with a one-token prompt: claude-haiku-4.5, claude-sonnet-4.6, gpt-5.4, claude-opus-4.8, gpt-5.5. Report any errors.
```

If a model is unavailable, swap to the closest same-family successor while preserving the cross-family invariants above.

---

## Project Layout

```
stonk-sage/
├── .github/
│   ├── agents/             # 6 agent definitions (data-analyst, bull, bear, risk-officer, devils-advocate, cio)
│   ├── instructions/       # 10 finance brain files (the operational knowledge base)
│   └── skills/
│       └── analyze/SKILL.md   # the /analyze skill — invoked via Copilot CLI /skills mechanism
├── src/stonk_sage/
│   ├── __init__.py         # public facade
│   ├── brain.py            # loads instruction files into agent context
│   ├── contracts.py        # pydantic schemas (MarketSnapshot, Thesis, RiskAssessment, ...)
│   ├── data.py             # point-in-time market data fetcher
│   └── guards.py           # post-CIO hard-rule + vague-edge guard
├── tests/                  # 60 tests; live network tests gated behind -m live
├── docs/
│   ├── interpreting-memos.md          # how to read a /analyze memo (field by field, red flags, worked example)
│   └── dispatch-surface-findings.md   # Task 0.0 findings — see for Copilot CLI mechanics
├── data/                   # gitignored — runtime staging
│   ├── snapshots/
│   └── runs/<TICKER>_<DATE>_<UUID>/
├── examples/               # committed memo output
└── pyproject.toml
```

---

## The Brain

Ten finance instruction files in `.github/instructions/` (133 inline citations, 95 Further Reading entries) cover:

| File | Topic |
|---|---|
| `finance-fundamentals.instructions.md` | Financial statements, ratios, accounting, sector exceptions |
| `equity-research.instructions.md` | End-to-end stock research methodology + edge identification |
| `sec-filings.instructions.md` | 10-K/Q/8-K/Form 4/proxy/13F/13D/13G reference (post-2024 deadlines) |
| `investment-strategies.instructions.md` | Value/growth/momentum/quality/event-driven taxonomy |
| `risk-portfolio.instructions.md` | Position sizing, risk metrics, portfolio construction |
| `behavioral-finance.instructions.md` | Cognitive biases + counter-strategies |
| `backtesting-methodology.instructions.md` | How not to lie to yourself with historical data |
| `market-microstructure.instructions.md` | Order types, liquidity, options, settlement (T+1) |
| `personal-investing-tax-basics.instructions.md` | Cap gains, wash sale, account types (US 2026) |
| `multi-agent-finance-patterns.instructions.md` | Committee architecture + hardened escalation gates |

Each Phase 0+1 agent `view`s the brain files relevant to its role as its first instruction (the dispatch-surface spike confirmed that Standards References is advisory only).

See [`docs/interpreting-memos.md`](docs/interpreting-memos.md) for how to read the memos `/analyze` produces, and [`docs/dispatch-surface-findings.md`](docs/dispatch-surface-findings.md) for the Copilot CLI mechanics findings the architecture relies on.
