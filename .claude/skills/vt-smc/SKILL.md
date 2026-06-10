---
name: vt-smc
description: Smart Money Concepts (ICT) signal engine. Uses the smartmoneyconcepts library to implement institutional-trading-school analysis of BOS, ChoCH, FVG, and order blocks (OB).
---

<!--
Available Vibe-Trading MCP tools for this skill:
  - get_market_data(codes, start_date, end_date, source, interval) — fetch OHLCV
  - backtest(run_dir) — run backtest from config.json + signal_engine.py
  - factor_analysis(codes, factor_name, start_date, end_date, ...) — factor IC/returns
  - analyze_options(...) — options pricing & greeks
  - pattern_recognition(run_dir) — chart pattern detection
  - read_url(url) / read_document(path) / web_search(query) — content tools
  - write_file(path, content) / read_file(path) — file I/O
  - list_skills() / load_skill(name) — skill discovery
-->

# Smart Money Concepts

## Purpose

The modern institutional trading school (ICT / Inner Circle Trader), built around the core idea of tracking the behavior of "smart money" (institutional capital):

| Concept | English | Meaning |
|------|------|------|
| Break of structure | BOS (Break of Structure) | Trend continuation signal |
| Change of character | ChoCH (Change of Character) | Trend reversal signal |
| Fair value gap | FVG (Fair Value Gap) | Price refill target |
| Order blocks | Order Blocks | Institutional order concentration zones |
| Liquidity | Liquidity | Stop-hunt target zones |

## Signal Logic

Direction from ChoCH + confirmation from BOS + filtering by FVG:
- **Long**: bullish ChoCH/BOS + bullish FVG exists
- **Short**: bearish ChoCH/BOS + bearish FVG exists
- **Stand aside**: no structural signal or conflicting directions

## Dependencies

```bash
pip install smartmoneyconcepts pandas numpy requests
```

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| swing_length | 10 | Window for swing high/low detection |
| close_break | True | Whether BOS/ChoCH requires a closing-price break |

## Signal Convention

- `1` = long, `-1` = short, `0` = stand aside
