# Onboarding — Alpaca MCP Server

> Get a new engineer from zero to a working **Alpaca MCP** connection inside their editor. This covers the external API + local scaffolding that `stonk-sage` relies on for live/market data and (paper) trading. For the core Python project setup (`uv sync`, `EDGAR_IDENTITY`, running `/analyze`), see the [README](../README.md#setup) first — this doc layers the Alpaca MCP on top.

> **Not financial advice.** The MCP can place real orders if pointed at a live account. Default everything to **paper trading** until you know exactly what you're doing.

---

## What you're installing

The [Alpaca MCP Server](https://docs.alpaca.markets/us/docs/alpaca-mcp-server) is a Model Context Protocol server that exposes Alpaca's Trading + Market Data APIs as tools your AI assistant can call. Once connected you can ask, in plain language, for account balances, quotes, bars, option chains, screeners, news, and order placement — **60+ tools** (62 observed on a paper account; Alpaca documents 65 across toolsets).

It runs locally over **stdio**, launched on demand by your MCP client via `uvx`. There is no separate service to host.

---

## Prerequisites

| Requirement | Why | Link |
|---|---|---|
| **Python 3.10+** | Runtime for the server (this repo pins 3.12) | [python.org/downloads](https://www.python.org/downloads/) |
| **uv / uvx** | Launches the server (`uvx alpaca-mcp-server`) | [uv install guide](https://docs.astral.sh/uv/getting-started/installation/) |
| **Alpaca account + API keys** | Auth; a free **paper** account is enough | [Paper dashboard](https://app.alpaca.markets/paper/dashboard/overview) |
| **An MCP client** | VS Code (Copilot), Cursor, Claude Desktop/Code, etc. | [Alpaca MCP docs](https://docs.alpaca.markets/us/docs/alpaca-mcp-server) |

---

## Step 1 — Install `uv` (provides `uvx`)

The MCP config calls `uvx`, which ships with [uv](https://docs.astral.sh/uv/). If `uvx --version` already works, skip to Step 2.

```pwsh
# Recommended cross-platform installer:
#   see https://docs.astral.sh/uv/getting-started/installation/

# Windows fallback (also works everywhere) — installs into the Python user base:
python -m pip install --user uv
```

### PATH gotcha (Windows)

`pip install --user uv` drops `uv.exe` / `uvx.exe` into your **Python user Scripts** directory, which is often **not on PATH**. If your MCP client can't find `uvx`, add it:

```pwsh
# Find the directory:
python -c "import site, os; print(os.path.join(site.getuserbase(), 'Scripts'))"
# Typically: C:\Users\<you>\AppData\Roaming\Python\Python312\Scripts

# Add it to your user PATH permanently:
[Environment]::SetEnvironmentVariable(
  'Path',
  $env:Path + ';C:\Users\<you>\AppData\Roaming\Python\Python312\Scripts',
  'User'
)
```

Then **fully restart** your editor so the MCP host inherits the new PATH. Verify:

```pwsh
uvx --version
```

---

## Step 2 — Get Alpaca API keys (paper)

1. Create / log in to a [paper trading account](https://app.alpaca.markets/paper/dashboard/overview).
2. Generate an **API Key ID** and **Secret Key** from the dashboard.
3. Keep them handy for Step 3. The secret is shown once — regenerate if you lose it.

Paper keys are free and trade against a simulated $100k account. No funding required.

---

## Step 3 — Configure the MCP server

This repo uses VS Code, so the config lives at **`.vscode/mcp.json`** (note: VS Code uses the key `servers`, *not* `mcpServers` like Cursor/Claude Desktop).

```json
{
  "servers": {
    "alpaca": {
      "command": "uvx",
      "args": ["alpaca-mcp-server"],
      "env": {
        "ALPACA_API_KEY": "your_alpaca_api_key",
        "ALPACA_SECRET_KEY": "your_alpaca_secret_key"
      }
    }
  }
}
```

Replace the two placeholder values with your paper keys.

> 🔐 **`.vscode/` is gitignored in this repo**, so `.vscode/mcp.json` (and your keys) **will not be committed** — good. Never paste API keys into chat, and never force-add this file to git. If you prefer to keep secrets out of the file entirely, use VS Code's env-var substitution: `"ALPACA_API_KEY": "${env:ALPACA_API_KEY}"` and export the variables in your shell/OS secret store instead.

**Other clients** (config keys differ — see the [Alpaca docs](https://docs.alpaca.markets/us/docs/alpaca-mcp-server)):
- Cursor → `~/.cursor/mcp.json`, key `mcpServers`
- Claude Desktop → `claude_desktop_config.json`, key `mcpServers`
- Claude Code (CLI) → `claude mcp add alpaca --scope user --transport stdio uvx alpaca-mcp-server --env ALPACA_API_KEY=... --env ALPACA_SECRET_KEY=...`

---

## Step 4 — Verify the connection

Restart your MCP client so it picks up `.vscode/mcp.json`, then ask your assistant:

> "What is my Alpaca account balance and buying power?"

If you get account details back (status `ACTIVE`, ~$100k buying power on a fresh paper account), you're connected. A couple more smoke tests:

> "Get a snapshot of MSFT including latest trade and quote."
> "What are the most active stocks right now?"

### Argument-name gotchas

If you call tools directly (not via natural language), note the exact parameter names — they trip people up:

| Tool | Correct argument | Notes |
|---|---|---|
| `get_asset` | `symbol_or_asset_id` (singular) | e.g. `"MSFT"`; CUSIP also accepted |
| `get_stock_latest_quote` / `_trade` / `_snapshot` / `_bars` | `symbols` (plural) | comma-separated string, e.g. `"MSFT,AAPL"` |

Quotes default to the **IEX** feed on free/paper plans. Full **SIP** (`feed: "sip"`) requires an Algo Trader Plus market-data subscription.

---

## Step 5 — Scope the tools (recommended)

By default all toolsets load. You can restrict them with `ALPACA_TOOLSETS` (comma-separated) in the `env` block — useful to limit blast radius (e.g. read-only data, no trading) or to stay under an MCP client's tool-count cap.

```json
"env": {
  "ALPACA_API_KEY": "your_alpaca_api_key",
  "ALPACA_SECRET_KEY": "your_alpaca_secret_key",
  "ALPACA_TOOLSETS": "account,stock-data,crypto-data,options-data,news"
}
```

| Toolset | Scope |
|---|---|
| `account` | Account info, config, portfolio history, activities |
| `trading` | Orders, positions, exercise / do-not-exercise |
| `watchlists` | Watchlist CRUD |
| `assets` | Assets, option contracts, calendar, clock, corporate actions |
| `stock-data` | Stock bars, quotes, trades, snapshots, screeners |
| `crypto-data` | Crypto bars, quotes, trades, snapshots, orderbook |
| `options-data` | Option bars, trades, quotes, chain, snapshots |
| `corporate-actions` | Corporate actions (market data) |
| `news` | News articles |
| `fixed-income-data` | Fixed income latest quotes |
| `index-data` | Index values |

For a **read-only / no-trading** setup, simply omit `trading` from the list above.

---

## Paper vs. live trading

| Variable | Default | Effect |
|---|---|---|
| `ALPACA_PAPER_TRADE` | `true` | Paper trading (simulated). |
| `ALPACA_PAPER_TRADE=false` | — | **Live trading with real capital.** Requires live keys. |

Orders execute **directly** against Alpaca's Trading API — always review AI-suggested orders before confirming, and keep `ALPACA_PAPER_TRADE` at its default until you intend otherwise.

Other operational notes:
- **Rate limits** apply per account; high-frequency querying can trigger throttling.
- **Real-time data** for some feeds requires a paid Algo Trader Plus subscription (paper/free defaults to IEX).
- **V2 is not a drop-in for V1** — tool names/params changed. Pin `alpaca-mcp-server==1.x.x` if you need the old API.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Client reports `uvx` / command not found | `uvx` isn't on the MCP host's PATH — see [Step 1 PATH gotcha](#path-gotcha-windows), then restart the editor. |
| First call hangs ~30–60s | First run downloads the package + deps via `uvx`; subsequent launches are fast. |
| `401 / 403` or auth errors | Wrong/expired keys, or paper keys pointed at live (or vice versa). Regenerate from the dashboard. |
| `get_stock_bars` returns `403 subscription does not permit querying recent SIP data` | The free/paper plan blocks **recent** SIP. Pass `feed="iex"` (works for all dates). Historical dates also work on the default `sip` feed. `delayed_sip` is rejected (`400`) by the current server. |
| `asset not found for {symbol_or_asset_id}` | You passed the wrong argument name — use `symbol_or_asset_id` for `get_asset` (see [argument gotchas](#argument-name-gotchas)). |
| Server starts but no tools appear | Confirm the JSON parses and uses the `servers` key (VS Code), not `mcpServers`. |
| Want fewer tools | Set `ALPACA_TOOLSETS` (Step 5). |
| `/analyze` errors with `EdgarAccessDenied: SEC EDGAR returned 403` | Unrelated to Alpaca — `EDGAR_IDENTITY` must be a real `Name email@domain`. SEC blocks placeholder/`noreply` addresses (e.g. `*@users.noreply.github.com`). Set it in `.env`. |

---

## Reference links

- **Alpaca MCP Server docs** — https://docs.alpaca.markets/us/docs/alpaca-mcp-server
- **GitHub repo** — https://github.com/alpacahq/alpaca-mcp-server
- **V2 launch blog post** — https://alpaca.markets/blog/alpaca-launches-mcp-server-v2/
- **Other-client setup (README)** — https://github.com/alpacahq/alpaca-mcp-server/blob/main/README.md#setup
- **uv install guide** — https://docs.astral.sh/uv/getting-started/installation/
- **Alpaca paper dashboard** — https://app.alpaca.markets/paper/dashboard/overview
- **stonk-sage core setup** — [../README.md#setup](../README.md#setup)
