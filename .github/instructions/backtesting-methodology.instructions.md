---
description: "Backtesting methodology — survivorship bias, look-ahead bias, point-in-time data, walk-forward analysis, out-of-sample testing, transaction costs, slippage, market impact, overfitting, multiple comparisons, regime sensitivity, statistical vs economic significance, honest reporting"
---
# Backtesting Methodology — How Not to Lie to Yourself

> A backtest tells you what *would have* happened if a strategy *had been* executed historically. Almost every published backtest is wrong in ways that flatter the strategy. This file describes the disciplines required to make a backtest worth trusting.

## The Fundamental Problem

In any sample of historical data, with enough trials, a strategy that looks profitable will emerge **by random chance alone** (Bailey et al. 2014; Harvey, Liu & Zhu 2016). The bar for believing a backtest is therefore much higher than "Sharpe > 1.0 on history."

**Most published quantitative strategies fail to replicate out-of-sample.** Academic finance has a replication crisis: most "factors" don't survive multiple-comparisons adjustment (Harvey, Liu & Zhu 2016).

The discipline of backtesting is the discipline of **defeating your own confirmation bias**.

## Survivorship Bias — the Silent Killer

**Definition:** Backtesting on a universe of currently-listed companies excludes those that went bankrupt, were acquired, or were delisted. Results are systematically inflated.

### How It Manifests
- Use `yfinance` to get "all S&P 500 stocks since 2000" → only get current S&P 500 members, weighted by historical prices
- Backtest "buy small caps with low P/B from 2000-2010" → never sees Enron, Bear Stearns, WaMu, Circuit City, Lehman
- **Inflates returns by 1-3% annually on equity strategies** depending on universe

### Counter-Strategies
- Use a point-in-time universe with full death history (Norgate Data, Sharadar SF1, CRSP)
- For free-tier work: maintain a manual delisting log; query Wikipedia historical revisions for index membership
- Disclaim in every backtest report: "universe construction method: X; survivorship-cleaned: yes/no"
- If survivorship-cleaned data unavailable, apply a conservative haircut (subtract 1-2% from annualized return)

## Look-Ahead Bias — the Subtle Killer

**Definition:** Using information in the backtest that wouldn't have been available at the simulated decision time.

### Common Sources
| Source | What it looks like | Fix |
|--------|-------------------|-----|
| **Restated financials** | Using restated 10-K values for backtest dated before the restatement | Use as-filed values; edgartools preserves filing-date snapshots |
| **Index membership** | "Was AAPL in the S&P on 2018-06-15?" — using today's membership rosters | Use historical index reconstitution data |
| **Symbol changes** | Treating FB and META as different histories | Maintain ticker history (CIK-based identity in SEC data) |
| **Earnings release dates** | Using fiscal-period date as available date (it's not — there's a 30-90 day lag to filing) | Use filing date, not period date |
| **Analyst estimates** | Using "consensus on date X" that was actually revised post-event | Use point-in-time consensus snapshots |
| **News sentiment** | Using news APIs that backfill or re-tag historical articles | Snapshot daily and read snapshots, never live |
| **Stock split adjustments** | Using current adjusted prices for backtests where unadjusted matters | Be explicit about adjustment policy |
| **Closing price as fill price** | Trades that "fill at close" assume you could trade at the closing print — you can't unless using market-on-close orders | Use next-day open (or VWAP) as fill assumption |
| **Survivorship in news/data feed** | Source has been pruned of bankrupt-name records | Audit the data source |

### General Rule
**At decision time T, a strategy can only use information knowable at time T.** Enforce this in code: data fetches should take an `as_of` parameter; sources that can't honor it should be wrapped in daily snapshot caches.

## Point-in-Time Data Discipline

### What "PIT-safe" Means by Source Type
| Source | PIT-safe by default? |
|--------|---------------------|
| OHLCV stock prices (historical) | ✅ Yes (historical bars are historical) |
| Adjusted prices | ⚠️ Be careful — adjustments are applied retroactively for splits/dividends |
| Fundamentals via yfinance | ❌ Returns latest reported values, not as-of |
| Fundamentals via XBRL on filings (edgartools) | ✅ Yes (each filing is a snapshot of what was known at filing date) |
| Index membership | ❌ Live APIs return current members |
| Earnings estimates (consensus) | ❌ Live APIs return current estimates (revised) |
| News articles | ⚠️ Depends — some sources backfill or update historical coverage |
| Insider transactions (Form 4) | ✅ Yes — Form 4 has filing date (not transaction date) for as-of |
| Congressional trades (Quiver) | ✅ Yes — disclosure date is immutable |
| Macro economic data | ⚠️ Revised after initial release (use ALFRED at FRED for vintage data) |

### Snapshot Pattern for Non-PIT Sources
For any source that doesn't honor as-of natively:
- Snapshot daily (or appropriate cadence) to `data/snapshots/<source>/<YYYY-MM-DD>/...`
- Query reads the most recent snapshot ≤ `as_of`
- Disclose in backtest reports: "PIT enforcement: as-of via snapshot store; coverage starts YYYY-MM-DD"
- Reports run on dates before snapshot coverage = downgrade to "PIT_PARTIAL" or refuse

## Out-of-Sample Testing

### Why
In-sample fitting can produce spurious patterns. Out-of-sample data is the only honest test.

### Patterns
**Train/Test Split (Simple)**
- Use first 70% of history for development; last 30% for validation
- Test set must never be looked at during strategy development
- Once tested, the test set is "burned" — no further iteration on that data without bias creeping back

**Walk-Forward Analysis**
- Train on a rolling window (e.g., 5 years), test on the next year, then advance
- Better mimics how a strategy would actually be developed and refined over time
- Most realistic single methodology for time-series strategies

**Cross-Validation (CAREFUL)**
- Standard k-fold CV is **wrong for time series** — randomly shuffles future into training, causing leakage (López de Prado 2018)
- Use time-series CV (sequential folds, train < test in time order)
- Even time-series CV can leak if returns are auto-correlated or features have lookahead structure

### Anti-Patterns
- "Re-optimizing parameters when strategy stops working" — that's overfitting in slow motion
- "We tested 10 strategy variants and picked the best" — 1 in 20 random strategies passes a 95% significance test by chance; you need correction for multiple comparisons (Harvey, Liu & Zhu 2016)

## Overfitting & Multiple Comparisons

### The Core Issue
Try enough strategy variants and one will look great by chance. With 100 variants, you expect ~5 to pass at p<0.05 even if all are noise (Bailey et al. 2014).

### Symptoms of Overfit Strategies
- Many parameters relative to data points
- Strategy works only on specific universe / timeframe / parameters
- Edge case rules ("don't trade on Fridays in October") suggest curve-fitting
- Sensitivity tests show large performance variance for small parameter changes
- In-sample Sharpe > 2.0, out-of-sample Sharpe < 0.5

### Counter-Strategies
- **Pre-register hypotheses** (write down the strategy before backtesting)
- **Limit parameters** — fewer is better; default values without tuning preferred
- **Sensitivity analysis** — perturb parameters; if performance collapses, you've overfit
- **Out-of-sample is sacred** — test once, accept the result
- **Bonferroni / FDR correction** for multiple-strategy testing (Harvey, Liu & Zhu 2016)
- **Combinatorial Purged CV** for more robust evaluation (López de Prado 2018)
- **Deflated Sharpe Ratio** accounts for number of trials and non-normality (Bailey et al. 2014)

### Decision Rule
If a strategy needs 20 trials of variant-tweaking before it works, the effective p-value is much worse than the single-test p-value. Be honest about how many variants were tested.

## Transaction Costs & Realistic Execution

### Costs to Model
| Cost | Magnitude | Notes |
|------|-----------|-------|
| **Commissions** | $0 for most US retail brokers now | Was $5-10 pre-2019 |
| **Bid-ask spread** | 1-50 bps for liquid; 50-500 bps for illiquid | Half-spread paid per trade |
| **Slippage** | 1-100 bps depending on size + liquidity | Larger orders move price |
| **Market impact** | Scales with √(order size / ADV) (Almgren et al. 2005) | Significant for >1% of ADV |
| **Borrow cost (shorts)** | 25-500 bps annually for hard-to-borrow | Easy-to-borrow names: 25-50 bps |
| **Taxes** | 15-40% on gains depending on jurisdiction + holding period | Backtest pre-tax for strategy validation; net-of-tax for personal use |
| **Margin interest** | 5-10% annually for leveraged strategies | Compounds |

### Realistic Fill Assumptions
- **Closing print fills are unrealistic** for retail (only MOC orders can fill at the print exactly; size is limited)
- **Use next-day open or VWAP** for retail-realistic fills
- **Add slippage estimate** = function of order size / ADV
- **For small caps** — consider 20-50 bps slippage even on small orders
- **For backtests with high turnover** — costs can erase the entire edge

### Rule of Thumb
If your backtest doesn't include transaction costs, **subtract 1-2% annualized for medium-frequency strategies, 5-10%+ for high-frequency**. If the strategy still works, you might have something.

## Regime Sensitivity

### Why It Matters
A strategy that works 2009-2021 may not work 2022 (regime change: rates rising, multiples compressing, growth de-rating).

### Test Across Regimes
- Bull market: 2003-2007, 2009-2020 (most)
- Bear markets: 2000-2002, 2007-2009, 2022
- Sideways: 2015-2016, 2018, parts of 2023
- High-vol: 2008, March 2020, 2022
- Low-vol: 2017, parts of 2021

If a strategy only works in bull markets, it's a beta-trade with extra steps. Report per-regime returns separately, not just aggregate.

### Macroeconomic Regimes
- Inflation regimes: low/stable (2009-2021), rising (2022-2024)
- Rate regimes: zero-bound (2009-2021), rising (2022+)
- Credit cycles: tight (2008-2009, 2020 Q2), loose (most of 2010s)

## Sample Size & Statistical Significance

### How Much Data Is Enough?
- Daily returns over 10 years = ~2,500 observations (sounds like a lot)
- But adjacent observations are not independent (auto-correlation)
- Effective sample size for monthly strategies over 10 years: ~120 observations
- **Quarterly rebalancing over 10 years: 40 observations** — not enough for confident inference

### Statistical Significance
- Sharpe ratio significance (annualized Sharpe, T years of data, assuming i.i.d. returns): **`t = Sharpe_annualized × √T`** (Lo 2002)
- For 10 years of data, Sharpe 1.0 has t-stat ~3.16 → "significant" — but the i.i.d. assumption is rarely true; autocorrelation inflates the apparent t-stat, making p-values look more impressive than they are
- But: many adjustments needed (multiple testing, non-normality, autocorrelation)
- Use **Probabilistic Sharpe Ratio** for more honest measure that accounts for skew/kurtosis + sample size (Bailey & López de Prado 2012)

### Economic vs Statistical Significance
- A Sharpe of 0.3 might be statistically significant with enough data
- But 0.3 Sharpe < pure equity beta — not economically interesting
- Bar: significant **AND** large enough to justify the operational complexity

## Reporting: What Every Backtest Report Must Include

A backtest report that omits any of these is misleading. Use this as a template:

```
STRATEGY: [name + version]
UNIVERSE: [size, definition, survivorship-cleaned: yes/no]
DATE RANGE: [start - end]
REBALANCE FREQUENCY: [daily/weekly/monthly/quarterly]

OUT-OF-SAMPLE PERIOD: [yes/no — if no, explain]
NUMBER OF VARIANTS TESTED: [N] — if >1, apply correction
PRE-REGISTERED: [yes/no]

PERFORMANCE:
  CAGR: X%
  Sharpe: X (Probabilistic Sharpe: Y)
  Sortino: X
  Max Drawdown: X% (duration: Y days)
  Calmar: X
  
  BENCHMARK (e.g., SPY): CAGR, Sharpe, Max DD for comparison
  ALPHA vs Benchmark: X% annualized
  TRACKING ERROR: X%
  INFORMATION RATIO: X

COSTS ASSUMED:
  Commission: $X/trade
  Slippage: X bps per side
  Borrow cost (shorts): X bps annualized
  Fill assumption: [closing / next-day open / VWAP]

PIT DISCIPLINE:
  Survivorship-cleaned universe: yes/no
  Point-in-time fundamentals: yes/no
  Point-in-time index membership: yes/no
  Snapshot coverage: [date range]
  PIT grade: STRICT / PARTIAL / INVALID

REGIME ATTRIBUTION:
  Performance by regime: bull / bear / sideways / high-vol / low-vol

SENSITIVITY:
  Parameter perturbation: range of Sharpe over ±20% parameter changes
  Universe perturbation: Sharpe with random 20% universe subset
  
NOT SHAREABLE if PIT grade is INVALID without explicit override flag.
```

## The Honesty Checklist

Before believing a backtest:
1. ❓ Is the universe survivorship-cleaned?
2. ❓ Are fundamentals point-in-time (as-of decision date)?
3. ❓ Is index membership point-in-time?
4. ❓ Are transaction costs included realistically?
5. ❓ Is the fill assumption realistic (not closing print)?
6. ❓ Was there an out-of-sample test?
7. ❓ How many strategy variants were tested? Was multiple-comparisons correction applied?
8. ❓ Does the strategy work across regimes?
9. ❓ Is the sample size large enough?
10. ❓ Is the result economically meaningful (not just statistically significant)?
11. ❓ Are the parameters minimal (not curve-fit)?
12. ❓ Does sensitivity analysis show robustness?
13. ❓ Are the costs assumed comparable to your actual broker?
14. ❓ Do the results survive when applied to a different universe / time period?

A strategy that passes all 14 is rare. Most published strategies pass 3-5 and are oversold accordingly.

## Common Backtest Mistakes (Quick Reference)
- Backtesting current S&P 500 members (survivorship)
- Using "today's" fundamentals on historical dates (look-ahead)
- Filling at closing print (impossible at retail)
- No transaction costs (or $0 commissions but missing slippage)
- Random k-fold CV on time-series (leakage)
- Optimizing parameters then reporting in-sample Sharpe
- Cherry-picking universe ("works on tech stocks 2010-2020")
- Cherry-picking date ranges ("works 2009-2021", omitting 2022)
- Not adjusting for multiple-comparisons after testing many variants
- Reporting in-sample only without out-of-sample validation
- Confusing simulation P&L with reachable real-world P&L
- Backtesting LLM-driven signal generation by calling the LLM live during the loop (catastrophic cost) → see `multi-agent-finance-patterns` for the precompute pattern

## Further Reading

- **...and the Cross-Section of Expected Returns** — Harvey, Liu & Zhu (2016). Documents the multiple-testing problem behind the factor-zoo replication crisis.
- **The Sharpe Ratio Efficient Frontier** — Bailey & López de Prado (2012). Introduces the Probabilistic Sharpe Ratio for non-normal return distributions.
- **The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality** — Bailey, Borwein, López de Prado & Zhu (2014). Adjusts Sharpe significance for trials, selection bias, and non-normality.
- **Pseudo-Mathematics and Financial Charlatanism** — Bailey, Borwein, López de Prado & Zhu (2014). Explains why backtest overfitting can produce impressive but fragile results.
- **Advances in Financial Machine Learning** — López de Prado (2018). Covers purging, embargoing, and combinatorial purged cross-validation.
- **Machine Learning for Asset Managers** — López de Prado (2020). Compact treatment of ML validation, signal research, and portfolio applications.
- **The Statistics of Sharpe Ratios** — Lo (2002). Shows why Sharpe inference and annualization require distributional care.
- **Direct Estimation of Equity Market Impact** — Almgren et al. (2005). Empirical basis for square-root-style market-impact modeling.
- **The Black Swan** — Taleb (2007). Tail-risk and model-risk caution relevant to VaR and backtest extrapolation.
