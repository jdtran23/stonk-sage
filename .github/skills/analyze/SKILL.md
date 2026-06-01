---
name: "analyze"
description: "Run the stonk-sage investment committee on a ticker as of a date — 6-agent pipeline with post-CIO guards"
---
# analyze — Investment Committee Pipeline

> Orchestrates the 6-agent stonk-sage committee (Data Analyst → Bull & Bear → Risk Officer → Devil's Advocate → CIO) and publishes a guard-validated memo.

## Triggers
- `/analyze <TICKER> <YYYY-MM-DD>`
- `/analyze <TICKER> --as-of <YYYY-MM-DD>`
- "analyze <ticker>"
- "run committee on <ticker>"

## Invocation UX

Joe types one of:

```
/analyze AAPL 2024-06-01
/analyze AAPL --as-of 2024-06-01
```

Parse `Ticker` (uppercase symbol) and `AsOfDate` (ISO date) from the freeform args. Either positional or `--as-of` form is accepted. If either is missing, ask the user before proceeding.

## Critical Operating Rules

1. **Persist captured sub-agent output with the `create` tool (or `edit` for overwrites). NEVER use shell heredocs, `Set-Content` from a pipeline of the raw text, `echo > file`, or any shell-string redirection to write captured agent output.** Sub-agent output routinely contains backticks, `$`, single/double quotes, and fence-terminator-like strings (` ``` `) that break shell quoting. Reserve PowerShell for filesystem ops only (`New-Item`, `Copy-Item`, `Remove-Item`, `Test-Path`).
2. **Bull and Bear fan out in parallel. Risk Officer does NOT join that fan-out.** Risk reads `bull.json` and `bear.json` from disk — those files must exist before Risk is dispatched. See the deadlock note in Step 5/6.
3. **Cross-family invariant:** The committee must include both Claude-family and GPT-family voices to avoid intra-family rubberstamping. Bull (`claude-sonnet-4.6`) ↔ Bear (`gpt-5.4`) is the load-bearing pair. CIO (`gpt-5.5`) must differ from Devil's Advocate (`claude-opus-4.8`). Data Analyst and Risk share a model (`claude-haiku-4.5`); that's fine — they don't debate each other.
4. **Model unavailability:** Swap to a same-family successor and preserve the cross-family invariant. Examples:
   - `claude-opus-4.8` unavailable → `claude-opus-4.7` (DA stays Claude family).
   - `gpt-5.5` unavailable for CIO → `gpt-5.4` is fine (still differs from DA's Claude).
   - Never swap Bull or Bear across families.

## Architecture (agents already defined in `.github/agents/`)

| Agent | Model | Role |
|---|---|---|
| `@data-analyst` | `claude-haiku-4.5` | Reads `snapshot.json` → emits Markdown digest |
| `@bull` | `claude-sonnet-4.6` | DA digest + snapshot → fenced ` ```json ` Thesis |
| `@bear` | `gpt-5.4` | DA digest + snapshot → fenced ` ```json ` Thesis (gpt family — cross-family invariant) |
| `@risk-officer` | `claude-haiku-4.5` | Snapshot + Bull + Bear → fenced ` ```json ` RiskAssessment |
| `@devils-advocate` | `claude-opus-4.8` | Snapshot + Bull + Bear + Risk → fenced ` ```json ` Critique |
| `@cio` | `gpt-5.5` | All above → Markdown memo with embedded fenced ` ```json ` CIOMemo |

Python helpers:
- `python -m stonk_sage.data fetch <TICKER> --as-of <DATE>` — fetches the snapshot, prints `SNAPSHOT_PATH=<absolute path>` on stdout.
- `python -m stonk_sage.guards check --run-dir <RUN_DIR>` — validates the run artifacts. Exit 0 = pass.

## 9-Step Pipeline

### Step 1 — Parse args
Extract `Ticker` (uppercase) and `AsOfDate` (`YYYY-MM-DD`) from the user's invocation. Reject and ask if either is missing or malformed.

### Step 2 — Create staging dir
Generate an 8-hex-char UUID (e.g. `python -c "import uuid; print(uuid.uuid4().hex[:8])"`). Then:

```powershell
New-Item -ItemType Directory -Force -Path "data/runs/<TICKER>_<DATE>_<UUID8>" | Out-Null
```

Store the absolute path as `RUN_DIR`.

### Step 3 — Fetch snapshot
```powershell
python -m stonk_sage.data fetch <TICKER> --as-of <DATE>
```
Capture stdout, parse the `SNAPSHOT_PATH=…` line, store as `SNAPSHOT_PATH`.

### Step 4 — Data Analyst leg
Dispatch `@data-analyst` with model `claude-haiku-4.5`. Provide it `SNAPSHOT_PATH`. **Capture the returned text and write it to `<RUN_DIR>/da.md` using the `create` tool** — do not pipe the text through shell.

### Step 5 — Bull + Bear (parallel fan-out)
**Dispatch `@bull` and `@bear` in the same response so they run in parallel.**
- `@bull` model: `claude-sonnet-4.6`
- `@bear` model: `gpt-5.4`

Both receive: `SNAPSHOT_PATH` and the contents (or path) of `<RUN_DIR>/da.md`.

Capture each return value. Write **the captured text verbatim — fence and all** — to:
- `<RUN_DIR>/bull.json` (use `create`)
- `<RUN_DIR>/bear.json` (use `create`)

`guards.py` extracts the JSON from the fenced block; do not strip fences yourself.

### Step 6 — Risk Officer (sequential, AFTER Step 5 writes complete)

> **Deadlock fix — read this carefully.** The earlier prompt-file version of this workflow fanned out Bull, Bear, AND Risk Officer in parallel. Risk's agent file tells it to `view` `bull.json` and `bear.json`. Those files are written by THIS orchestrator after the Bull/Bear dispatches return. If Risk runs in the same parallel batch, the files do not yet exist and Risk either blocks or reads missing files. **Do NOT dispatch Risk in the same response as Bull/Bear.** Wait for Bull/Bear to return, write their files with `create`, THEN dispatch Risk in a subsequent response.

Dispatch `@risk-officer` with model `claude-haiku-4.5`. Tell it the `RUN_DIR` so it can `view` `bull.json` and `bear.json`. Capture its return → write `<RUN_DIR>/risk.json` via `create`.

### Step 7 — Devil's Advocate
Dispatch `@devils-advocate` with model `claude-opus-4.8`. Inputs: snapshot, `<RUN_DIR>/bull.json`, `<RUN_DIR>/bear.json`, `<RUN_DIR>/risk.json`. Capture → `create` `<RUN_DIR>/da_critique.json`.

**Quota canary:** Devil's Advocate is the most expensive single dispatch in the pipeline (Opus). If a run report shows this one dispatch consumed a disproportionate share of monthly Copilot premium quota, **downshift DA to `gpt-5.4` for subsequent runs** — NOT to `claude-sonnet-4.6`. `claude-sonnet-4.6` is Bull's model; using it for DA collapses the contrarian role into a rubberstamp of Bull. `gpt-5.4` preserves the cross-family critique posture (it's already Bear's family but it's a different role and that's acceptable for a quota-driven downshift).

### Step 8 — CIO
Dispatch `@cio` with model `gpt-5.5`. Inputs: snapshot, da.md, bull.json, bear.json, risk.json, da_critique.json. Capture → `create` `<RUN_DIR>/cio_draft.md`.

### Step 9 — Guards + publish

```powershell
python -m stonk_sage.guards check --run-dir <RUN_DIR>
```

**On exit code 0 — publish:**
```powershell
Copy-Item "<RUN_DIR>/cio_draft.md" "examples/<TICKER>_<DATE>_<UUID8>.md"
Copy-Item "examples/<TICKER>_<DATE>_<UUID8>.md" "examples/<TICKER>_<DATE>_latest.md" -Force
```
Two plain `Copy-Item`s. **No `os.replace`, no `.tmp` intermediates, no atomic-rename dance.** The prior bug here was an over-engineered single-line copy/replace; do not reintroduce it.

Then print the published memo body to chat.

**On non-zero exit — STOP:**
- Report the full guard output to the user.
- Do NOT publish. Do NOT copy to `examples/`.
- The user decides whether to re-run.

## Acceptance Ritual

Phase 1 ship gate: run the pipeline **3 times** on the chosen acceptance tickers. Ship Phase 1 only if **≥2 of 3 runs pass the 6-item coherence checklist**: recommendation matches sizing; falsification criteria are observable; specialist disagreements are real; no unsupported claims; benchmark comparison cites numbers; source_of_edge is plausibly that type.

- A guard-failed run (Step 9 non-zero exit) counts as a §1.5 failure.
- The denominator stays 3 — do NOT retry the failed run and call the retry "run 3"; that defeats the acceptance bar.

## Summary of the Three Bug Fixes Baked Into This Skill

1. **Deadlock fix (Step 5/6):** Bull + Bear parallel → write files → THEN Risk Officer. Not all three parallel.
2. **Capture-write fix (rule #1, Steps 4–8):** `create`/`edit` tool for all sub-agent output writes. Shell only for `mkdir`/`cp`.
3. **Publish fix (Step 9):** Two plain `Copy-Item` calls. No `os.replace`, no `.tmp`, no single-line copy/replace.
