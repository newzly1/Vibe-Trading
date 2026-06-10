---
name: vt-elliott-wave
description: Elliott Wave Theory signal engine. Detects swing points through Zigzag, matches 5-wave impulse and 3-wave corrective structures, validates them with Fibonacci wave relationships, and generates trend-top / correction-complete signals. Pure in-house pandas implementation.
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

# Elliott Wave Theory

## Purpose

Classic wave theory based on the core assumption that markets move in fractal wave structures:

| Structure | Wave Count | Direction | Meaning |
|------|------|------|------|
| Impulse wave | 5 waves (1-2-3-4-5) | Trend-following | Main trend direction |
| Corrective wave | 3 waves (A-B-C) | Counter-trend | Pullback correction |

## Core Rules

### Three Iron Rules for Impulse Waves
1. Wave 2 cannot retrace beyond the start of wave 1
2. Wave 3 cannot be the shortest impulse wave
3. Wave 4 cannot enter the price territory of wave 1

### Fibonacci Relationships Between Waves
- Wave 2 retraces 0.5-0.618 of wave 1
- Wave 3 = wave 1 × 1.618 (most common)
- Wave 4 retraces 0.382 of wave 3
- Wave 5 ≈ the length of wave 1

## Signal Logic

- **5-wave advance completed** → sell (trend top)
- **ABC pullback completed** → buy (correction finished)
- **Wave 3 in progress** → stay with the trend (no reversal signal is generated)

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| swing_window | 10 | Rolling window for swing-point detection |
| fib_tolerance | 0.15 | Tolerance for Fibonacci ratios |
| min_wave_bars | 5 | Minimum number of candles per wave |

## Notes

Wave theory is highly subjective, and automatic counting can yield multiple interpretations. This implementation uses a "simplest effective single interpretation" strategy and would rather miss signals than misclassify them.

## Dependencies

```bash
pip install pandas numpy requests
```

## Signal Convention

- `1` = long, `-1` = short, `0` = stand aside
