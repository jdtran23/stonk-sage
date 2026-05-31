# Dispatch Surface Findings — Task 0.0

> **Status:** ✅ COMPLETE
> **Date:** 2026-05-30
> **Spike duration:** ~30 min
> **Plan reference:** `myBrain/Plans/003-plan-agent-committee-plan-b.md` § Phase 0 Task 0.0
> **Method:** Probed in-session from a Copilot CLI session running in `myBrain`. myBrain proves the mechanism: its `.github/agents/*.agent.md` files are auto-loaded as callable sub-agents. stonk-sage's `.github/agents/` will load the same way when a session is started in that workspace.

This document records what Copilot CLI's `task` tool and slash-command system actually do versus what Plan 003 assumed.

---

## TL;DR

| Mechanism | Status | Plan delta |
|---|---|---|
| Workspace `.github/agents/*.agent.md` auto-load | ✅ Works | None |
| `task` tool `model` override per dispatch | ✅ Works | None |
| Self-reported model identity from sub-agent | ⚠️ Unreliable | Don't rely on LLM self-report; trust the override parameter |
| Parallel dispatch (multiple `task` calls in one response) | ✅ Works (overlapping windows) | None |
| **`Standards References` auto-load** | ❌ **Advisory only** | **Each agent's first instruction must `view` its referenced brain files** |
| Sub-agent text capture (via `read_agent`-equivalent) | ✅ Works | None |
| Staging seam: capture → write to disk → Python parses fenced JSON | ✅ Works | None |
| `model:` in agent.md frontmatter | ⚠️ myBrain agents don't use it — pass via slash command instead | `/analyze` passes `model=` per `task` dispatch; agent.md does not need `model:` |
| `tools:` in agent.md frontmatter | ⚠️ myBrain agents don't use it — appears advisory | Encode tool constraints as prompt-level instructions, not frontmatter |
| Slash command argument syntax | ✅ `${input:Name}` | Confirmed by `myBrain/.github/prompts/orchestrate.prompt.md`; `/analyze` will use same |
| Per-model availability | ❓ Untested in stonk-sage session | Run a `--check-models` probe before first `/analyze` |

**Overall verdict: ☑ Proceed to Task 0.1 with two surgical deltas** (Standards References → explicit `view`; model + tools → not in frontmatter).

---

## Findings detail

### F1 — Workspace agent loading: ✅ confirmed
**Evidence:** myBrain has 10 files in `.github/agents/*.agent.md` (absol, cresselia, gardevoir, klefki, metagross, mewtwo, porygon, rotom, tapu-fini, uxie) and exactly those 10 names appear in this session's callable custom agent registry. 1:1 mapping. Therefore stonk-sage's `.github/agents/*.agent.md` will be loaded into a Copilot CLI session started in stonk-sage workspace.

### F2 — `task` tool's `model` override parameter: ✅ confirmed
**Evidence:** dispatched two `general-purpose` sub-agents in the same response with `model=claude-haiku-4.5` and `model=gpt-5.4`. Both completed without error. The override parameter is the supported model-selection mechanism. (Whether agent.md frontmatter `model:` is independently read is unknown but irrelevant — the slash command sets the model per dispatch.)

### F3 — Self-report model identity: ⚠️ unreliable
**Evidence:** Haiku claimed to be "claude-sonnet-4.6". GPT-5.4 said "unknown". LLMs are famously bad at knowing their own model. **Use behavioral signals (speed, response style) to confirm routing, not self-report.**

### F4 — Parallel dispatch: ✅ confirmed
**Evidence:**
```
Haiku spike:   start 04:05:07Z  →  end 04:05:11Z
GPT-5.4 spike: start 04:05:10Z  →  end 04:05:15Z
```
GPT-5.4 started while Haiku was still running. Two `task` calls in the same response fan out, they do not serialize. **Plan 003 §1.4 (Bull/Bear/Risk parallel leg) stands as written.**

### F5 — Standards References: ❌ advisory only
**Evidence:** dispatched a sub-agent with explicit instruction "without using any tools, answer from your initial context only: what does stonk-sage's risk-portfolio.instructions.md say about position sizing?" Sub-agent replied: *"NO STANDARDS-REFERENCES AUTO-LOAD: I do not have any stonk-sage brain content in my initial context. I would need to use the view tool to read it."*

**Plan delta (REQUIRED):** Every agent.md authored in Tasks 0.3, 0.4, 1.1, 1.2, 1.3 must include an **Instructions** section whose first numbered step is:
> *"Before doing anything else, use the `view` tool to read your referenced brain files: `[list of paths]`. Their content is the operational definition of your role."*

Standards References stays in the agent file as **documentation for humans** of what brain content is relevant; it does not auto-load.

### F6 — Sub-agent output capture: ✅ confirmed
**Evidence:** every `task` dispatch in this session returned the sub-agent's complete final text through the orchestrating context. The output is plain text/markdown and can be programmatically inspected.

### F7 — Staging seam (capture → disk → Python parse): ✅ confirmed
**Evidence:** simulated the `/analyze` flow:
1. Created `data/runs/test_XXXXX/`
2. Wrote a Bull-style output (markdown with a fenced ```json``` block) to `bull.json`
3. Ran a Python script that regex-extracts the fenced block and `json.loads()` it
4. Got `PARSED: ticker=AAPL, conviction=MEDIUM, 3 thesis points` + `STAGING SEAM: WORKS`

**The exact mechanism the `/analyze` slash command relies on works.** No fork needed. Task 1.4's design holds: agents emit a fenced JSON block in their response → slash command writes that captured text to disk → `guards.py` reads the file → parse → validate.

### F8 — Agent.md frontmatter conventions: ⚠️ revised
**Evidence:** ran `Select-String '^model:'` and `Select-String '^tools:'` over all 10 myBrain agent files. **Zero hits.** myBrain agents declare only `name` and `description` in frontmatter and they work fine. This means:
- `model:` in frontmatter is at best optional; the `task` tool's `model` parameter is the canonical mechanism
- `tools:` in frontmatter is similarly not used by working agents

**Plan delta:** stonk-sage's agent.md files will follow myBrain's pattern — frontmatter has `name` and `description` only. Per-agent model is set via the `/analyze` slash command's `task` dispatch call (`model=<assigned model>`). Tool constraints are described in the agent's prose (e.g., "You do not write files; the orchestrator handles persistence").

### F9 — Slash command argument syntax: ✅ confirmed via myBrain example
**Evidence:** `myBrain/.github/prompts/orchestrate.prompt.md` uses `${input:Describe the task to orchestrate}`. `/analyze` will use the same: `${input:Ticker}` and `${input:AsOfDate}`.

### F10 — Per-model availability: ❓ untested
**Plan delta (small):** before the first real `/analyze` run, Joe runs in stonk-sage workspace:
> "Probe each of these models via `task` tool with a one-token prompt: `claude-haiku-4.5`, `claude-sonnet-4.6`, `gpt-5.4`, `claude-opus-4.8`, `gpt-5.5`. Report any that error out."

If a model is unavailable, swap to closest same-family successor preserving cross-family invariants:
- Bull (claude family) ≠ Bear (gpt family)
- Devil's Advocate ≠ CIO (different family)

---

## Plan 003 deltas to apply

1. **Delta-A (REQUIRED):** Every Phase 0+1 agent.md gets an **Instructions** section whose step 1 is `view` of all referenced brain files. (F5)
2. **Delta-B (REQUIRED):** Agent.md frontmatter contains only `name` and `description`. Model is set per dispatch via the slash command. (F8)
3. **Delta-C (REQUIRED):** Tool restrictions are described in agent prose ("you write/don't write to disk"), not via `tools:` frontmatter. (F8)
4. **Delta-D (small):** Add a one-line model availability probe to the README/runbook before first `/analyze`. (F10)

No fork is needed (staging seam works). No architectural revision is needed (parallel dispatch works). Plan 003's Phase 0+1 structure is intact.

---

## Decisions

- [x] **Proceed to Task 0.1** — Plan 003 stands with deltas A/B/C/D applied during agent authoring.
- [ ] ~~Apply Fork A (agent-self-writes-staging)~~ — not needed; F7 works.
- [ ] ~~Escalate Fork B (staging not viable)~~ — not needed; F7 works.

## Cleanup — toy artifacts

Hello.agent.md and foo.prompt.md served their purpose. They will be removed in the same commit that lands this findings doc, since their probing job is done and we've proven the mechanism by other means (F1, F2, F4, F6, F7).
