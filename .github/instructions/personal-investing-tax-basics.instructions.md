---
description: "Personal investing tax basics — short-term vs long-term capital gains, qualified vs ordinary dividends, wash-sale rule, tax-loss harvesting, options/futures Section 1256, taxable vs IRA/401k accounts, account-type-aware recommendations, US-focused operational reference"
---
# Personal Investing Tax Basics

> Operational reference for an agent reasoning about taxes in personal investing context. **This is educational reference, not tax advice — agents should always defer specific personal tax questions to a licensed CPA or tax attorney.** Scope: US individual investor tax rules as of 2026. International / corporate / estate / state-specific tax is out of scope.

## Why Tax Matters

For a hobbyist investor, **taxes can dominate realized returns**. A strategy with 12% pre-tax return can net out to ~6-7% after-tax for a high-bracket investor with high turnover, while a buy-and-hold strategy with 10% pre-tax can net out to ~9% after-tax. Strategy comparisons that ignore taxes are misleading.

The agent must distinguish:
- **Pre-tax vs after-tax returns** when comparing strategies
- **Account types** that change tax treatment (taxable / IRA / Roth IRA / 401(k))
- **Holding periods** that determine cap-gain rate
- **Income vs gain** treatment for dividends, options, futures
- **Wash sales** that disallow losses

## Capital Gains: Short-Term vs Long-Term

### Short-Term Capital Gain (STCG)
- Realized on positions held **≤ 1 year** (IRC §1222)
- Taxed at **ordinary income rates** (10% / 12% / 22% / 24% / 32% / 35% / 37% federal in 2026, plus state)
- High-frequency or high-turnover strategies often realize gains as STCG

### Long-Term Capital Gain (LTCG)
- Realized on positions held **more than 1 year** (IRC §1222; must be strictly more than 365 days — the practical rule is "sell on or after the same calendar date + 1 day, one year later"; the "day 366" framing breaks around leap years and Feb 29 purchases)
- Federal rates: **0% / 15% / 20%** based on income bracket (IRC §1(h))
- Plus 3.8% NIIT (Net Investment Income Tax) for high-income filers (IRC §1411 — NIIT)
- Plus state tax (varies; CA up to 13.3% on cap gains, effective ~14.4% on wages >$1M; NY up to 10.9%; WA 7% on LTCG above ~$285K threshold since 2022; FL/TX/NV/SD/WY/TN/AK/NH 0%)

### Why It Matters for Agents
- A position with 30% gain held 11 months → sell now = STCG at 32% federal = ~9.6% tax drag
- Same position held 1 more month → LTCG at 15% federal = ~4.5% tax drag
- **Delaying a sale by 1 month can double the after-tax return.** Agents should flag positions near the 1-year mark before recommending sells.

## Dividends

### Qualified Dividends
- Most US large-cap stock dividends qualify (must meet holding period: >60 days during the 121-day window around ex-dividend date; IRC §1(h)(11))
- Taxed at **LTCG rates** (0% / 15% / 20%) — same preferential treatment as long-term cap gains (IRC §1(h)(11))
- Most S&P 500 dividends are qualified

### Ordinary (Non-Qualified) Dividends
- Most REIT distributions, BDC distributions, MLP distributions (partially)
- Some foreign stock dividends
- Taxed at **ordinary income rates** (up to 37%)
- A 4% REIT yield at 37% bracket = 2.5% net; same 4% qualified dividend = 3.4% net

### Implications for Recommendations
- REITs in taxable accounts have meaningful tax drag vs in IRAs
- High-yield "income" portfolios should consider account placement
- Foreign withholding tax (typically 15%) on dividends may be partially offset by foreign tax credit

## The Wash Sale Rule

**Definition:** If you sell a security at a loss and buy a "substantially identical" security within **30 days before or after** (61-day window), the loss is **disallowed** for current-year tax purposes. The disallowed loss is added to the cost basis of the replacement security (IRC §1091).

### What Counts as "Substantially Identical"
- Same ticker = always substantially identical
- Same company different share class (e.g., GOOG vs GOOGL) = **legally gray** — IRS has never ruled; conservative practice treats as identical, but no definitive guidance
- Different funds tracking same index (VTI vs ITOT) = **legally gray**; IRS has not definitively ruled
- Different sector ETFs = generally NOT substantially identical
- **Selling stock at a loss and buying a call (or deep-in-the-money option) on the same stock within the 61-day window IS a wash sale** (IRC §1091; Rev. Rul. 56-406). The reverse direction (option-to-stock) depends on the option's character; ATM/OTM options are less clearly identical to the underlying. The stock→option direction is the more common operational trap.

### Operational Implications
- An agent recommending "sell XYZ at a loss, buy similar XYZ-class stock" needs to flag wash-sale risk
- **Tax-loss harvesting strategies must use replacement securities that aren't substantially identical** (e.g., sell VTI loss, buy ITOT — gray area but commonly done; safer: sell VTI, buy VEA or VOO)
- Wash sales across accounts count too — selling at a loss in a taxable account and buying back in an IRA triggers wash sale (the loss is permanently disallowed in this case, not deferred; Rev. Rul. 2008-5)

## Tax-Loss Harvesting (TLH)

**Strategy:** Realize losses to offset gains (or up to $3,000/year of ordinary income; IRC §1211(b)), while maintaining market exposure via similar (but not identical) replacement.

### Mechanics
1. Identify positions with unrealized losses
2. Sell to realize the loss
3. Buy a non-substantially-identical replacement to maintain exposure
4. After 31 days (post wash-sale window), can rotate back if desired

### Caveats
- Doesn't eliminate tax — it **defers** it (lower cost basis on replacement = larger gain when eventually sold)
- Only beneficial if future tax rate ≤ current tax rate (TLH at 37% now, sell future LTCG at 15% = net win; opposite scenarios = wash)
- $3,000 annual cap on ordinary-income offset; excess carries forward indefinitely (IRC §1211(b); IRC §1212(b))
- Operational complexity (tracking lots, replacements, wash-sale windows) is non-trivial

## Account Types — Account-Aware Recommendations

| Account Type | Contributions | Growth | Withdrawals | Best For |
|--------------|---------------|--------|-------------|----------|
| **Taxable** | After-tax | Taxed annually (dividends, realized gains) | No tax on already-taxed principal | Flexibility; high-conviction long-term holds; tax-loss harvesting |
| **Traditional IRA / 401(k)** | Pre-tax (deductible) | Tax-deferred | Taxed as ordinary income | Bonds, REITs, high-turnover; defers tax to (hopefully) lower-bracket retirement |
| **Roth IRA / Roth 401(k)** | After-tax | Tax-free growth | Tax-free withdrawals (rules apply) | Highest-expected-return assets; long-holding-period equities; tax diversification |
| **HSA** | Pre-tax | Tax-free growth | Tax-free for qualified medical | "Triple-tax-advantaged"; under-used for long-term investing |
| **529 Plan** | After-tax (often state-deductible) | Tax-free growth | Tax-free for qualified education | Education savings only |

### Account-Placement Rules of Thumb (Asset Location)
- **Tax-inefficient assets in tax-advantaged accounts:** REITs, high-yield bonds, actively-managed funds with high turnover, MLPs (also avoid UBTI issues in IRAs)
- **Tax-efficient assets in taxable accounts:** broad-market index ETFs (low turnover), individual stocks held long-term, qualified dividend payers
- **Highest-expected-return assets in Roth:** maximizes tax-free growth where it matters most
- This is a long-term optimization; for short-term tactical positions, account choice may matter less

### Operational Implication for Agents
**Always ask account type before tax-sensitive recommendations.** Selling at a gain in an IRA has zero current tax impact; the same sale in a taxable account triggers cap gains. The "best" recommendation differs by account.

## Options and Futures Special Treatment

### Options on Equities
- Generally taxed as **short-term cap gains** if held ≤ 1 year (which is almost always — most options have <1 year expirations)
- Selling a covered call against a long-stock position: if assigned, treated as a sale of the underlying at the strike + premium received
- Closed positions (bought-to-close) realize gain/loss as STCG
- Cash-secured put assigned: premium received reduces cost basis of acquired shares

### Section 1256 Contracts
Special tax treatment for: **broad-based index options (SPX, NDX, RUT), regulated futures (ES, NQ, ZN, CL, GC, etc.), futures options** (IRC §1256).

- **60% long-term / 40% short-term** regardless of holding period (IRC §1256(a)(3))
- **Mark-to-market at year-end** — open positions count gain/loss as if sold on Dec 31 (IRC §1256(a)(1))
- More tax-efficient than equity options for high-bracket frequent traders
- Worth knowing: SPX options have meaningfully better tax treatment than equivalent SPY options

### Wash Sale Note
- Standard wash-sale rule does NOT apply to Section 1256 contracts (they're mark-to-market; IRC §1256)
- Does apply to single-stock options (IRC §1091)

## Special Situations

### Spinoffs
- Generally **tax-free at the spin date** (IRC §355) — cost basis is allocated between parent and spinco based on relative FMV
- Selling the spin shortly after = tax event (use allocated cost basis)
- Some spins are **taxable** — read the Form 8937 (broker should provide)

### Mergers (Stock-for-Stock)
- Often **tax-free** if structured properly (Type A/B/C reorganization; IRC §368)
- Cost basis carries over to acquirer shares
- Cash boot (cash portion of consideration) is taxable

### Mergers (Cash)
- **Taxable event** — gain realized on the cash received
- Treated as a sale of target shares at the cash amount

### Stock Splits and Dividends
- Stock splits: no tax event; cost basis adjusts proportionally
- Stock dividends: usually no tax event; cost basis spreads across new + original
- Dividend reinvestment (DRIP): each reinvested dividend is taxable as a dividend AND creates a new cost-basis lot

## State Tax (Briefly)
- State cap gains tax varies dramatically: 0% wage **and** cap gains (FL, TX, NV, SD, WY, TN, AK, NH); **WA — 0% wage but 7% LTCG above ~$285K threshold (since 2022)**; ~5-7% (most middle); 10-13% (NY, NJ, OR); CA 13.3% headline cap-gains, ~14.4% effective on wages >$1M
- States generally follow federal classification (LTCG vs STCG) but most don't have preferential rates — gains taxed as ordinary state income
- State of residence matters; for high-net-worth retirees, state-shifting is a real planning tool

## NIIT (Net Investment Income Tax)
- 3.8% additional tax on investment income (interest, dividends, cap gains, rental income; IRC §1411 — NIIT)
- Applies to single filers with AGI > $200K, married filing jointly > $250K (**not** inflation-adjusted; more taxpayers pulled in each year; IRC §1411)
- **Applied to the lesser of net investment income or AGI-over-threshold** — for filers near the threshold this is a partial drag, not full (IRC §1411(a))
- On top of LTCG/dividend rates — so 20% LTCG bracket effectively pays 23.8% federal

## SECURE 2.0 Updates Relevant for 2026
- **RMD age is 73** (rising to 75 in 2033; SECURE 2.0 Act, Pub. L. 117-328) — relevant for IRA/401k withdrawal planning
- **Mandatory Roth catch-up contributions** for participants with prior-year wages > $145K start in 2026 — catch-up amounts must go to Roth, not pre-tax (SECURE 2.0 Act, Pub. L. 117-328; IRS Notice 2023-62 transition relief)
- **529-to-Roth IRA rollover** allowed (up to $35K lifetime; 529 account must be 15+ years old; subject to annual Roth contribution limit; SECURE 2.0 Act, Pub. L. 117-328)
- Annual contribution limits change each year — verify against IRS for the current year (illustrative 2026: 401(k) ~$24K, IRA ~$7.5K, HSA family ~$8.7K)

## Tax Reporting Forms (US)

| Form | Issued by | Reports |
|------|-----------|---------|
| **1099-B** | Broker | Sales / closing transactions, cost basis, gains/losses |
| **1099-DIV** | Broker / issuer | Dividends (ordinary and qualified), cap gain distributions |
| **1099-INT** | Broker / issuer | Interest income |
| **K-1** | Partnerships, MLPs, BDCs | Distributions, sometimes ordinary income / UBTI |
| **Form 8949** | Taxpayer | Detail of cap gains/losses (feeds Schedule D) |
| **Schedule D** | Taxpayer | Summary of cap gains/losses |
| **Form 8937** | Issuer | Cost basis allocations for corporate actions (spinoffs, mergers) |

K-1s are notoriously late (often March-April or later) and can complicate filing. Agents recommending MLPs / partnerships should flag this operational reality.

## Common Tax Mistakes (Agent-Catchable)

- Selling at a loss and rebuying within 30 days (wash sale → loss disallowed)
- Selling before the 1-year holding-period mark (loses LTCG treatment by days)
- Recommending high-turnover strategies in taxable accounts without flagging tax drag
- Recommending REITs in taxable accounts when they belong in IRAs
- Ignoring state tax when computing after-tax returns
- Suggesting MLPs in IRAs without warning about UBTI (Unrelated Business Taxable Income)
- Failing to use specific-lot identification when selling partial positions (HIFO / specific ID minimizes tax in most cases; Treas. Reg. §1.1012-1(c))
- Forgetting that dividend reinvestment creates cost-basis tracking complexity

## Operational Checklist

When an agent recommends a sell or rebalance, automatically check:
1. **Account type** — taxable or tax-advantaged? Materially changes the recommendation.
2. **Holding period** — is the position close to the 1-year LTCG threshold? Days vs months matter.
3. **Wash sale risk** — is the user likely to buy back the same/similar security within 30 days?
4. **Lot identification** — partial sale? Recommend specific lots (typically HIFO — highest cost first) to minimize gain (Treas. Reg. §1.1012-1(c)).
5. **Year-end timing** — December sales can be planned around tax loss/gain harvesting; January sales push tax to following year.
6. **NIIT bracket** — high-income filers face an additional 3.8% drag.
7. **State implications** — flag if user is in a high state-tax jurisdiction.
8. **Corporate action artifacts** — if the position came from a spinoff/merger, cost basis may be more complex than the broker shows.

If account type is unknown, **ask** before recommending tax-sensitive actions. The recommendation can be materially wrong without that context.

## Out of Scope (Refer to a CPA)

- International tax (FATCA, FBAR, foreign tax credits beyond basics)
- Estate / gift tax planning
- Trust taxation
- Partnership tax intricacies (K-1 deep analysis, UBTI mechanics, basis tracking)
- State-specific elections (NJ S-Corp election, CA mark-to-market for traders)
- Sec 1244 small business stock losses
- Qualified Opportunity Zone investments
- Wash-sale rules across spouses' accounts
- §475(f) trader-status election

These require licensed CPA / tax attorney input. Agents should refuse to recommend in these areas, surface the question, and defer.

## Further Reading

- **Federal Income Taxation** — Freeland, Lathrope, Lind, and Stephens (current edition). Casebook foundation for individual income-tax concepts and statutory interpretation.
- **Publication 550: Investment Income and Expenses** — Internal Revenue Service (current tax year). Primary IRS operational guide for dividends, capital gains, wash sales, and investment expenses.
- **Publication 590-A: Contributions to Individual Retirement Arrangements** — Internal Revenue Service (current tax year). IRA contribution rules, limits, and eligibility basics.
- **Publication 590-B: Distributions from Individual Retirement Arrangements** — Internal Revenue Service (current tax year). IRA distribution, RMD, and beneficiary-distribution reference.
- **Publication 17: Your Federal Income Tax** — Internal Revenue Service (current tax year). Broad individual-tax baseline for non-specialist readers.
- **The Bogleheads' Guide to Investing** — Taylor Larimore, Mel Lindauer, and Michael LeBoeuf (2006). Practical personal-finance framing for tax-efficient long-term investing.
- **J.K. Lasser's Your Income Tax** — J.K. Lasser Institute (annual). Practitioner-friendly annual reference for individual tax rules and reporting mechanics.
- **Investment Valuation** — Aswath Damodaran (current edition). Useful for thinking about tax-adjusted returns and after-tax valuation impacts.
- **SECURE 2.0 Act Implementation Guidance** — Internal Revenue Service and Treasury (current releases). Tracks evolving implementation of RMD, Roth catch-up, and 529-to-Roth provisions.
