---
description: "Risk management and portfolio construction — position sizing, Kelly criterion, Sharpe ratio, Sortino, max drawdown, volatility, beta, correlation, diversification math, concentration limits, VaR, expected shortfall, rebalancing, tail risk"
---
# Risk & Portfolio Construction — Operational Reference

> Stock picking generates returns; risk management determines whether you keep them. This file covers position sizing, portfolio construction, and risk metrics with operational definitions an agent can compute and reason about.

## The Two Risks

| Risk type | Source | Diversifiable? |
|-----------|--------|----------------|
| **Specific / idiosyncratic** | Company-specific (earnings miss, fraud, key personnel, product failure) | Yes (with sufficient names) |
| **Systematic / market** | Market-wide (recession, rate shock, geopolitical) | No (only by reducing equity exposure) |

Diversification removes specific risk. It does **not** remove market risk (Markowitz 1952; Sharpe 1964). A 100-stock portfolio is still subject to 2008-style drawdowns.

## Volatility & Return Distribution

### Standard Deviation
- Measure of dispersion around the mean
- For returns: annualized σ = daily σ × √252 (Lo 2002)
- US large-cap equity: ~15-20% annualized historically
- High-quality bonds: ~4-7%
- Single stocks: 25-60% typical; individual names regularly 40-80%

### Why Standard Deviation Misleads
- Assumes symmetric (normal) distribution; equity returns are **skewed and fat-tailed** (Taleb 2007)
- 1987 crash, 2008, March 2020 are >10σ events under normal assumption; they happen every ~7-10 years empirically
- Use **downside deviation** (semi-deviation) for asymmetric risk concerns

### Downside Deviation
σ_down = √(Σ min(r_i − target, 0)² / N)
- Only penalizes returns below a target (usually 0 or risk-free rate)
- Used in Sortino ratio (Sortino & Price 1994)

## Risk-Adjusted Return Metrics

### Sharpe Ratio
**Sharpe = (R_portfolio − R_risk_free) / σ_portfolio** (Sharpe 1966)

- Excess return per unit of volatility
- Sharpe > 1.0 is good for a stock-picking strategy
- Sharpe > 2.0 is excellent and rare over long periods
- Sharpe > 3.0 sustained = likely hidden risk, leverage, or fraud (LTCM had >4 before blowing up; Madoff claimed near-monotonic returns implying Sharpe ~2.5+ — both were frauds)
- **Note: Sharpe is conventionally annualized.** When computed from daily returns, multiply by √252; from monthly, by √12. Always disclose the cadence; comparing daily-computed Sharpe to annualized Sharpe is meaningless (Lo 2002).
- **Caveat:** assumes returns are normal; understates risk for fat-tailed strategies (options selling, merger arb)

### Sortino Ratio
**Sortino = (R_portfolio − R_target) / σ_downside** (Sortino & Price 1994)
- Like Sharpe but only penalizes downside volatility
- Higher than Sharpe for skewed-positive strategies
- Lower than Sharpe for skewed-negative strategies (selling vol)

### Calmar Ratio
**Calmar = Annualized Return / |Max Drawdown|**
- Captures pain-adjusted return
- 1.0+ over 3-5 years is good

### Information Ratio
**IR = (R_portfolio − R_benchmark) / σ(R_portfolio − R_benchmark)**
- Active return per unit of active risk (tracking error)
- Used to evaluate active management vs benchmark
- IR > 0.5 sustained is rare; > 1.0 is elite

### Treynor Ratio
**Treynor = (R_portfolio − R_risk_free) / β_portfolio** (Treynor 1965)
- Excess return per unit of systematic risk (beta), not total risk
- Used in CAPM framework

## Drawdown Analysis

### Maximum Drawdown
- Largest peak-to-trough decline in equity curve
- US large-cap equity: ~-55% (2008-2009), ~-50% (2000-2002), ~-34% (Mar 2020)
- Single stocks regularly hit -70% or worse
- **The number that most matters to investor survival.** Sharpe doesn't capture the difference between -20% and -50% drawdown if both reach the same end value.

### Time to Recovery
- How long to regain prior peak
- S&P 500 took 4 years (2000-2002 peak to 2007 peak), 5+ years (2007 peak to 2013), <1 year (Mar 2020 to Aug 2020)
- Long recoveries break investor psychology (and capital allocations)

### Ulcer Index
- Square-root of average squared drawdown
- Penalizes long, deep drawdowns more than short shallow ones
- Better single-number drawdown measure than max DD alone

### Underwater Curve
- Plot of (current value / running peak) − 1 over time
- Shows depth and duration of drawdowns visually
- Always include in backtest reports

## Position Sizing

### Fixed Fractional
- Each position = X% of portfolio (e.g., 2-5% per name)
- Simple, robust, prevents single-position blowups
- 20-position portfolio at 5% each = standard mid-concentration

### Volatility-Adjusted (Risk Parity-style)
- Each position contributes equal risk (not equal dollars)
- Position size = (target risk per position) / (position volatility)
- High-vol stocks get smaller weights, low-vol get larger
- Used in CTAs, hedge funds

### Kelly Criterion
**f* = (p × b − q) / b** (Kelly 1956)
where p = win probability, b = win/loss ratio, q = 1 − p

- Mathematically optimal fraction to bet for long-run wealth maximization
- **In practice: use fractional Kelly (typically 0.25 to 0.5 of full Kelly).** Full Kelly leads to ~50% drawdowns; fractional smooths the ride (Thorp 2006)
- Requires accurate probability estimates (most investors overestimate edge → over-bet)
- **For equities, Kelly is rarely above 5-10% per position even for high-conviction views.** "All in" bets are almost always wrong-sized

### Conviction-Weighted
- Position size scales with conviction (1-5 star or letter-grade system)
- Highest-conviction = 8-10%, lowest-conviction = 1-2%
- Subjective but enforces position-size discipline

### Concentration Limits
Recommended hard caps for non-professional portfolios:
- **No single position > 10% at cost** (let winners run, but don't add at higher cost basis)
- **No single position > 20% at market** (force trim if a winner gets there)
- **No sector > 30%**
- **No single thesis > 25%** (multiple positions sharing a thesis count as one)

## Diversification

### Number of Holdings
- ~15-20 stocks captures ~85% of diversification benefit (vs holding the market)
- ~30 captures ~95% (Evans & Archer 1968)
- Beyond 30, you're "diworsifying" — closet-indexing without index-fund cost structure
- Counter-argument: concentrated investors (Buffett, Pabrai, Greenblatt) hold 5-15 names and rely on conviction

### Correlation Matters More Than Count
- 30 stocks all in tech sector ≠ diversified
- Compute correlation matrix; aim for clusters of low-correlation positions
- Long-term equity correlations: ~0.3-0.5 within sectors, ~0.1-0.3 across sectors, but **all correlations spike to 0.7+ in crises** (the cruel irony of diversification)

### Cross-Asset Diversification
- Stocks ↔ bonds historically negative correlation (60/40 portfolio rationale)
- 2022 broke this: stocks and bonds both fell ~15-20% (rates rose with growth fears)
- Alternatives: gold (uncorrelated long-term), real estate (correlated with equities short-term), TIPS (inflation hedge), commodities (cyclical)

## Beta & CAPM

### Beta
- Sensitivity to market returns
- β = covariance(asset, market) / variance(market)
- β = 1.0: moves with market
- β > 1.0: amplifies market moves (high beta — tech, small caps, leveraged plays)
- β < 1.0: dampens market moves (low beta — utilities, staples, healthcare)
- β < 0: moves opposite market (rare — gold sometimes, VIX-related products)

### CAPM
- E(R_asset) = R_risk_free + β × (E(R_market) − R_risk_free) (Sharpe 1964)
- "Expected return is compensated only for systematic risk"
- Theoretical framework; rarely matches reality precisely
- Practical use: rough cost-of-equity estimate for DCF (8-10% typical for US equity)

### Beta's Limits
- Estimated from historical data; varies over time
- Different windows (3yr vs 5yr) give different betas
- Bear-market beta often higher than bull-market beta (asymmetric risk)
- Beta only captures linear sensitivity to market; misses convexity (options, distressed)

## Tail Risk

### Value at Risk (VaR)
- "At X% confidence over horizon T, loss is **no greater than** Y" — equivalently, the probability of a loss exceeding Y is (1−X%)
- 95% 1-day VaR of -2% = "95% chance we don't lose more than 2% tomorrow"
- **VaR says nothing about the 5% tail.** A strategy with -2% VaR and -50% tail is more dangerous than one with -3% VaR and -10% tail
- Most famous critique: Taleb on VaR pre-2008 (Taleb 2007)

### Conditional VaR (Expected Shortfall)
- Expected loss *given* you're in the tail beyond VaR
- "If we're in the worst 5% of days, average loss is X%"
- Better tail measure than VaR; coherent risk metric (subadditive) (Artzner et al. 1999)

### Fat-Tail Awareness
- Equity returns are not normal; kurtosis is much higher than 3
- Multi-σ events ("black swans") happen more often than Gaussian predicts
- Strategies that depend on normal distribution assumptions (some options models, mean-reversion at edges) will eventually break
- **Healthy paranoia is a risk-management discipline.**

## Rebalancing

### Why
- Drift away from target allocations over time as positions move
- Rebalancing forces "sell high, buy low" — anti-momentum discipline
- Captures volatility harvesting premium

### When
- **Calendar-based:** quarterly or annual rebalance (simple, low cost)
- **Threshold-based:** when any position drifts >5% from target (better but more transactions)
- **Hybrid:** check quarterly, rebalance if threshold breached

### Tax Drag
- Rebalancing in taxable accounts triggers capital gains
- Tax-loss harvesting can offset
- Long-term holders (1+ year) get preferential rates in US
- Tax-advantaged accounts (IRA, 401k) don't have this issue

### When NOT to Rebalance
- Strong-momentum periods: rebalancing trims winners that may run further
- Drifting up into a quality compounder = often correct to let it run
- Buffett: "Lethargy bordering on sloth remains the cornerstone of our investment style"

## Common Risk Mistakes
- **Over-betting on conviction** — Kelly overestimates apply
- **Confusing volatility with risk** — vol is a measure, risk is permanent loss of capital
- **Diversification = many similar names** (30 tech stocks)
- **Stop-losses based on price, not thesis** — selling at -10% on a value position can be exactly wrong
- **No portfolio-level view** — sum of positions reveals concentrations not visible per-position
- **Ignoring correlation regime changes** — crises break correlation models
- **Optimizing risk metrics in backtest** — Sharpe-maximized portfolios often have hidden tail risk
- **Confusing tracking error with risk** — outperforming the benchmark by 5% on the upside is "tracking error" but isn't a risk
- **Not pre-committing position sizes** before buying — size in the heat of the moment is usually wrong

## Operational Checklist for Portfolio-Level Health
1. **Concentration:** any position > 10%? Any sector > 30%?
2. **Correlation:** are top holdings clustered (all-tech, all-financials, all-China-exposed)?
3. **Beta:** is portfolio beta where you want it given market view?
4. **Drawdown tolerance:** if market fell 30%, what's the portfolio drawdown? Comfortable?
5. **Cash position:** appropriate for opportunity set or just inertia?
6. **Position vintage:** how many names have you owned >2 years? Are they outdated theses?
7. **Tax overhang:** what would liquidation cost in unrealized gains?
8. **Liquidity:** could you exit the worst 10% positions in a day without major impact?
9. **Rebalance status:** any positions outside threshold?
10. **Thesis review:** when did you last re-evaluate each position?

If an agent is asked to assess portfolio risk, it should produce numbers for at least items 1-5, not vague characterizations.

## Further Reading

- **Portfolio Selection** — Markowitz (1952). Foundational modern portfolio theory and diversification framing.
- **Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk** — Sharpe (1964). Introduces CAPM and beta as systematic risk.
- **Mutual Fund Performance** — Sharpe (1966). Defines the Sharpe ratio for risk-adjusted fund performance.
- **Performance Measurement in a Downside Risk Framework** — Sortino & Price (1994). Formalizes downside-risk performance measurement and the Sortino ratio.
- **How to Rate Management of Investment Funds** — Treynor (1965). Introduces return per unit of systematic risk.
- **A New Interpretation of Information Rate** — Kelly (1956). Derives log-optimal bet sizing under edge and odds assumptions.
- **The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market** — Thorp (2006). Practical argument for fractional Kelly sizing discipline.
- **The Statistics of Sharpe Ratios** — Lo (2002). Shows why Sharpe comparisons require care with sampling, autocorrelation, and annualization.
- **Coherent Measures of Risk** — Artzner et al. (1999). Establishes coherence properties behind expected shortfall preferences over VaR.
- **The Black Swan** — Taleb (2007). Tail-risk and model-risk critique relevant to VaR and Gaussian assumptions.
