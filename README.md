# stonk-sage

Knowledge base for building multi-agent stock-research and assessment systems.

## What This Is
This repo currently contains **brain directives only** — instruction files that capture finance and investing domain knowledge for use by AI agents. The actual code (agents, data layer, backtester) will come later. Knowledge first; agents built on top of it second.

## Structure
- `.github/instructions/` — Domain knowledge as agent-loadable instructions
  - `finance-fundamentals.instructions.md` — Financial statements, ratios, accounting, sector exceptions
  - `equity-research.instructions.md` — End-to-end stock research methodology + edge identification + benchmark comparison
  - `sec-filings.instructions.md` — 10-K/Q/8-K/Form 4/proxy/13F/13D/13G reference (deadlines updated post-2024)
  - `investment-strategies.instructions.md` — Value/growth/momentum/quality/event-driven taxonomy
  - `risk-portfolio.instructions.md` — Position sizing, risk metrics, portfolio construction
  - `behavioral-finance.instructions.md` — Cognitive biases + counter-strategies
  - `backtesting-methodology.instructions.md` — How not to lie to yourself with historical data
  - `market-microstructure.instructions.md` — Order types, liquidity, options, settlement (T+1)
  - `personal-investing-tax-basics.instructions.md` — Cap gains, wash sale, account types, US 2026
  - `multi-agent-finance-patterns.instructions.md` — Committee architecture with hardened escalation gates

## Conventions
- **Instructions** lazy-load via `description` keyword matching — they activate when an agent's context suggests the relevant domain
- Content is **operational** (formulas + interpretation + gotchas), not academic
- PIT-safety (point-in-time data discipline) is called out explicitly per data source
- Common analyst traps and biases are surfaced, not buried

## Coming Later
- Skills (procedural workflows: `analyze-stock`, `read-filing`, `assess-thesis`, `build-finance-committee`)
- Agent definitions
- Data layer + backtester
