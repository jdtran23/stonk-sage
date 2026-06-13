---
name: analyze
description: Run the stonk-sage investment committee on a ticker as of a date — 6-agent pipeline (Data Analyst → Bull & Bear → Risk Officer → Devil's Advocate → CIO) with post-CIO guards. Use when the user says "analyze <TICKER>", "run the committee on <TICKER>", or gives a ticker + as-of date.
---

# analyze — Investment Committee Pipeline (Claude Code)

> Orchestrates the 6-agent stonk-sage committee and publishes a guard-validated memo. This is the **Claude Code** edition of the skill. The GitHub Copilot edition lives at `.github/skills/analyze/SKILL.md`; keep the two in sync on logic, but note the host differences below.

## Triggers
- "analyze <TICKER> <YYYY-MM-DD>"
- "analyze <TICKER> as of <YYYY-MM-DD>"
- "run committee on <TICKER>"

Parse `Ticker` (uppercase symbol) and `AsOfDate` (ISO `YYYY-MM-DD`) from the request. If either is missing, ask before proceeding.

## Host differences vs the Copilot edition (read first)

1. **Models are fixed in subagent frontmatter, not set per dispatch.** Each `.claude/agents/*.md` declares its own `model:`. You invoke a subagent by name via the Task tool; you do **not** pass a model override per call. The roster is:

   | Subagent | Model (from frontmatter) |
   |---|---|
   | `data-analyst` | `haiku` |
   | `bull` | `sonnet` |
   | `bear` | `opus` |
   | `risk-officer` | `haiku` |
   | `devils-advocate` | `opus` |
   | `cio` | `sonnet` |

2. **This roster is all-Claude, tier-differentiated — a degraded substitute for the canonical Claude↔GPT cross-family invariant.** Bull `sonnet` ↔ Bear `opus` and CIO `sonnet` ≠ Devil's Advocate `opus` give tier separation only. See `AGENTS.md` → "Cross-family invariant — and the Claude Code degradation". **Treat Claude Code runs as fast local drafts. The Phase-1 acceptance ritual must be run under GitHub Copilot CLI**, which can run the true cross-family roster.

3. **Capture-write uses the `Write` tool.** Everywhere this skill says "write the captured output", use the `Write` tool. The Copilot edition uses its `create` tool; same intent.

## Critical Operating Rules

1. **Persist captured sub-agent output with the `Write` tool (or `Edit` for overwrites). NEVER use shell heredocs, `Set-Content` from a pipeline of the raw text, `echo > file`, or any shell-string redirection to write captured agent output.** Sub-agent output routinely contains backticks, `$`, single/double quotes, and fence-terminator-like strings (` ``` `) that break shell quoting. Reserve the shell (Bash) for filesystem ops only (`New-Item`, `Copy-Item`, `Remove-Item`, `Test-Path`) and the two `python -m stonk_sage.*` calls.
2. **Bull and Bear fan out in parallel. Risk Officer does NOT join that fan-out.** Risk reads `bull.json` and `bear.json` from disk — those files must exist before Risk is dispatched. See the deadlock note in Step 5/6.
3. **Tier-separation invariant:** Keep the two hard inequalities — Bull's model ≠ Bear's model, and CIO's model ≠ Devil's Advocate's model. If a model tier is unavailable, substitute another Anthropic tier that preserves BOTH inequalities (e.g. if `opus` is unavailable, Bear and Devil's Advocate fall back to `sonnet` only if Bull and CIO are then moved off `sonnet` to keep the inequalities). Never collapse a debate pair onto the same model.

## Architecture (subagents already defined in `.claude/agents/`)

| Subagent | Model | Role |
|---|---|---|
| `data-analyst` | `haiku` | Reads `snapshot.json` → emits Markdown digest |
| `bull` | `sonnet` | DA digest + snapshot → fenced ` ```json ` Thesis |
| `bear` | `opus` | DA digest + snapshot → fenced ` ```json ` Thesis (tier-diff vs Bull) |
| `risk-officer` | `haiku` | Snapshot + Bull + Bear → fenced ` ```json ` RiskAssessment |
| `devils-advocate` | `opus` | Snapshot + Bull + Bear + Risk → fenced ` ```json ` Critique |
| `cio` | `sonnet` | All above → Markdown memo with embedded fenced ` ```json ` CIOMemo |

Python helpers:
- `python -m stonk_sage.data fetch <TICKER> --as-of <DATE>` — fetches the snapshot; the last stdout line is the snapshot path (e.g. `data/snapshots/AAPL_2024-06-01.json`). Add `--prices <file>` to source prices/returns/news from a PIT-safe Alpaca MCP price file (see Step 3); without it, yfinance is used.
- `python -m stonk_sage.guards check --run-dir <RUN_DIR>` — validates the run artifacts. Exit 0 = pass.

### Prerequisite — Alpaca MCP

Step 3 calls the Alpaca MCP `get_stock_bars` / `get_news` tools. The `alpaca` MCP server must be configured in Claude Code (`claude mcp add alpaca ...`, launched via `uvx`). If it isn't available, use the **yfinance fallback** in Step 3. See [`docs/onboarding.md`](../../../docs/onboarding.md) for setup.

## 9-Step Pipeline

### Step 1 — Parse args
Extract `Ticker` (uppercase) and `AsOfDate` (`YYYY-MM-DD`) from the user's request. Reject and ask if either is missing or malformed.

### Step 2 — Create staging dir
Generate an 8-hex-char UUID (e.g. `python -c "import uuid; print(uuid.uuid4().hex[:8])"`). Then:

```powershell
New-Item -ItemType Directory -Force -Path "data/runs/<TICKER>_<DATE>_<UUID8>" | Out-Null
```

Store the absolute path as `RUN_DIR`.

### Step 3 — Fetch snapshot (Alpaca MCP prices → yfinance fallback)

Price/return/news data come from the **Alpaca MCP**; the 10-K filing date still comes from `stonk_sage.data` (EDGAR).

**3a. Pull PIT-safe bars** — call `get_stock_bars` for the ticker and SPY, **`sip` first then `iex`:**

```
get_stock_bars(symbols="<TICKER>,SPY", timeframe="1Day",
               start="<AsOfDate - 400 days>", end="<AsOfDate>",   # end MUST be <= as_of
               limit=10000, sort="asc")
```

> **Feed selection:** the free/paper plan serves **historical** SIP (full-market) but **blocks recent SIP** (`403 "subscription does not permit querying recent SIP data"`). If the response has an `error` or zero bars, **retry with `feed="iex"`** (free, all dates, IEX-only coverage). **Do not use `feed="delayed_sip"`** — this MCP build rejects it (`400 invalid feed`). Record the feed you used for 3c.

> **PIT discipline:** use `get_stock_bars` with `end=<AsOfDate>`. **Never** use `get_stock_latest_quote` / `get_stock_snapshot` / `get_stock_latest_trade` for an as-of snapshot — they return live data and inject look-ahead.

**3b. (Optional) Pull news**, also bounded by `end=<AsOfDate>`:

```
get_news(symbols="<TICKER>", start="<AsOfDate - 30 days>", end="<AsOfDate>", limit=10, sort="desc")
```

**3c. Write `<RUN_DIR>/alpaca_prices.json` with the `Write` tool** (never shell redirection — news headlines contain quotes/`$`/specials). Include the `feed` you used (`data.py` surfaces it in `pit_source.price_feed`):

```json
{ "bars": { "<TICKER>": [ ...get_stock_bars bars... ], "SPY": [ ...bars... ] },
  "news": [ ...get_news items... ],
  "feed": "iex" }
```

**3d. Build the snapshot:**

```powershell
python -m stonk_sage.data fetch <TICKER> --as-of <DATE> --prices "<RUN_DIR>/alpaca_prices.json"
```

The last stdout line is the snapshot path; store it as `SNAPSHOT_PATH`.

**Fallback (yfinance):** if **both** `sip` and `iex` fail or return too few bars (date predates Alpaca history, unsupported symbol) or the MCP is unavailable, **omit `--prices`**:

```powershell
python -m stonk_sage.data fetch <TICKER> --as-of <DATE>
```

Both forms write the same `MarketSnapshot`; `data.py` records the source in `pit_source.price_summary` (`"alpaca"` or `"yfinance"`) and the feed in `pit_source.price_feed`.

### Step 4 — Data Analyst leg
Dispatch the `data-analyst` subagent (Task tool). Provide it `SNAPSHOT_PATH`. **Capture the returned text and write it to `<RUN_DIR>/da.md` using the `Write` tool** — do not pipe the text through the shell.

### Step 5 — Bull + Bear (parallel fan-out)
**Dispatch the `bull` and `bear` subagents in the same turn so they run in parallel.** Both receive: `SNAPSHOT_PATH` and the contents (or path) of `<RUN_DIR>/da.md`.

Capture each return value. Write **the captured text verbatim — fence and all** — to:
- `<RUN_DIR>/bull.json` (use `Write`)
- `<RUN_DIR>/bear.json` (use `Write`)

`guards.py` extracts the JSON from the fenced block; do not strip fences yourself.

### Step 6 — Risk Officer (sequential, AFTER Step 5 writes complete)

> **Deadlock note — read carefully.** Risk's subagent file tells it to `Read` `bull.json` and `bear.json`. Those files are written by THIS orchestrator after the Bull/Bear dispatches return. If Risk runs in the same parallel batch, the files do not yet exist and Risk either blocks or reads missing files. **Do NOT dispatch Risk in the same turn as Bull/Bear.** Wait for Bull/Bear to return, write their files with `Write`, THEN dispatch Risk.

Dispatch the `risk-officer` subagent. Tell it the `RUN_DIR` so it can `Read` `bull.json` and `bear.json`. Capture its return → write `<RUN_DIR>/risk.json` via `Write`.

### Step 7 — Devil's Advocate
Dispatch the `devils-advocate` subagent. Inputs: snapshot, `<RUN_DIR>/bull.json`, `<RUN_DIR>/bear.json`, `<RUN_DIR>/risk.json`. Capture → `Write` `<RUN_DIR>/da_critique.json`.

**Quota canary:** Devil's Advocate and Bear are the two `opus` dispatches and the most expensive in this roster. If a run report shows Devil's Advocate consuming a disproportionate share of quota, downshift it to `sonnet` only if you simultaneously keep CIO off `sonnet` (move CIO to `haiku`) so the CIO ≠ Devil's Advocate inequality survives. Never collapse Devil's Advocate onto the CIO's model.

### Step 8 — CIO
Dispatch the `cio` subagent. Inputs: snapshot, da.md, bull.json, bear.json, risk.json, da_critique.json. Capture → `Write` `<RUN_DIR>/cio_draft.md`.

### Step 9 — Guards + publish

```powershell
python -m stonk_sage.guards check --run-dir <RUN_DIR>
```

**On exit code 0 — publish:**
```powershell
Copy-Item "<RUN_DIR>/cio_draft.md" "examples/<TICKER>_<DATE>_<UUID8>.md"
Copy-Item "examples/<TICKER>_<DATE>_<UUID8>.md" "examples/<TICKER>_<DATE>_latest.md" -Force
```
Two plain `Copy-Item`s. **No `os.replace`, no `.tmp` intermediates, no atomic-rename dance.**

Then print the published memo body to chat.

**On non-zero exit — STOP:**
- Report the full guard output to the user.
- Do NOT publish. Do NOT copy to `examples/`.
- The user decides whether to re-run.

## Acceptance Ritual

> The canonical Phase-1 acceptance ritual runs under **GitHub Copilot CLI** with the cross-family roster. A Claude Code run can sanity-check the pipeline end-to-end, but a passing Claude-Code-only run does NOT certify a name — the committee was not cross-family. Record Claude Code runs as drafts.

If you do run the coherence check here: a memo is coherent when recommendation matches sizing; falsification criteria are observable; specialist disagreements are real; no unsupported claims; benchmark comparison cites numbers; source_of_edge is plausibly that type.

## Summary of the Bug Fixes & Data-Source Changes Baked Into This Skill

1. **Deadlock fix (Step 5/6):** Bull + Bear parallel → write files → THEN Risk Officer. Not all three parallel.
2. **Capture-write fix (rule #1, Steps 4–8):** `Write`/`Edit` tool for all sub-agent output writes. Shell only for `mkdir`/`cp` and the two `python -m` calls.
3. **Publish fix (Step 9):** Two plain `Copy-Item` calls. No `os.replace`, no `.tmp`, no single-line copy/replace.
4. **Alpaca MCP price source (Step 3):** prices/returns/news come from the Alpaca MCP `get_stock_bars`/`get_news` tools (PIT-safe, `end <= as_of`), written to `alpaca_prices.json` via `Write` and consumed by `data.py --prices`. Try `sip` first, fall back to `iex` on the recent-SIP 403 (`delayed_sip` is unsupported); yfinance is the final fallback.
