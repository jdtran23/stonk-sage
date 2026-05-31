---
description: "SEC filings reference — 10-K, 10-Q, 8-K, Form 4, S-1, DEF 14A proxy, 13F, 13D, 13G, NT-10-K; EDGAR access via edgartools; required sections, what to look for, red flags, insider transactions, institutional ownership, material events"
---
# SEC Filings — Reference for Stock Research

> The most reliable primary source for US-listed companies. Filings are PIT-safe by filing date and immutable post-acceptance. Every claim in equity research should ideally trace back to a filing. This file describes what each filing type contains and how to mine it.

## Filing Type Quick Reference

| Filing | Filed when | Frequency | What it contains |
|--------|-----------|-----------|------------------|
| **10-K** | Within 60-90 days of fiscal year end (Form 10-K General Instruction A.(2); Exchange Act Rule 12b-2) | Annual | Full audited financials + business description + risk factors + MD&A |
| **10-Q** | Within 40-45 days of quarter end (Form 10-Q General Instruction A.1) | Quarterly (not Q4 — that's the 10-K) | Unaudited quarterly financials + MD&A update |
| **8-K** | Within 4 business days of trigger event (Form 8-K General Instruction B.1) | Event-driven | Material corporate events (see below) |
| **Form 4** | Within 2 business days of insider transaction (Exchange Act §16(a); Rule 16a-3(g)) | Event-driven | Insider buys/sells (officers, directors, 10%+ holders) |
| **S-1** | Before IPO | Once per IPO | Full company disclosure for IPO registration |
| **S-4** | For M&A using stock | Per deal | Acquisition disclosure |
| **DEF 14A** | Before annual meeting | Annual | Proxy statement — exec comp, board, related-party, shareholder proposals |
| **13F** | Within 45 days of quarter end (Exchange Act §13(f); Rule 13f-1) | Quarterly | Institutional holdings (managers with >$100M AUM) |
| **SC 13D** | Within **5 business days** of crossing 5% ownership (SEC Final Rule 33-11253, effective Feb 5, 2024; was 10 calendar days); amendments due within 2 business days (SEC Final Rule 33-11253) | Event-driven | Active large holder (intent matters) |
| **SC 13G** | QIIs file within 45 days after **calendar quarter-end** (SEC Final Rule 33-11253, effective Feb 5, 2024; was annual); within 5 business days of crossing 10% (SEC Final Rule 33-11253). Passive non-QII filers: also quarterly under amended Rule 13d-1 (SEC Final Rule 33-11253) | Quarterly (QIIs and passive) / Annual (some legacy paths) | Passive large holder (no intent to influence) |
| **NT-10-K / NT-10-Q** | When a filing will be late | As needed | Notification of late filing — **major red flag** |
| **20-F / 6-K** | Foreign private issuers | Annual / event | Equivalent of 10-K / 8-K for non-US companies |
| **N-CSR / N-PORT** | Mutual funds & ETFs | Quarterly/semi | Fund holdings |

## 10-K Structure (Memorize this)

The 10-K has 15 standardized Items in 4 Parts (Form 10-K; Regulation S-K). Most useful sections in **bold**:

**Part I**
- **Item 1: Business** — what the company does. The first place to read.
- **Item 1A: Risk Factors** — required disclosures of material risks. Skim for new/changed risks YoY.
- Item 1B: Unresolved SEC Staff Comments — if anything here, dig in.
- Item 2: Properties — real estate / physical facilities.
- Item 3: Legal Proceedings — material lawsuits.
- Item 4: Mine Safety Disclosures (mostly N/A).

**Part II**
- Item 5: Market for Registrant's Common Equity — share repurchase history table.
- Item 6: [Reserved/Removed]
- **Item 7: MD&A (Management's Discussion & Analysis)** — management's narrative explanation of results. The most analytically valuable text in the document.
- Item 7A: Quantitative and Qualitative Disclosures About Market Risk — FX, rate, commodity exposures.
- **Item 8: Financial Statements and Supplementary Data** — the audited statements + footnotes. Footnotes contain a huge amount of buried truth.
- Item 9: Changes in and Disagreements With Accountants — auditor changes are a red flag.
- **Item 9A: Controls and Procedures** — material weaknesses in internal controls are a major red flag.
- Item 9B: Other Information.

**Part III** (often incorporates by reference to the proxy)
- Item 10-14: Directors, executive officers, exec comp, security ownership, related transactions, principal accountant fees.

**Part IV**
- **Item 15: Exhibits & Financial Statement Schedules** — contracts, agreements, subsidiary lists. Material contracts (key customers, debt agreements, JV terms) live here as exhibits.

### Recommended Reading Order for a 10-K
1. **Item 1** (Business) — what does it do?
2. **Item 1A** (Risk Factors) — compare to prior year; flag new/removed/changed risks
3. **Item 8 footnotes** (often Note 1: Significant Accounting Policies, Note 2: Revenue, Segment Note) — what the accounting actually means
4. **Item 7** (MD&A) — management's explanation of YoY changes
5. **Item 8 statements** — the numbers themselves
6. **Item 7A** — non-operating risks
7. **Exhibits** — for any material contract mentioned in Risk Factors or MD&A

## 8-K Triggers (Items)

8-K is filed for "material" events. The Item number tells you what kind:

| Item | Triggers |
|------|----------|
| 1.01 | Material definitive agreement |
| 1.02 | Termination of material definitive agreement |
| 1.03 | Bankruptcy or receivership |
| 2.01 | Completion of acquisition/disposition |
| 2.02 | **Results of operations** — earnings press releases |
| 2.03 | Material direct financial obligation |
| 2.04 | Triggering events that accelerate financial obligation |
| 2.06 | Material impairments |
| 3.01 | Notice of delisting / failure to satisfy listing rules |
| 4.01 | Changes in registrant's certifying accountant |
| 4.02 | Non-reliance on previously issued financials — **restatement** — major red flag |
| 5.02 | **Departure or appointment of directors/officers** — CEO/CFO changes |
| 5.07 | Submission of matters to shareholder vote |
| 7.01 | Regulation FD disclosure (general material info) |
| 8.01 | Other events (catch-all) |

Set up alerts for 4.02, 5.02, 1.03 on any owned stock.

## Form 4 — Insider Transactions

Filed within 2 business days of an officer, director, or 10%+ shareholder transacting in company stock (Exchange Act §16(a); Rule 16a-3(g)).

### Transaction Codes (most common)
- **P** — Open-market purchase (the most bullish signal — they're buying with their own money)
- **S** — Open-market sale (often noise — could be diversification, taxes, lifestyle)
- **A** — Grant/award (usually compensation; not a market signal)
- **M** — Exercise/conversion of derivative (usually combined with S)
- **F** — Payment of exercise price or tax via withholding
- **G** — Gift (often charitable — not a market signal)
- **J** — Other

### How to Interpret
- **Cluster of unusual P transactions across multiple insiders** = high-conviction bullish signal
- **CFO selling >50% of position over 30 days** = worth investigating
- **CEO buying in size at depressed price** = high-conviction bullish (Buffett: "There's only one reason to buy — you think the price is going up")
- **Programmatic 10b5-1 sales** — pre-scheduled, usually for diversification; less signal
- Heavy **A** grants near year-end = ordinary comp, ignore as market signal

## DEF 14A — Proxy Statement

Filed annually before the shareholder meeting. Contains:

- **Executive compensation tables** — Summary Comp Table, Grants of Plan-Based Awards, Outstanding Equity Awards, Option Exercises, Pension Benefits, Nonqualified Deferred Comp. Compute total comp = salary + bonus + stock + options + perks.
- **CEO Pay Ratio** — required disclosure of CEO comp vs median worker (Regulation S-K Item 402(u))
- **Compensation Discussion & Analysis (CD&A)** — what metrics drive bonuses (the most important text in the proxy)
- **Related Person Transactions** — payments to directors, family members, affiliates. Red flag if substantial.
- **Director independence** — how many directors are truly independent
- **Audit committee report** — auditor relationship
- **Shareholder proposals** — what activists are pushing
- **Board structure** — staggered vs annually elected, classified/declassified

CD&A tells you what management will optimize for. If bonus is tied to "Adjusted EBITDA," expect aggressive non-GAAP add-backs.

## 13F — Institutional Holdings

Filed quarterly by managers with >$100M AUM (Exchange Act §13(f); Rule 13f-1). Discloses long equity holdings (NOT shorts, NOT options, NOT cash, NOT international).

### How to Use
- Track positioning changes by sophisticated investors (Berkshire, Pershing Square, Greenlight, Tiger Cubs, etc.)
- **Caveat 1:** 45-day lag — positions are 45+ days stale by publication
- **Caveat 2:** Only longs — shorts could offset
- **Caveat 3:** Sub-$100M managers excluded
- **Caveat 4:** Survivorship bias on lists like "best 13F managers" — losers vanish

Good for thesis generation, terrible for trade timing.

## SC 13D vs SC 13G

Both filed when crossing 5% ownership. Difference is intent + deadline (deadlines updated by SEC amendments effective Feb 5, 2024; SEC Final Rule 33-11253):

- **13D** — Active. Holder may try to influence control (proxy fights, board representation, M&A). Item 4 ("Purpose of Transaction") is the key section.
  - **Filing deadline: 5 business days** after crossing 5% (SEC Final Rule 33-11253, effective Feb 5, 2024; was 10 calendar days pre-Feb 2024)
  - **Amendment deadline: 2 business days** after a material change (SEC Final Rule 33-11253; was "promptly")
- **13G** — Passive. Filed by ETFs, index funds, institutions with no intent to influence.
  - **Filing cadence: 45 days after calendar quarter-end** (SEC Final Rule 33-11253; was annually after year-end)
  - **5 business days** after crossing 10% (SEC Final Rule 33-11253; for QIIs and exempt investors)

A 13D filing is a much bigger signal than 13G. Watch for activists (Elliott, Pershing Square, Starboard, Trian) filing 13D — often catalyst.

## S-1 (IPO Registration)

For new IPOs. Contains:
- Full company history + business description
- 2-3 years of audited financials
- Use of proceeds
- Risk factors (often the most candid risk section a company ever publishes)
- Underwriting agreement (banks, lockup periods)
- Capitalization table pre/post IPO

Lockup expiration (usually 180 days post-IPO) is often a catalyst for selling pressure.

## Red Flags in Filings

| Red Flag | Why it matters |
|----------|----------------|
| **NT-10-K/Q filing** (late filing notification) | Auditor disagreement, internal controls issue, fraud investigation possible |
| **Item 4.02 8-K** (non-reliance on prior financials) | Restatement coming |
| **Item 4.01 8-K** (auditor change) | Especially if mid-cycle |
| **Material weakness disclosed in Item 9A** | Internal controls broken |
| **Going concern qualification** in audit report | Auditor doubts the company can continue |
| **Frequent accounting policy changes** | Earnings management likely |
| **Risk Factors section grows materially YoY** | New material risks management was forced to disclose |
| **Auditor's letter has any qualified opinion** | Anything but a clean opinion is a yellow flag minimum |
| **Related-party transactions growing as % of revenue** | Self-dealing risk |
| **Heavy insider sales (Form 4) before a quarter** | They may know something |
| **Departure of CFO without clear successor** | Often precedes earnings problems |
| **Frequent 8-K Item 5.02** (executive departures) | Org chaos |
| **Stock-based comp >10-15% of revenue** | Real cost being hidden by non-GAAP |
| **Goodwill > total equity** | One impairment away from technical insolvency |

## Accessing Filings (Operational)

### EDGAR
- Free, no API key required
- URL pattern: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={CIK}&type={form-type}`
- Full-text search at `https://efts.sec.gov/LATEST/search-index?q="search+term"`

### edgartools (Python — recommended)
```python
from edgar import Company, set_identity
set_identity("Your Name your.email@example.com")  # required per SEC fair access rules (SEC EDGAR Fair Access policy)

co = Company("AAPL")
latest_10k = co.latest("10-K")
financials = latest_10k.financials  # parsed XBRL
text = latest_10k.text()  # full filing text
```

PIT-safe: filings are immutable once filed. Use `filed_date` (not period date) for as-of comparisons.

### EDGAR Full-Text Search
For searching across filings (e.g., every 10-K mentioning "supply chain disruption" or a specific customer):
`https://efts.sec.gov/LATEST/search-index?q=%22term%22&dateRange=custom&startdt=2024-01-01&enddt=2024-12-31`

## XBRL — Structured Financial Data

Financial statements in 10-K/Q are tagged with XBRL (eXtensible Business Reporting Language), allowing programmatic extraction of standardized line items. Use this rather than scraping the HTML/PDF.

`edgartools` parses XBRL automatically. Standardized concepts (e.g., `us-gaap:Revenues`, `us-gaap:NetIncomeLoss`) make cross-company comparison possible — but **not every concept is standardized**; many companies use custom extensions for important items.

## Operational Checklist for Reading a 10-K
1. Check filing date — is this the most recent annual? (`edgartools` `Company("X").latest("10-K")`)
2. Read Item 1 (Business)
3. Compare Item 1A (Risk Factors) to prior year — diff for added/removed/changed risks
4. Read Item 7 (MD&A) for management's narrative
5. Pull Item 8 financial statements (XBRL preferred for comparison)
6. Read Note 1 (Significant Accounting Policies) and the Segment footnote
7. Check Item 9A for any internal-controls issue
8. Scan exhibits for new material contracts (Item 15)
9. Read the latest DEF 14A for CD&A and related-party transactions
10. Pull last 4 quarters of Form 4 — any unusual insider activity?

If an agent's response cites a financial fact, it should cite **which filing, which item or note, and which fiscal period**. Vague "company filings say…" is not enough.

## Further Reading

- **EDGAR Filer Manual** — U.S. Securities and Exchange Commission (current edition). Primary operational manual for EDGAR submissions, identifiers, filing mechanics, and access expectations.
- **Modernization of Beneficial Ownership Reporting** — U.S. Securities and Exchange Commission Final Rule 33-11253 (2023). Primary authority for amended 13D/13G deadlines and cadence.
- **Securities Regulation** — Louis Loss, Joel Seligman, and Troy Paredes (current edition). Comprehensive treatise on the federal securities disclosure framework.
- **Securities Regulation in a Nutshell** — Thomas Lee Hazen (current edition). Concise practitioner reference for Exchange Act reporting and filing rules.
- **SEC Investor Publications** — SEC Office of Investor Education and Advocacy (current releases). Plain-English guides on company filings, insider transactions, and market structure.
- **Negotiated Acquisitions of Companies, Subsidiaries and Divisions** — Lou R. Kling, Eileen T. Nugent, and Brandon A. Van Dyke (current edition). Useful context for S-4s, merger proxies, and acquisition disclosure.
- **Public Company Deskbook** — Practising Law Institute (current edition). Operational reference for periodic reporting, current reporting, and disclosure controls.
