---
description: "Equity research methodology — business model analysis, industry/sector analysis, Porter's five forces, competitive moats, management quality, valuation methods (DCF, comps, sum-of-parts), bull/bear cases, catalyst identification, investment thesis construction"
---
# Equity Research — Methodology Reference

> Reference for any agent conducting end-to-end stock research. The goal: produce an **investment thesis** that is specific, falsifiable, and grounded in evidence. This file is about *how to look*, not what to compute (see `finance-fundamentals` for ratios).

## The Research Stack (top-down → bottom-up)

A complete thesis usually has all six layers. Skipping any layer leaves blind spots.

```
1. Macro context        — what regime are we in (rates, growth, inflation, cycle)?
2. Sector / industry    — structure, growth drivers, regulatory landscape
3. Competitive position — moat, share, customer relationships
4. Business model       — how the company actually makes money, unit economics
5. Financials           — fundamentals, capital allocation, balance sheet health
6. Valuation + catalysts — what's priced in, what changes the price
```

Bottom-up investors (Buffett-style) start at (4) and work outward. Top-down (macro/sector) start at (1). Either is valid; **doing only one is incomplete.**

## Understanding the Business Model

Before any financial analysis, an agent must be able to answer in one paragraph:
- **What does the company sell?**
- **Who buys it?** (customer concentration, B2B vs B2C, geography)
- **How is it priced?** (subscription, transaction, ad-supported, hardware-margin, services)
- **What does it cost to deliver?** (variable vs fixed cost mix)
- **What's the sales motion?** (self-serve, direct sales, channel, retail)
- **What's the unit of economic analysis?** (per subscriber, per transaction, per device)

If an agent cannot produce this paragraph, no financial analysis will be meaningful. Common test: can you describe the company without using its name and without using buzzwords like "AI" or "platform"?

### Unit Economics
For subscription / SaaS businesses: **LTV / CAC, payback period, gross margin per customer, net dollar retention**.
For marketplaces: **take rate, GMV growth, supply/demand balance**.
For commerce: **AOV (average order value), repeat rate, contribution margin per order**.
For hardware: **ASP (average selling price), attach rates for services, replacement cycle**.

## Industry / Sector Analysis

### Porter's Five Forces (the classic checklist) (Porter 1980)
1. **Threat of new entrants** — barriers to entry (capital, regulation, brand, network effects, switching costs)
2. **Bargaining power of suppliers** — concentration, substitutes, switching costs for the firm
3. **Bargaining power of buyers** — concentration, price sensitivity, switching costs for buyers
4. **Threat of substitutes** — alternatives that solve the same job-to-be-done differently
5. **Industry rivalry** — number of competitors, growth rate, exit barriers, differentiation

High forces = profit margin compression over time. Low forces = profit pool persistence.

### Growth Drivers vs Headwinds
For any industry, name three of each. Be specific:
- ❌ Vague: "secular growth tailwinds"
- ✅ Specific: "US population aging 65+ growing 3% annually drives Medicare Advantage enrollment; CMS reimbursement updates set in Q1 each year"

### Regulatory & Cyclical Sensitivity
- Is this industry consolidating or fragmenting?
- What regulatory body matters? (FDA, FCC, OCC, FERC, EPA, state-level)
- Is this cyclical (housing, autos, semis, industrials, banks)? Where are we in the cycle?
- Is this secular (software, healthcare services, defense)?

## Competitive Position — The Moat

Moats are durable competitive advantages. Five common types (from Pat Dorsey / Morningstar framework) (Dorsey 2008):

| Moat Type | What it looks like | Examples |
|-----------|--------------------|----------|
| **Network effects** | Product gets more valuable as more people use it | Visa/Mastercard, Meta, marketplaces |
| **Switching costs** | Customers stuck due to integration, retraining, data | Enterprise SaaS, Oracle, ADP |
| **Cost advantage** | Lower unit cost than competition (scale, location, process, IP) | Walmart, GEICO, Costco |
| **Intangibles** | Brand, patents, regulatory licenses | Luxury brands, pharma, utilities |
| **Efficient scale** | Market only supports a few players profitably | Pipelines, airports, regional rail |

**ROIC > WACC consistently for >5 years is the financial fingerprint of a moat (Mauboussin and Callahan 2014).** Without that, claims of a moat are usually marketing.

### Moat Direction (not just presence)
Moats can be widening, stable, or narrowing. Examples:
- **Widening:** AWS network effects deepen as more enterprises commit
- **Stable:** Coca-Cola's brand persists but isn't getting stronger
- **Narrowing:** Cable TV, traditional broadcast networks, print media

Direction matters more than current level — a narrowing moat with high current ROIC will mean-revert.

## Management Quality

The hardest thing to assess, the most important over a multi-year horizon. Look for:

### Capital Allocation Track Record
Where has free cash flow gone over the last 5-10 years? Categorize:
1. Reinvestment in the business (R&D, CapEx, marketing) — what was the return?
2. Acquisitions — at what price, what synergies, how have they performed post-close?
3. Buybacks — bought at what price relative to current? (Buying at peaks destroys value)
4. Dividends — sustainable? Growing?
5. Debt paydown — strengthening balance sheet?
6. Cash hoarding — productive or a sign of indecision?

**Best management: takes value-creating investments, returns the rest, doesn't overpay for M&A.**

### Incentive Alignment
- **Insider ownership** — meaningful skin in the game?
- **Compensation structure** — what metrics drive bonuses? (Revenue growth? EPS? ROIC? Adjusted EBITDA? Stock price?) Whatever it measures, they will optimize for it.
- **Stock-based comp as % of revenue** — high (>10%) means founders/execs are extracting value via dilution
- **Related-party transactions** — flagged in DEF 14A proxy; can indicate self-dealing

### Communication Quality
- Read the last 8 earnings call transcripts. Does management directly answer questions or deflect?
- Compare guidance accuracy over time — chronically over-promising is a red flag
- Long-term shareholder letter quality (Buffett-style annual letters are a high bar; rare)

## Valuation Methods

No method is "right" — triangulate across multiple.

### Discounted Cash Flow (DCF) (Damodaran 2012)
- Project FCF for 5-10 years, discount at WACC, add terminal value
- **Extremely sensitive to terminal growth rate and discount rate.** A 1% change in discount rate can swing intrinsic value 20-30%.
- Best used as a sensitivity tool, not a precision tool
- Useful prompt: "what assumptions about growth and margin do I have to believe for today's price to be fair?"

### Comparable Companies (Comps / "Multiples")
- Pick 5-15 truly comparable companies (same industry, similar size, similar growth, similar capital intensity)
- Compare on EV/EBITDA, EV/Sales, P/E, P/B, FCF Yield
- Adjust for growth differential (PEG-style)
- **The hardest part is picking comps honestly.** Most analysts cherry-pick comps that flatter the thesis.

### Sum-of-the-Parts (SOTP)
- For conglomerates with distinct businesses (e.g., AMZN: retail + AWS + ads)
- Value each segment separately using appropriate comps
- Add cash, subtract debt, subtract corporate overhead
- Useful when one segment is masking another (the "hidden gem" thesis)

### Reverse DCF (Damodaran 2012)
- Take today's stock price as given
- Solve for what growth + margin + capital intensity assumptions are implied
- Useful for asking: "Is the market expecting something realistic, or extraordinary?"

### Asset-Based / Liquidation Value
- For deeply discounted situations, distressed, or holding companies
- Mark every asset to realizable value; subtract liabilities
- Floor value; useful margin-of-safety check for value plays

## Edge Identification — The Market-Efficiency Burden of Proof

**Default assumption: the market is mostly right (Fama 1970).** Current price reflects public information reasonably well. A thesis that the market is wrong about a specific stock must identify a credible **source of edge** — otherwise the most likely explanation is that the agent's reasoning is shallower than the consensus.

### Five recognized sources of edge
1. **Informational** — access to data the market hasn't priced (rare for public-equity retail; mostly institutional)
2. **Analytical** — better interpretation of the same data (deeper accounting analysis, better industry context, better synthesis across disclosures)
3. **Time-horizon** — willingness to hold through volatility / multi-year drawdowns that institutional capital cannot tolerate
4. **Structural** — forced selling (index removal, redemptions, regulatory mandates) creates temporary mispricing
5. **Behavioral** — narrative-driven overreaction or underreaction by the broad market

### Rule
**If a thesis cannot identify which of these edge sources applies — and back it with specific evidence — the correct output is `NO_ACTION`.** "Looks cheap" or "good company at a fair price" without an edge source is not a thesis; it's a vibe.

### Benchmark Comparison (Mandatory)
Every recommendation must answer: **"Why not just hold SPY / VTI / cash / T-bills instead?"** The hurdle for active selection is:
- **Beat the benchmark** by enough to compensate for transaction costs, taxes, time spent, and the discomfort of single-name risk
- A position that's expected to return 10% over a year when the index is expected to return 9% is **not worth holding** for a retail investor — the spread doesn't cover taxes + opportunity cost
- "Default to no action" is the correct stance when the expected excess return doesn't clear this hurdle

## Building the Thesis

A complete thesis answers:
1. **What is the business?** (one paragraph)
2. **Why is it mispriced?** (information asymmetry, narrative-driven mispricing, time-arbitrage, complexity discount, forced selling, sentiment overreaction)
3. **What is the source of edge?** (See "Edge Identification" above. If unclear → NO_ACTION.)
4. **Why not just buy SPY?** (Mandatory benchmark comparison — does expected excess return clear the hurdle?)
5. **What is the expected return?** (price target with timeframe + IRR estimate)
6. **What is the catalyst?** (what specific event resolves the mispricing? Earnings beat? Spin-off? Re-acceleration? Acquisition?)
7. **What is the risk?** (specific scenarios that break the thesis, with probabilities)
8. **What would prove me wrong?** (the falsification criteria — see `behavioral-finance` for why this matters)
9. **What is the position size?** (see `risk-portfolio`)

Theses that lack any of (3), (4), (6), (7), or (8) are not theses — they're vibes. Output `NO_ACTION` instead.

## Bull / Bear Cases

For every thesis, force the agent to write both:
- **Bull case** — what happens if I'm right? Specify P&L impact, multiple expansion, IRR
- **Base case** — what's the most likely outcome? (often the boring case)
- **Bear case** — what happens if the thesis fails? What's the downside?

Asymmetry is the goal: **bull case 3x upside, bear case 30% downside, base case 50% return over 3 years** is a much better setup than "looks cheap."

## Catalyst Identification

Mispricings can persist for years without a catalyst. Catalysts force re-rating:
- **Earnings catalysts:** beat-and-raise quarter, guidance reset, margin inflection
- **Corporate actions:** spin-off, divestiture, large buyback announcement, acquisition (buyer or target)
- **Industry catalysts:** regulatory change, technology shift, supply/demand inflection
- **Management changes:** new CEO with track record
- **Index inclusion / forced buying**
- **Activist involvement**

"Cheap stock with no catalyst" can stay cheap. Time decay (cost of capital) matters.

## Common Research Mistakes
- **Anchoring to current price.** Asking "is this cheap?" instead of "what is this worth?" The market price is just an opinion.
- **Cherry-picking comps** to flatter the thesis. Comps should be picked *before* computing.
- **Extrapolating recent trends** without questioning sustainability. Hot quarter ≠ secular shift.
- **Confusing a good business with a good investment.** Great companies at terrible prices = bad investments.
- **Confusing a low P/E with cheapness.** Value traps abound; low multiples often reflect deteriorating fundamentals.
- **Ignoring share count growth.** "Earnings doubled!" can hide 30% dilution.
- **Falling for the management narrative.** Earnings calls are sales pitches.
- **Skipping the bear case** because it's uncomfortable.
- **Assuming acquisitions will deliver promised synergies.** Most don't.
- **Confusing being early with being wrong** (and vice versa).

## Operational Checklist for Researching a Stock
1. Read the company description (Wikipedia + investor relations site) — produce the one-paragraph business model
2. Read the latest 10-K (focus on Items 1, 1A, 7, 8 — see `sec-filings`)
3. Read the last 4 earnings call transcripts
4. Pull 5-10 years of financials (revenue, margins, ROIC, FCF, share count, debt)
5. Identify 5-10 comparable companies; pull their same metrics
6. Identify the moat (or lack thereof); state direction (widening/stable/narrowing)
7. Identify 3 growth drivers and 3 headwinds
8. Build a valuation triangulation (DCF + Comps + Reverse DCF minimum)
9. Write the bull / base / bear cases with specific numbers
10. List 2-3 catalysts with expected timing
11. List 3-5 specific risks with probabilities
12. State falsification criteria — what would change your mind?
13. Decide position size based on conviction × asymmetry × portfolio fit (see `risk-portfolio`)

If an agent cannot complete all 13 steps with specific, ticker-grounded content, the thesis is not ready.

## Further Reading

- **Competitive Strategy** — Michael E. Porter (1980). Foundational industry-structure analysis and Five Forces framework.
- **Competitive Advantage** — Michael E. Porter (1985). Value-chain and cost/differentiation framework for competitive positioning.
- **The Little Book That Builds Wealth** — Pat Dorsey (2008). Practical economic-moat taxonomy used in equity research.
- **Investment Valuation** — Aswath Damodaran (2012). DCF, relative valuation, and reverse-engineering market expectations.
- **Value Investing: From Graham to Buffett and Beyond** — Bruce Greenwald et al. (2001). Sustainable competitive advantage and intrinsic-value analysis.
- **Measuring the Moat** — Michael J. Mauboussin and Dan Callahan (2014). ROIC durability and competitive advantage assessment.
- **Berkshire Hathaway Letters to Shareholders** — Warren Buffett (1977–present). Long-form examples of business-quality and capital-allocation thinking.
- **One Up on Wall Street** — Peter Lynch (1989). Practical retail-investor business research and scuttlebutt discipline.
- **The Little Book That Still Beats the Market** — Joel Greenblatt (2010). Quality-plus-value screening through return-on-capital and earnings-yield lenses.
- **Efficient Capital Markets: A Review of Theory and Empirical Work** — Eugene F. Fama (1970). Classic statement of the efficient-market baseline.
