---
name: vt-ccxt
description: CCXT unified crypto exchange library (100+ exchanges). Free public market data. Fallback when OKX is unavailable.
---

<!--
Vibe-Trading MCP tools available to this skill (Claude Code is the harness; key tools):
  Market data:    get_market_data
  A-share data:   get_fundamentals, get_financial_statements, get_money_flow,
                  get_margin_data, get_earnings_forecast, get_events
  Backtest/anlys: backtest, factor_analysis, analyze_options, pattern_recognition
  Alpha Zoo:      alpha_zoo, alpha_bench, alpha_compare
  Hypotheses:     create_hypothesis, update_hypothesis, link_backtest, search_hypotheses
  Research goals: start_research_goal, get_research_goal, add_goal_evidence, update_research_goal_status
  Journal/shadow: analyze_trade_journal, extract_shadow_strategy, run_shadow_backtest,
                  render_shadow_report, scan_shadow_signals
  Trading (read-only): trading_connections, trading_select_connection, trading_check,
                  trading_account, trading_positions, trading_orders, trading_quote, trading_history
Native Claude Code tools (use directly, NOT an MCP tool): Read, Write, Edit, WebFetch, WebSearch, Skill.
-->

## Overview

CCXT is a unified cryptocurrency exchange trading library supporting 100+ exchanges including Binance, Bybit, OKX, Coinbase, Kraken, and more. Public market data (OHLCV, tickers, order books) requires no API key.

- GitHub: https://github.com/ccxt/ccxt (35k+ stars)
- Install: `pip install ccxt`

## Quick Start

```python
import ccxt

exchange = ccxt.binance({"enableRateLimit": True})

# Fetch daily OHLCV
ohlcv = exchange.fetch_ohlcv("BTC/USDT", "1d", limit=100)
# Returns: [[timestamp, open, high, low, close, volume], ...]

# Fetch ticker
ticker = exchange.fetch_ticker("ETH/USDT")
print(f"ETH price: {ticker['last']}")
```

## Key Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `fetch_ohlcv(symbol, timeframe, since, limit)` | Historical candles | `[[ts, o, h, l, c, v], ...]` |
| `fetch_ticker(symbol)` | Latest quote | `{last, bid, ask, volume, ...}` |
| `fetch_tickers(symbols)` | Batch quotes | `{symbol: ticker}` |
| `fetch_order_book(symbol, limit)` | Order book | `{bids, asks, timestamp}` |
| `fetch_trades(symbol, since, limit)` | Recent trades | `[{price, amount, side, timestamp}, ...]` |

## Timeframes

`1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `6h`, `12h`, `1d`, `1w`, `1M`

Note: not all exchanges support all timeframes. Use `exchange.timeframes` to check.

## Symbol Format

CCXT uses slash format: `BTC/USDT`, `ETH/BTC`, `SOL/USDT`

The project's DataLoader automatically converts `BTC-USDT` (hyphen) to `BTC/USDT` (slash).

## Exchange Selection

Set via environment variable: `CCXT_EXCHANGE=binance` (default)

Popular exchanges: `binance`, `bybit`, `okx`, `coinbase`, `kraken`, `bitget`, `gate`

## Built-in Loader

The project has a built-in CCXT DataLoader at `backtest/loaders/ccxt_loader.py`. It serves as a fallback when the OKX loader is unavailable.

## Pagination

For long history, CCXT paginates via the `since` parameter (millisecond timestamp). The built-in loader handles this automatically (up to 200 pages).
