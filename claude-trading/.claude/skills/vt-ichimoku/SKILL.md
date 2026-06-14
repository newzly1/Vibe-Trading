---
name: vt-ichimoku
description: Ichimoku Kinko Hyo five-line system signal engine. A standalone Japanese technical-analysis school that generates trading signals from Tenkan/Kijun crossovers, cloud position, and Chikou confirmation. Pure pandas implementation.
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

# Ichimoku Kinko Hyo

## Purpose

A standalone Japanese technical analysis framework that uses a five-line system and the cloud to provide a complete trend-evaluation structure:

| Line | Japanese | Calculation | Meaning |
|----|------|------|------|
| Conversion line | Tenkan-sen | (9H+9L)/2 | Short-term trend |
| Base line | Kijun-sen | (26H+26L)/2 | Medium-term trend |
| Leading Span A | Senkou Span A | (Tenkan+Kijun)/2 shifted forward by 26 | Upper cloud boundary |
| Leading Span B | Senkou Span B | (52H+52L)/2 shifted forward by 26 | Lower cloud boundary |
| Lagging Span | Chikou Span | Closing price shifted backward by 26 | Trend confirmation |

## Signal Logic

Signals are triggered only on TK crossover events, with three filters:
- **Strong buy**: bullish TK cross + price above the cloud + bullish cloud (A > B)
- **Strong sell**: bearish TK cross + price below the cloud + bearish cloud (A < B)
- All other cases → stand aside

Warm-up requires 78 candles (52+26).

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| tenkan_period | 9 | Tenkan-sen period |
| kijun_period | 26 | Kijun-sen period |
| senkou_b_period | 52 | Senkou Span B period |
| displacement | 26 | Forward/backward shift period |

## Dependencies

```bash
pip install pandas numpy requests
```

## Signal Convention

- `1` = long, `-1` = short, `0` = stand aside
