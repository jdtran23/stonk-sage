# CLAUDE.md

> Primary entry point for **Claude Code**. The full shared guide is imported below; this file adds only the Claude-Code-specific pointers.

@AGENTS.md

## Claude Code surface

When running under Claude Code, the committee surface is:

- **Subagents:** `.claude/agents/` (`data-analyst`, `bull`, `bear`, `risk-officer`, `devils-advocate`, `cio`). Each subagent's model is fixed in its frontmatter `model:` field — do not try to override it per dispatch.
- **Orchestration:** the `analyze` skill at `.claude/skills/analyze/SKILL.md`. Trigger it with "analyze AAPL 2024-06-01" or "run the committee on AAPL as of 2024-06-01".

## Read before your first run

This roster is **all-Claude, tier-differentiated** (Bull `sonnet` ↔ Bear `opus`; CIO `sonnet` ≠ Devil's Advocate `opus`). That is a **degraded substitute** for the canonical Claude↔GPT cross-family invariant — see `AGENTS.md` → "Cross-family invariant — and the Claude Code degradation". Claude Code runs are fast local drafts; run the Phase-1 acceptance ritual under GitHub Copilot CLI, which can run the true cross-family roster.

## Conventions

- Write captured subagent output to disk with the **`Write`** tool, never via shell heredocs or redirection (see `AGENTS.md` → "Critical operating rules").
- Use the shell (`Bash`) only for `python -m stonk_sage.*` calls and filesystem ops (`New-Item`, `Copy-Item`).
