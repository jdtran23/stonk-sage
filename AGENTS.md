# stonk-sage — Agent Guide

> Shared operating guide for the stonk-sage investment committee. **Both GitHub Copilot CLI and Claude Code load this file.** Keep it host-neutral: anything tool-specific lives in that tool's own surface (`.github/**` for Copilot, `.claude/**` for Claude Code).

## What this is

A 6-agent equity-research committee (Data Analyst → Bull & Bear → Risk Officer → Devil's Advocate → CIO) that turns a point-in-time `MarketSnapshot` into a guard-validated investment memo. The agents dispatch through the host's sub-agent/`task` mechanism; deterministic Python (`stonk_sage.data`, `stonk_sage.guards`) does the data fetching and the hard-rule validation. No third-party LLM API keys are required for the **Copilot** path.

> **Not financial advice.** Memos are LLM output for experimentation, not professional analysis.

## Surface map — which files each host loads

| Concern | GitHub Copilot CLI | Claude Code |
|---|---|---|
| Agent definitions | `.github/agents/*.agent.md` | `.claude/agents/*.md` |
| Orchestration | `.github/skills/analyze/SKILL.md` | `.claude/skills/analyze/SKILL.md` |
| Finance brain (shared) | `.github/instructions/*.instructions.md` | same files, read by path |
| Entry memory | `AGENTS.md`, `CLAUDE.md` | `CLAUDE.md` → imports `@AGENTS.md` |

The **brain** (`.github/instructions/*.instructions.md`) is shared verbatim by both hosts — it is not duplicated. Each agent `view`s/`Read`s its referenced brain files by relative path as its first step. The directory is named `.github/` for historical reasons; both hosts read those files fine.

## The committee + model rosters

| Agent | Role | Copilot model (canonical) | Claude Code model |
|---|---|---|---|
| `data-analyst` | snapshot → prose digest | `claude-haiku-4.5` | `haiku` |
| `bull` | strongest long case | `claude-sonnet-4.6` | `sonnet` |
| `bear` | strongest short/skeptic case | `gpt-5.4` | `opus` *(substituted)* |
| `risk-officer` | sizing band + veto | `claude-haiku-4.5` | `haiku` |
| `devils-advocate` | adversarial critique | `claude-opus-4.8` | `opus` |
| `cio` | final synthesized memo | `gpt-5.5` | `sonnet` *(substituted)* |

**Where the model is set differs by host:**
- **Copilot:** the `/analyze` skill sets the model **per dispatch** via the `task` tool's `model=` parameter. Agent frontmatter carries only `name` + `description`.
- **Claude Code:** each subagent's model is fixed in its **frontmatter `model:` field** (`.claude/agents/*.md`). The Task tool uses the subagent's configured model; it is not overridden per call.

## Cross-family invariant — and the Claude Code degradation

The committee's load-bearing design rule is that adversarial pairs run on **different model families** so the committee never produces a one-voice consensus by accident:

- **Bull (Claude) ↔ Bear (GPT)** — the debate pair must not share a family.
- **CIO (GPT) ≠ Devil's Advocate (Claude)** — the synthesizer must not rubber-stamp its own critique.

**Claude Code can only dispatch Anthropic models**, so it cannot run the two GPT roles natively. The Claude Code roster substitutes them with Anthropic models chosen to differ by **tier** from their pair:

- Bull `sonnet` ↔ Bear `opus` (tier-differentiated)
- CIO `sonnet` ≠ Devil's Advocate `opus` (tier-differentiated)

> ⚠️ **Tier-differentiation is a degraded substitute, not true cross-family.** Two Claude tiers share training lineage and will correlate more than a Claude/GPT pair. Treat Claude Code runs as fast local drafts. **The canonical cross-family run — and the Phase-1 acceptance ritual — must be performed under GitHub Copilot CLI.** Do not certify a name on the strength of a Claude-Code-only run.

**Cost note (Claude Code):** Bear and Devil's Advocate both run on `opus`, the most expensive tier. Two Opus dispatches per run is intentional (a weak Bear undermines the debate), but expect higher token cost than the Copilot roster.

## Critical operating rules (host-neutral)

1. **Persist captured sub-agent output with your host's file-creation tool** — Copilot `create`/`edit`, Claude Code `Write`/`Edit`. **Never** use shell heredocs, `Set-Content` from a raw-text pipeline, `echo > file`, or any shell-string redirection to write captured agent output. Agent output routinely contains backticks, `$`, quotes, and ```` ``` ```` fences that break shell quoting. Reserve the shell for filesystem ops only (`New-Item`, `Copy-Item`, `Remove-Item`, `Test-Path`).
2. **Bull and Bear fan out in parallel. Risk Officer does NOT join that fan-out.** Risk reads `bull.json` and `bear.json` from disk — the orchestrator must write those files *before* dispatching Risk. Dispatching Risk in the same parallel batch deadlocks on missing files.
3. **Brain files do not auto-load.** Each agent's first step is to `view`/`Read` its referenced `.github/instructions/*.instructions.md` files. The "Standards References" section in each agent is documentation for humans, not an auto-load.
4. **No-edge ⇒ no-action** is enforced structurally by `contracts.CIOMemo` and re-validated by `guards.py`. The guard additionally fails memos with vague prose ("brand strength", "quality compounder") lacking a quantitative anchor.
5. **Publish only on guard PASS**, with two plain copies (`cio_draft.md` → `examples/<TICKER>_<DATE>_<UUID>.md` → `examples/<TICKER>_<DATE>_latest.md`). No `os.replace`, no `.tmp` intermediates, no atomic-rename dance.

## Python helpers (deterministic, no LLM)

```
python -m stonk_sage.data fetch <TICKER> --as-of <YYYY-MM-DD>
#   → prints the snapshot path (e.g. data/snapshots/AAPL_2024-06-01.json) on its
#     last stdout line; point-in-time-safe (every dated field <= as_of)

python -m stonk_sage.data fetch <TICKER> --as-of <YYYY-MM-DD> --prices <FILE>
#   → same, but sources prices/returns/news from a PIT-safe Alpaca price/news
#     JSON file instead of yfinance (the analyze skill produces it via the
#     Alpaca MCP get_stock_bars tool; falls back to yfinance when omitted)

python -m stonk_sage.guards check --run-dir <RUN_DIR>
#   → exit 0 = PASS, non-zero = FAIL with reasons printed line by line
```

Requires `EDGAR_IDENTITY` (`Your Name your.email@example.com`) in the environment or `.env` for SEC fair-access compliance.

## The brain — `.github/instructions/`

| File | Topic |
|---|---|
| `finance-fundamentals.instructions.md` | Statements, ratios, accounting, sector exceptions |
| `equity-research.instructions.md` | End-to-end research methodology + edge identification |
| `sec-filings.instructions.md` | 10-K/Q/8-K/Form 4/proxy/13F/13D/13G reference |
| `investment-strategies.instructions.md` | Value/growth/momentum/quality/event-driven taxonomy |
| `risk-portfolio.instructions.md` | Position sizing, risk metrics, portfolio construction |
| `behavioral-finance.instructions.md` | Cognitive biases + counter-strategies |
| `backtesting-methodology.instructions.md` | Avoiding self-deception with historical data |
| `market-microstructure.instructions.md` | Order types, liquidity, options, settlement (T+1) |
| `personal-investing-tax-basics.instructions.md` | Cap gains, wash sale, account types (US) |
| `multi-agent-finance-patterns.instructions.md` | Committee architecture + escalation gates |
