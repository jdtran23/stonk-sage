---
description: "Market microstructure — order book, bid-ask spread, liquidity, order types (market, limit, stop, IOC, FOK, MOC, OPG), exchanges, ECNs, dark pools, market makers, short selling mechanics, options basics, futures basics, settlement T+1, when microstructure matters"
---
# Market Microstructure — Reference

> How markets actually work at the execution level. Long-term value investors can mostly ignore this. Anyone trading frequently, in illiquid names, or with size needs it. Agents producing trade recommendations should know enough to flag when microstructure matters.

## The Order Book

For any listed security, there is a **limit order book**: a list of all standing buy and sell orders at various prices.

```
ASKS (sells, ordered by price ascending):
  $101.05  500 shares
  $101.00  1,200 shares  ← best ask (lowest sell)
  ────────────────────────  spread
  $100.95  800 shares    ← best bid (highest buy)
  $100.90  1,500 shares
BIDS (buys, ordered by price descending):
```

- **Best bid** = highest price someone is willing to buy at
- **Best ask** (or "offer") = lowest price someone is willing to sell at
- **Spread** = ask − bid (always ≥ 0 in a normal market)
- **Mid** = (bid + ask) / 2
- **Depth** = total shares at each price level
- **Top of book** = the best bid + best ask
- **Level 2** = visible book beyond top of book (multiple price levels)

### NBBO (National Best Bid and Offer)
US equities trade on multiple exchanges. NBBO = best bid across all venues + best ask across all venues. Brokers are required (Reg NMS Rule 611) (FINRA Rule 5310) to route orders to the venue with NBBO.

## Order Types

### Basic Types

| Type | Behavior | Use case |
|------|----------|----------|
| **Market** | Execute immediately at best available price | Need certainty of fill, not price; liquid names only |
| **Limit** | Execute only at specified price or better | Need price control; willing to wait or not fill |
| **Stop (stop-loss)** | Becomes market order when price crosses trigger | Risk management; "sell if it drops below $X" |
| **Stop-limit** | Becomes limit order when trigger hit | More control but may not fill in fast-moving markets |
| **Trailing stop** | Stop that adjusts as price moves favorably | Lock in gains while letting winner run |

### Time-in-Force Modifiers

| TIF | Meaning |
|-----|---------|
| **DAY** (default) | Cancels at end of session if unfilled |
| **GTC** (Good 'til Canceled) | Persists across days (usually max 90 days at most brokers) |
| **IOC** (Immediate or Cancel) | Fill what you can immediately; cancel the rest |
| **FOK** (Fill or Kill) | Fill entire order immediately or cancel entirely |
| **GTD** (Good 'til Date) | Cancels at specified future date |

### Execution Modifiers

| Modifier | Behavior |
|----------|----------|
| **Hidden** | Order not displayed on the book (still executable) |
| **Iceberg** | Display only a slice; replenish from hidden reserve |
| **Post-only** | Reject if order would take liquidity (cross the spread); only post passively |
| **MOC** (Market on Close) | Submitted into closing auction; fills at official closing print |
| **LOC** (Limit on Close) | Like MOC but with limit constraint |
| **OPG** (At the Open) | Submitted to opening auction; fills at official opening print |
| **Pegged** | Order price tracks a reference (e.g., midpoint, primary bid) |

### Why This Matters for Backtesting
Backtests that assume "fill at close" require **MOC** orders, which have size limits and aren't always available. More realistic retail assumption: fill at next day's open or VWAP (see `backtesting-methodology`).

## Liquidity

### Average Daily Volume (ADV)
- The single most important liquidity number
- AAPL: ~$10B+ ADV (extremely liquid)
- Mid-cap: $50-500M ADV (liquid)
- Small-cap: $1-50M ADV (moderate)
- Micro-cap: <$1M ADV (illiquid; slippage dominates)

### Rule of Thumb
You can typically trade up to **5-10% of ADV** without major market impact. Beyond that, expect significant slippage.

### Depth at Touch
- How many shares can you trade at the best bid/ask before moving the price?
- Top-of-book depth varies widely (1,000 shares for liquid names; 100 for illiquid)

### Effective Spread vs Quoted Spread
- **Quoted spread** = ask − bid (what you see)
- **Effective spread** = 2 × |execution price − midpoint| (what you actually paid relative to fair value) (Harris 2003)
- For market orders, effective spread is what matters
- Hidden liquidity (dark pools, iceberg orders) can compress effective spread below quoted spread

### Liquidity Across the Day
- **Open** (9:30 ET) — high volume, wide spreads
- **Midday** (11:00-14:00 ET) — slower volume, tighter spreads
- **Close** (15:30-16:00 ET) — high volume, tight spreads (auctions concentrate liquidity)
- **Pre/post-market** — thin, wide spreads, avoid for non-emergency trading

## Market Makers & the Spread

### What Market Makers Do
- Continuously post bids and offers, profit from the spread
- Provide liquidity in exchange for the spread + rebates from exchanges (maker-taker fee model)
- Subject to obligations (must quote within X% of midpoint, minimum sizes) on regulated exchanges

### Modern Market Making
- Almost entirely electronic / algorithmic since 2010s
- Citadel Securities, Virtu, Jane Street, Susquehanna dominate US equities
- Provide ~50%+ of US equity liquidity
- Internalize retail flow via Payment for Order Flow (PFOF) arrangements with brokers

### PFOF (Payment for Order Flow)
- Retail brokers (Robinhood, Schwab, etc.) route orders to market makers in exchange for payment
- Market makers benefit from "uninformed" retail flow (more profitable to fill than institutional)
- Critics argue this creates a conflict; defenders argue retail gets best execution + free trading
- Banned in some jurisdictions (UK, Canada); **EU phasing out under MiFIR review (2024-2026 transition)**; allowed in US with disclosure

## Exchanges, ECNs, Dark Pools

### US Equity Venues
| Venue | Type | Notes |
|-------|------|-------|
| **NYSE** | Traditional exchange | Designated market makers; opening + closing auctions are central |
| **NASDAQ** | Electronic exchange | Most tech listings; multiple market makers per stock |
| **CBOE** | Electronic exchange | Listed options + equities |
| **IEX** | Electronic exchange | "Speed bump" delays orders 350μs to neutralize HFT |
| **ARCA, BATS, EDGX, EDGA** | Electronic exchanges (now owned by NYSE/CBOE) | Differentiated by fee models (maker-taker, taker-maker) |
| **Dark pools** | Off-exchange ATS (alternative trading systems) | Goldman Sigma X, UBS PIN, etc. **Dark pools (registered ATSs) specifically ~13-15% of US equity volume.** Distinct from total **off-exchange volume ~45%**, which also includes retail-flow internalization at wholesalers (Citadel, Virtu) and single-dealer platforms. |

### Dark Pools
- Match orders without pre-trade transparency (no visible book)
- Trades print to consolidated tape post-execution
- Institutional use case: large block trades without moving the market
- Risk: information asymmetry; better-informed counterparties

## Settlement

### T+1 in the US (since May 2024) (SEC T+1 settlement cycle)
- Trade date + 1 business day for settlement
- Was T+2 from 2017 to 2024
- Implications: faster capital recycling; tighter operational windows; less margin needed; affects FX hedging for foreign investors

### Settlement Conventions Globally
- US equities: T+1
- Most European equities: T+2
- UK Gilts: T+1
- Most government bonds: T+1
- Most corporate bonds: T+2 to T+3
- Mutual funds: usually T+1, NAV calculated at close

## Short Selling Mechanics

### The Process
1. **Locate** — broker confirms shares are available to borrow
2. **Borrow** — broker borrows shares from another customer's margin account (or from an institutional lender)
3. **Sell** — sell the borrowed shares in the market
4. **Buy-to-cover** — at some point, buy shares back to return them

### Costs
- **Borrow fee (rebate rate)** — annualized cost; "easy to borrow" names ~25-50 bps; "hard to borrow" can be 25-100%+
- **Lost dividend** — short owes the dividend to the original lender
- **Margin interest** — short sale proceeds held as margin collateral, may earn interest, but margin maintenance applies

### Risks Unique to Shorts
- **Unlimited loss** — long position max loss is 100% (price → 0); short max loss is unbounded (price → ∞)
- **Recall risk** — borrower (margin account customer) can sell their shares, forcing the short to be covered or re-borrowed elsewhere at higher rate
- **Short squeeze** — rapid short covering forces buying pressure, cascading price up (GME 2021, VW 2008)
- **Regulatory** — naked shorting (selling without locate) is illegal in US; short sale uptick rule (Rule 201) restricts shorting on down-ticks for stocks down 10%+ (Rule 201 — alternative uptick rule)

### Borrow Cost Data
- Sources: S3 Partners, IHS Markit, Interactive Brokers SLB rates
- Heavily-shorted + low-float = expensive borrow + crowded trade = squeeze risk

## Options Basics

### Calls & Puts
- **Call** — right to buy at strike price by expiration (bullish)
- **Put** — right to sell at strike price by expiration (bearish or protective)
- **Long** = bought the option (paid premium)
- **Short** = sold/wrote the option (received premium, took obligation)

### Value Decomposition
- **Intrinsic value** = max(0, S − K) for calls; max(0, K − S) for puts
- **Time value** = option price − intrinsic value
- At expiration, options are worth only intrinsic value
- Time value decays as expiration approaches (theta decay)

### Greeks
| Greek | Measures |
|-------|----------|
| **Delta (Δ)** | Sensitivity to underlying price (∂V/∂S); 0 to 1 for calls, -1 to 0 for puts |
| **Gamma (Γ)** | Rate of change of delta (∂²V/∂S²) |
| **Theta (Θ)** | Sensitivity to time decay (∂V/∂t); typically negative for long options |
| **Vega (ν)** | Sensitivity to implied volatility (∂V/∂σ) |
| **Rho (ρ)** | Sensitivity to interest rate (∂V/∂r) |

### Implied Volatility (IV)
- The market's forecast of future volatility, implied by current option prices via Black-Scholes
- IV ≠ realized volatility; trading IV vs RV is a strategy class
- **VIX** = 30-day implied vol on S&P 500 options ("fear index")
- High IV after a crash → options expensive → premium-selling strategies more attractive (but high tail risk)

### Common Strategies (without full P&L diagrams)
- **Long call** — leveraged bull bet, capped loss = premium
- **Long put** — leveraged bear bet OR portfolio hedge
- **Covered call** — own stock + sell call against it; income generation; caps upside
- **Cash-secured put** — sell put with cash collateral; "get paid to wait" for entry price; obligation to buy if assigned
- **Vertical spread** (call or put) — buy one strike, sell another; defined risk, capped reward
- **Iron condor** — sell call spread + put spread; profits if underlying stays in range; popular for income
- **Straddle / Strangle** — long call + long put; profits from large moves either direction; loses to time decay if quiet

### Options Caveats
- Bid-ask spreads on options are wider than equities (often 1-10% of price)
- Liquidity concentrates in near-the-money, near-expiration strikes
- Assignment risk on short options before expiration (American-style)
- Per OCC data: only **~7-10% of options are exercised**; ~20-40% expire worthless; **~55-71% are closed before expiration** via offsetting trades. The often-cited "90% expire worthless" folklore is wrong — most positions are actively closed, not held to expiration. Worthless-expiration is real for far-OTM options but not the population overall. Sellers of options have positive expectancy on average but with tail risk. (OCC public statistics; see also Options Industry Council education materials.)

## Futures Basics

- Standardized contracts traded on exchanges (CME, ICE, CBOT) (Commodity Exchange Act; CFTC)
- Underlying: indices (ES = S&P 500), commodities (CL = crude, GC = gold), rates (ZN = 10-yr Treasury), currencies (6E = EUR)
- Leverage embedded (margin << notional; 5-10% typical initial margin)
- Cash-settled (most index futures) or physically deliverable (most commodities — though most positions closed before delivery)
- Marked-to-market daily (gains/losses settle nightly)
- No PDT (pattern day trader) rule restrictions
- Tax treatment in US: 60% long-term / 40% short-term regardless of holding period (Section 1256) (IRC §1256)

## When Microstructure Matters

### Matters a Lot
- Day trading / swing trading
- Small-cap stocks (illiquid, wide spreads)
- Options trading (spreads + Greeks)
- Trading >1% of ADV
- Short positions (locate + borrow cost)
- HFT / market-making strategies
- Period of high market stress (spreads widen, depth evaporates)

### Doesn't Much Matter
- Long-term buy-and-hold of large-cap stocks
- ETF positions in major indices
- Automatic monthly contributions
- Tax-loss harvesting (slippage tiny compared to tax benefit)
- DCA strategies

## Operational Checklist
When an agent recommends a trade in a stock, it should consider:
1. **ADV check** — is the position size > 5% of ADV? Flag execution risk
2. **Spread check** — for small caps, what's typical spread? Wide spreads = execution drag
3. **Borrow cost** (if short) — what's the rebate rate? Hard-to-borrow names are expensive to hold
4. **Order type** — recommend market only for liquid names; limit for everything else
5. **Time of day** — for large orders, avoid open + close volatility unless using auctions explicitly
6. **Settlement implications** — for high-frequency rebalancing, account for T+1 cash availability
7. **Options-specific** — IV regime (high/low), spread width, time to expiration, assignment risk
8. **PDT compliance** (for under-$25K accounts) — pattern day trader rule limits day trades

If the strategy depends on tight microstructure assumptions in illiquid names, flag the risk explicitly. Real-world execution often invalidates pretty backtest curves.

## Further Reading

- **Market Microstructure Theory** — Maureen O'Hara (1995). Foundational model of trading, information, inventory, and price formation.
- **Trading and Exchanges: Market Microstructure for Practitioners** — Larry Harris (2003). Practitioner guide to order types, liquidity, trading costs, and market design.
- **Empirical Market Microstructure** — Joel Hasbrouck (2007). Data-driven measurement of spreads, price impact, and intraday market behavior.
- **Market Liquidity: Theory, Evidence, and Policy** — Foucault, Pagano & Röell (2013). Liquidity theory and policy implications across market structures.
- **High-Frequency Trading** — Irene Aldridge (2013). Overview of electronic trading, latency, and HFT strategy mechanics.
- **Regulation NMS** — U.S. Securities and Exchange Commission (2005). U.S. equity-market rules including the Order Protection Rule.
- **FINRA Rule 5310: Best Execution and Interpositioning** — Financial Industry Regulatory Authority (2024). Broker-dealer best-execution obligations.
- **Rule 201 Short Sale Price Test Circuit Breaker** — U.S. Securities and Exchange Commission (2010). Alternative uptick rule for covered securities after sharp declines.
- **Commodity Exchange Act** — U.S. Congress (1936). Primary statutory framework for U.S. futures and commodity derivatives markets.
- **Internal Revenue Code §1256** — U.S. Congress (1981). Mark-to-market and 60/40 tax treatment for Section 1256 contracts.
