---
description: "Run the full stonk-sage investment committee on a ticker as of a date — 6-agent pipeline with post-CIO guards"
---

# /analyze

Run the complete stonk-sage investment committee on **`${input:Ticker}`** as of **`${input:AsOfDate}`** (ISO date `YYYY-MM-DD`).

This is the canonical entry point. It dispatches the 6-agent pipeline (Data Analyst → Bull + Bear + Risk Officer → Devil's Advocate → CIO), runs post-CIO guards, and publishes the memo only on guard pass.

---

## Pipeline

You (Copilot CLI) will execute these steps **in order**. Each step's output is captured to a staging directory so the guards (and humans) can inspect the full trail.

### Step 1 — Fetch market snapshot (no LLM)

Use the shell tool to run:
```pwsh
python -m stonk_sage.data fetch ${input:Ticker} --as-of ${input:AsOfDate}
```
Capture the printed path; this is `SNAPSHOT_PATH`. The snapshot lives under `data/snapshots/`.

### Step 2 — Create the run staging directory

Generate a short uuid (8 hex chars, e.g. `python -c "import uuid; print(uuid.uuid4().hex[:8])"`). Call it `RUN_UUID`.

Create the staging dir:
```pwsh
$runDir = "data/runs/${input:Ticker}_${input:AsOfDate}_$RUN_UUID"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
```
This is `RUN_DIR`. The directory is gitignored (see `.gitignore`).

### Step 3 — Dispatch the Data Analyst

Dispatch `@data-analyst` with `model: claude-haiku-4.5`. Instruct it:
> "Read the snapshot at `<SNAPSHOT_PATH>` and emit your digest per your Output Contract."

Capture its complete returned text. Write it to `<RUN_DIR>/da.md` using the shell tool.

### Step 4 — Dispatch Bull, Bear, Risk Officer in parallel

In a single response, dispatch all three:

- `@bull` with `model: claude-sonnet-4.6` — *"Snapshot at `<SNAPSHOT_PATH>`; Data Analyst digest at `<RUN_DIR>/da.md`. Emit your Thesis per your Output Contract."*
- `@bear` with `model: gpt-5.4` — *(same prompt)*
- `@risk-officer` with `model: claude-haiku-4.5` — *"Snapshot at `<SNAPSHOT_PATH>`; Data Analyst digest at `<RUN_DIR>/da.md`. Bull and Bear are running in parallel and will write `<RUN_DIR>/bull.json` and `<RUN_DIR>/bear.json` shortly. Wait for both files to exist, then emit your RiskAssessment per your Output Contract."*

After each finishes, write its complete returned text to:
- `<RUN_DIR>/bull.json`
- `<RUN_DIR>/bear.json`
- `<RUN_DIR>/risk.json`

(The agents' outputs are fenced ```json``` blocks; the entire returned text — fence and all — goes into the file. `guards.py` knows how to extract the JSON.)

> **If parallel dispatch turns out to serialize in your session, just dispatch sequentially in this order: bull, bear, risk-officer.** The pipeline still works; only runtime increases.

### Step 5 — Dispatch the Devil's Advocate

Dispatch `@devils-advocate` with `model: claude-opus-4.8`. Instruct it:
> "Snapshot at `<SNAPSHOT_PATH>`; outputs at `<RUN_DIR>/bull.json`, `<RUN_DIR>/bear.json`, `<RUN_DIR>/risk.json`. Emit your DevilsAdvocateCritique per your Output Contract."

Write the returned text to `<RUN_DIR>/da_critique.json`.

> **Quota canary (per Plan 003 § 0.5):** if this single dispatch consumes a disproportionate share of your Copilot premium quota, downshift the Devil's Advocate to `model: gpt-5.4` for subsequent runs. **Do not downshift to `claude-sonnet-4.6` — that is Bull's model**, and DA-matches-Bull defeats the cross-family invariant.

### Step 6 — Dispatch the CIO

Dispatch `@cio` with `model: gpt-5.5`. Instruct it:
> "Snapshot at `<SNAPSHOT_PATH>`; outputs at `<RUN_DIR>/bull.json`, `<RUN_DIR>/bear.json`, `<RUN_DIR>/risk.json`, `<RUN_DIR>/da_critique.json`. Emit your CIO memo per your Output Contract — Markdown with the embedded fenced JSON block."

Write the returned text to `<RUN_DIR>/cio_draft.md`.

### Step 7 — Run the guards

```pwsh
python -m stonk_sage.guards check --run-dir $runDir
```

Capture stdout and the exit code. If exit code is **0** → proceed to Step 8. If exit code is **non-zero** → STOP. Report the guard output to the user. Do not publish. The user decides whether to re-run (often re-running with a re-randomized RUN_UUID surfaces a memo that passes; persistent failures indicate the inputs need attention).

### Step 8 — Publish on guard pass

Atomic publish:
```pwsh
$publishedPath = "examples/${input:Ticker}_${input:AsOfDate}_$RUN_UUID.md"
Copy-Item "$runDir/cio_draft.md" $publishedPath
Copy-Item $publishedPath "examples/${input:Ticker}_${input:AsOfDate}_latest.md" -Force
```

Report to user:
- `RUN_UUID`
- Path to published memo
- Path to `_latest.md`
- Guard verdict line

### Step 9 — Surface the memo

Print the published memo's full markdown to the chat so the user can read it directly without opening the file.

---

## Acceptance ritual (per Plan 003 § 1.5)

The Phase 1 exit gate requires running `/analyze` **3 times** on the same ticker + as_of and accepting Phase 1 only if **≥2 of 3** memos:
- Pass the guards (Step 7)
- Are coherent on a 6-item checklist (see `Plans/002-plan-agent-committee.md` § 1.6: recommendation matches sizing; falsification criteria are observable; specialist disagreements are real; no unsupported claims; benchmark comparison cites numbers; source_of_edge is plausibly that type)

Guard-failed runs count as failures for the 2-of-3 numerator (denominator stays at 3).
