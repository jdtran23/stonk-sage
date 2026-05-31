---
description: "Multi-agent finance patterns — investment committee architecture, specialist analyst roles, debate protocols, consensus mechanisms, devil's advocate, contrarian, fundamental/technical/risk/macro/quant specialists, output contracts, calibration enforcement, anti-patterns, sequential vs parallel composition"
---
# Multi-Agent Patterns for Investment Analysis

> Bridge from finance knowledge to agent system design. Investment decisions benefit from multi-agent architectures specifically because human single-agent reasoning is biased (Tversky & Kahneman 1974; Nickerson 1998). See `behavioral-finance`. This file specifies role taxonomies, debate protocols, and output contracts for finance-domain agent committees.

## Why Multi-Agent for Investment Decisions

Single-agent reasoning (whether human or LLM) suffers from:
- **Anchoring** on the first frame (Tversky & Kahneman 1974)
- **Confirmation bias** toward initial hypothesis (Nickerson 1998)
- **Narrative coherence** at the expense of contradicting evidence
- **Specialist knowledge limits** — no single agent is expert in fundamentals + macro + sentiment + technicals + portfolio risk

Multi-agent committees address these by:
- **Parallel specialist analysis** — each agent has bounded responsibility and depth (Anthropic 2025)
- **Adversarial roles** — designated devil's advocate forced to construct opposition
- **Sequenced reasoning** — agents see and respond to prior agents' work
- **Explicit consensus mechanisms** — disagreements surfaced rather than averaged away

**Caveat:** multi-agent is not automatically better. Poorly-designed committees produce groupthink, anchor on the first agent, or hide disagreement behind synthesized consensus. Architecture matters (Cemri et al. 2025).

## Specialist Role Taxonomy

### Fundamental Analyst
**Owns:** Business model, financials, valuation, moat analysis.
**Inputs:** 10-K, 10-Q, earnings call transcripts, peer comps.
**Outputs:** Business one-paragraph, ROIC trend, FCF trend, valuation range (DCF + comps + reverse DCF), key financial risks.
**Reads:** `finance-fundamentals`, `equity-research`, `sec-filings`.
**Anti-pattern:** Overweighting management's narrative; ignoring red flags in footnotes.

### Technical Analyst
**Owns:** Price action, volume patterns, momentum, technical signals.
**Inputs:** OHLCV history, volume profile, indicator series.
**Outputs:** Trend assessment (up/down/sideways), key support/resistance, momentum state, volume confirmation/divergence.
**Anti-pattern:** Treating technicals as predictive in isolation; over-reading short-term noise.
**Note:** Useful for entry/exit timing on fundamentals-driven theses; weak as a standalone strategy.

### Risk Officer
**Owns:** Position sizing, portfolio-level risk, correlation, concentration.
**Inputs:** Proposed thesis + current portfolio + risk metrics.
**Outputs:** Recommended position size, concentration check, correlation check, expected drawdown contribution.
**Reads:** `risk-portfolio`, `backtesting-methodology` (for honest base rates).
**Authority:** Can VETO position sizes that violate risk policy; cannot veto theses themselves.
**Anti-pattern:** Risk officer becomes a yes-machine that approves whatever portfolio manager proposes.

### Quantitative Analyst
**Owns:** Factor exposure, screen-based signals, statistical hypotheses.
**Inputs:** Historical price + fundamental data, factor definitions.
**Outputs:** Factor exposures of the proposed position (value/momentum/quality/size scores vs universe), regime sensitivity, backtest if applicable.
**Reads:** `investment-strategies`, `backtesting-methodology`.
**Anti-pattern:** Overconfidence from in-sample backtests; ignoring economic significance.

### Macro / Sector Specialist
**Owns:** Industry dynamics, regulatory landscape, macroeconomic context.
**Inputs:** Industry reports, regulatory filings, macro indicators (rates, inflation, ISM, employment).
**Outputs:** Sector regime assessment (early/mid/late cycle), regulatory risks, macro tailwinds/headwinds for the specific name.
**Anti-pattern:** Long-form macro narratives without translation to the specific stock.

### Devil's Advocate / Contrarian
**Owns:** Strongest bear case + falsification scenarios.
**Inputs:** The proposed bull thesis.
**Outputs:** (a) The strongest opposing case with specific evidence; (b) specific falsification criteria — what observable events would prove the thesis wrong.
**Authority:** Cannot block, but bear case must be acknowledged in the committee output.
**Critical principle:** This role should be filled by a **different model** if possible (e.g., bull thesis written by Claude → devil's advocate by GPT) to avoid same-model echo. Cross-vendor diversity is a feature, not a bug (Du et al. 2023; Park et al. 2024).

### Sentiment / Crowd Analyst
**Owns:** Positioning, sentiment, narrative state.
**Inputs:** AAII sentiment surveys, retail flow data, short interest, options skew, social mentions, news flow.
**Outputs:** Crowdedness assessment (consensus / contrarian setup), sentiment regime, narrative arc.
**Anti-pattern:** Sentiment as a primary signal vs as a context filter.

### Portfolio Manager (Synthesizer)
**Owns:** Integrating specialist outputs into a final decision.
**Inputs:** All specialist analyses + bull / bear cases.
**Outputs:** Decision (buy / hold / sell / no action), conviction level, position size, time horizon, falsification criteria, catalyst expectations.
**Authority:** Final word, but must address all specialist outputs — cannot ignore the bear case.

## Debate Protocols

### 1. Sequential (Round-Robin)
Each agent reads all prior agents' outputs before contributing. Final synthesizer integrates.

**Pros:** Late-stage agents have full context; reasoning builds.
**Cons:** Anchoring on early agents; first speaker has disproportionate influence; serial = slow.

**Best for:** Deep research on single name where each layer benefits from prior layers (the BlackRock Alpha Agents / 9-agent committee pattern) (BlackRock 2025; Greenblatt 1997).

**Anti-pattern:** First agent makes a confident strong claim; later agents pattern-match to it instead of fresh analysis.

### 2. Parallel + Synthesizer
All specialists analyze independently (no cross-visibility); synthesizer combines.

**Pros:** No anchoring; honest diverse perspectives; parallelism faster.
**Cons:** Specialists miss context the others have; synthesis is the hardest step.

**Best for:** Initial screens; first-pass evaluation of many candidates.

### 3. Adversarial (Bull vs Bear Debate)
Bull author writes thesis; bear author (different model) attacks; bull responds; bear responds; judge decides.

**Pros:** Forces strongest counterarguments; resistant to single-model groupthink (Du et al. 2023; Park et al. 2024).
**Cons:** Can become rhetorical sparring (clever beats correct); requires judge with good calibration.

**Best for:** High-conviction positions where the bear case must be tested.

**Implementation:** Use different LLM providers for bull and bear if possible. Same-prompt-different-model produces meaningfully different opposition than same-model-different-prompt (Du et al. 2023).

### 4. Iterative Refinement (Evaluator-Optimizer)
Maker produces draft thesis; reviewer critiques against rubric; maker revises; loop until reviewer passes or iteration cap reached (Anthropic 2024; Ng 2024).

**Pros:** Convergent; produces high-quality output; matches maker/reviewer pattern from other domains.
**Cons:** Same-domain reviewer may reinforce same biases; can loop indefinitely without escalation.

**Best for:** Refining a thesis to publishable quality. The bread-and-butter pattern for production thesis output.

### 5. Hierarchical Decomposition
Orchestrator decomposes question → assigns sub-questions to specialists → integrates → may decompose further (Anthropic 2024; OpenAI 2025; Google 2025).

**Pros:** Handles complex questions ("evaluate AAPL across business, financials, valuation, sentiment, macro").
**Cons:** Orchestrator becomes a bottleneck and bias source.

**Best for:** Wide-scope research questions that decompose naturally.

## Consensus & Conflict Resolution

### Voting (Simple Majority)
- Each specialist votes buy/hold/sell.
- Majority wins.
- **Anti-pattern:** Ignores conviction. A 3-2 vote with 2 strong bears is not the same as 3-2 with 2 mild bears.

### Weighted Voting (by Specialty Relevance)
- Fundamental analyst's vote weighted heavier for value plays; technical analyst's vote weighted heavier for short-term tactical.
- Requires explicit weights set per strategy class.

### Veto Authority
- Risk officer can veto position size (not direction).
- Devil's advocate cannot veto but must be acknowledged.
- Designed minorities prevent groupthink.

### Forced Disagreement Surface
- Final output must explicitly state where specialists disagreed.
- "All five specialists agree" should be treated with suspicion — likely groupthink or weak independent analysis.

### Escalation
- If maker/reviewer cannot converge after N iterations, escalate to human.
- If specialists are split with high conviction on both sides, escalate.
- Better to surface disagreement than synthesize fake consensus.

### Escalation (hardened gates)

A committee output that doesn't pass these criteria must escalate to human review, not produce a recommendation:

- **Maker/reviewer iteration cap:** maximum 2 iterations before escalation. Define the count in code; do not let "N iterations" be ambiguous.
- **High-conviction split:** if two or more specialists hold opposite high-conviction views (e.g., fundamental BUY + macro SELL, both 8+/10 conviction), escalate. Do not let the synthesizer pick a side.
- **Missing primary data:** if a specialist's analysis depends on data the committee couldn't retrieve (delisted name, restricted filing, broken API), escalate. Do not let the committee proceed on imputed values.
- **Valuation sensitivity too wide:** if the DCF-based fair value range varies by >2x across reasonable assumptions, escalate. The thesis is more about sensitivity than analysis.
- **Unresolved regulatory or legal question:** if a thesis depends on assumed legal/regulatory outcome that is not yet resolved (pending litigation, antitrust review, FDA decision), surface explicitly with probability bands and escalate before sizing.
- **Evidence independence failure:** if all specialists are citing the same single source (the company's own 10-K, one analyst report, one news story), they aren't independent. Escalate or require additional sources.

### Independent first-pass (anti-anchoring discipline)

Every committee runs **parallel-first**: each specialist produces an independent analysis without seeing other specialists' outputs. Only after each specialist has committed their first-draft output may they see the others' work and revise (a single revision pass; further revisions require explicit reason). This prevents the first-speaker anchoring problem that pure-sequential committees suffer from (Tversky & Kahneman 1974; Anthropic 2025).

### Citations required for every specialist (not just devil's advocate)

The original output contracts required only the devil's advocate to cite evidence. Updated rule: **every specialist must list evidence + source per claim**. This enables an "evidence-independence audit": if four specialists make the same claim citing the same source, that's one signal in four voices — not four independent confirmations. Treat as such when computing conviction (Anthropic 2025; Cemri et al. 2025).

### Final output preserves unresolved disagreement

The portfolio manager / synthesizer is **forbidden from synthesizing fake consensus**. If specialists disagree, the disagreement is preserved in the final output (specifically in the `specialist_disagreements` and `unresolved_questions` fields of the PM contract — both already required). A clean "all agreed, conviction = 5/5" output is suspicious by default; the synthesizer should flag it for review.

## Output Contracts (per Role)

Every specialist must produce output in a structured format. Free-text outputs are review-hostile and unparseable downstream. **Per the new "citations required for every specialist" rule above, every contract below includes an `evidence_cited` field — list each material claim with its source. The synthesizer uses this to compute evidence-independence: if multiple specialists cite the same single source, conviction does NOT compound.**

### Fundamental Analyst Output Contract
```yaml
business_summary: <one paragraph>
roic_trend:
  five_year_avg: <%>
  direction: increasing | stable | decreasing
revenue_growth:
  five_year_cagr: <%>
  recent_quarters: [<list>]
margin_trend:
  gross: <%>
  operating: <%>
  direction: expanding | stable | compressing
fcf_quality:
  fcf_to_ni_ratio: <ratio>
  assessment: high | moderate | low
balance_sheet:
  net_debt_ebitda: <ratio>
  health: strong | adequate | weak
valuation:
  dcf_value_per_share: <$>
  dcf_assumptions: <one paragraph>
  comp_multiples_implied_price: <$>
  reverse_dcf_implied_growth: <%>
  fair_value_range: <$X - $Y>
key_risks: [<list of 3-5>]
evidence_cited:
  - claim: <one material claim>
    source: <filing / data source / URL with as-of date>
  - claim: <another claim>
    source: <source>
  # one row per material claim; minimum 5
confidence: 1-10
```

### Devil's Advocate Output Contract
```yaml
strongest_bear_case: <one paragraph>
evidence_cited: [<list with sources>]
falsification_criteria:
  - <observable event 1>
  - <observable event 2>
  - <observable event 3>
probability_of_bear_case: <0-1>
asymmetry_concern: <one sentence describing skew>
```

### Portfolio Manager Final Output Contract
```yaml
decision: BUY | HOLD | SELL | NO_ACTION
conviction: 1-5 stars
position_size_recommended: <% of portfolio>
time_horizon: <months>
expected_return: <%>
expected_drawdown: <%>
source_of_edge: informational | analytical | time_horizon | structural | behavioral | none
benchmark_comparison: <expected excess return vs SPY/VTI/cash, net of estimated costs + taxes>
bull_case: <one paragraph>
bear_case: <one paragraph>
catalysts: [<list of 2-3 with expected timing>]
falsification_criteria: [<list of 3-5>]
specialist_disagreements: <where did the committee diverge?>
unresolved_questions: [<list>]
evidence_independence_audit: <how many unique sources backed the bull case? Were they truly independent or did they trace to one filing/article?>
```

**Hard rule (per "default to no action" + market-efficiency burden of proof):** if `source_of_edge: none`, the decision MUST be `NO_ACTION`. If `benchmark_comparison` shows excess return below 2% annualized after costs/taxes, the decision SHOULD be `NO_ACTION` (the spread doesn't justify single-name risk + tax friction + opportunity cost) (Fama 1970).

## Calibration Enforcement

Confidence claims must be tracked and audited:
- Every output includes a confidence level (1-10 or stars or probability)
- Predictions logged to a database with: claim, confidence, horizon, falsification criteria, resolution date
- Periodic calibration reports: at confidence X%, do predictions actually resolve correctly X% of the time? (Brier 1950)
- Persistent miscalibration → adjust prompts, models, or weighting

Without calibration tracking, confidence claims are theatre.

## Anti-Patterns

| Anti-pattern | What it looks like | Fix |
|--------------|--------------------|-----|
| **Echo chamber** | All agents agree because they share training data + framing | Use different model providers; explicit adversarial role |
| **Anchor on first speaker** | Sequential committee where first agent's claim shapes all subsequent | Parallel-first; or randomize speaking order |
| **Synthesized fake consensus** | Synthesizer averages disagreement away; disagreement hidden | Mandatory "disagreement surface" section in output |
| **Risk officer as rubber stamp** | Risk officer always approves; never vetoes | Set hard policy rules; track veto rate |
| **Devil's advocate as ritual** | Bear case written perfunctorily, dismissed in synthesis | Bear case author must be a different model; synthesizer must explicitly address each bear point |
| **Specialist scope leakage** | Fundamental analyst opines on technicals; technical opines on valuation | Explicit role boundaries in prompts; output contract enforces scope |
| **Calibration drift** | Confidence claims unchecked; agents become overconfident | Calibration tracking + periodic audit |
| **Sequential as default** | Always run sequential without considering parallel | Choose protocol per question type |
| **Decision-without-falsification** | Output recommends action but doesn't say what would prove it wrong | Output contract requires falsification criteria |
| **Confidence inflation by aggregation** | "5 of 5 specialists agree therefore conviction = 5/5" — but if they share data sources, they're one signal in five voices | Track independence of evidence, not vote count |
| **LLM-in-backtest loop** | Calling LLM agents for every backtest day-by-day | Pre-compute signals to cache before backtest iteration |
| **No human escalation criteria** | Committee runs autonomously through ambiguity | Hard rules: split conviction, novel situation, destructive action → escalate |

## Information Integration Patterns

### Convergent (When agents agree)
- Surface evidence overlap (are they citing the same sources?)
- If yes → one signal in many voices; conviction not actually 5/5
- If no → genuine independent confirmation; high-conviction signal

### Divergent (When agents disagree)
- Do not average. Surface explicitly.
- Identify the crux: what specific fact or assumption do they differ on?
- Either resolve the crux (more data, expert input) or document as unresolved
- Position size reflects unresolved disagreement (smaller position, wider stops)

### Orthogonal (When agents address different dimensions)
- Fundamental analyst: business is strong. Technical analyst: chart is broken.
- These aren't conflicting; they describe different aspects.
- Synthesizer integrates: "strong business + bad timing" → wait for technical setup before buying

## Architecting a Committee for a Specific Question

For a question of type "should we buy X today?":
- **Minimum committee:** Fundamental analyst + Risk officer + Devil's advocate + Portfolio manager
- **Medium committee:** Add Technical analyst + Sentiment analyst
- **Full committee:** Add Quantitative analyst + Macro/sector specialist

Match committee size to question complexity. Single-name research = small committee. Strategy evaluation across regimes = larger.

For a question of type "screen 500 stocks for value candidates":
- Parallel pass with Quantitative analyst (factor screens) + Fundamental analyst (per-name brief review on top 20)
- No need for full committee at screen stage; deploy full committee on the shortlist

## Prompt Patterns

### Role Anchoring
Every agent prompt should begin with explicit role + scope + output contract:
```
You are the [ROLE]. You analyze [SCOPE]. You do not opine on [OUT-OF-SCOPE].
Produce output in the following YAML structure: [contract].
```

### Calibration Forcing
```
Provide a confidence level from 1-10. Below 7 means you'd want to see more evidence
before committing capital. 10 means you'd stake meaningful personal capital on this.
```

### Falsification Forcing
```
Before submitting, list 3-5 specific observable events that would prove your thesis wrong.
If you cannot name any, your thesis is not falsifiable and must be reframed.
```

### Bear Case Forcing (for non-bear specialists)
```
Construct the strongest possible case for the opposite of your conclusion.
Spend at least as much effort as on the original case. Cite evidence.
```

## Operational Checklist for Building a Committee
1. **Question type:** what kind of question is this? Screen? Single-name? Portfolio review? Strategy evaluation?
2. **Committee composition:** which specialists are needed?
3. **Debate protocol:** sequential, parallel, adversarial, iterative, hierarchical?
4. **Model diversity:** different providers for adversarial roles?
5. **Output contracts:** is every role producing structured output?
6. **Consensus mechanism:** voting, weighted, veto, escalation?
7. **Calibration tracking:** are confidence claims logged?
8. **Anti-pattern audit:** what's the biggest groupthink risk in this committee?
9. **Escalation criteria:** when does a committee output bump to human?
10. **Output contract for the final synthesizer:** is the final output structured + auditable?

If those 10 questions don't have clear answers, the committee is under-specified and will produce inconsistent results.

## Further Reading

- **Building Effective Agents** — Anthropic (2024). Defines evaluator-optimizer, routing, and orchestrator-worker patterns for agent systems.
- **Multi-Agent Research System** — Anthropic (2025). Production case study for parallel research agents, synthesis, and failure controls.
- **Agentic Design Patterns** — Andrew Ng (2024). Explains reflection and multi-agent debate as practical quality-improvement loops.
- **Why Do Multi-Agent LLM Systems Fail?** — Cemri et al. (2025). MAST taxonomy of system design, inter-agent misalignment, and verification failures.
- **Improving Factuality and Reasoning in Language Models through Multiagent Debate** — Du et al. (2023). Empirical reference for debate-style cross-checking across models.
- **Interpreting and Mitigating Hallucination in MLLMs through Multi-agent Debate** — Park et al. (2024). Debate protocol applied to hallucination mitigation in multimodal models.
- **A Multimodal Foundation Agent for Financial Trading: Tool-Augmented, Diversified, and Generalist** — Yu et al. (2024). Finance-domain agent architecture for trading research.
- **AlphaAgents: A Multi-Agent LLM Framework for Equity Portfolio Construction** — BlackRock (2025). Role-based finance committee pattern for equity portfolio construction.
- **Agents SDK** — OpenAI (2025). Handoffs and agent-as-tool patterns for composable agent systems.
- **Agent Development Kit** — Google (2025). Multi-agent workflow agents, delegation, evaluation, and deployment framework.
