---
name: vt-candlestick
description: Candlestick pattern recognition engine, pure pandas vectorized implementation of 15 classic candlestick patterns (5 single-candle + 5 double-candle + 4 triple-candle + 1 trend confirmation), generating a composite signal from bullish/bearish pattern scores.
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
# Candlestick Pattern Recognition

## Purpose

Identifies 15 classic candlestick patterns and generates trading signals:

### Single-Candle Patterns (5)
| Pattern | Signal | Description |
|------|------|------|
| Hammer | Bullish | Long lower shadow with a small body at the top |
| Inverted Hammer | Bullish | Long upper shadow with a small body at the bottom |
| Shooting Star | Bearish | Long upper shadow with a small body at the bottom (appears after an uptrend) |
| Doji | Neutral | Open and close are nearly equal |
| Spinning Top | Neutral | Small body with roughly equal upper and lower shadows |

### Double-Candle Patterns (5)
| Pattern | Signal |
|------|------|
| Bullish Engulfing | Bullish |
| Bearish Engulfing | Bearish |
| Bullish Harami | Bullish |
| Bearish Harami | Bearish |
| Piercing Line | Bullish |
| Dark Cloud Cover | Bearish |

### Triple-Candle Patterns (4)
| Pattern | Signal |
|------|------|
| Morning Star | Bullish |
| Evening Star | Bearish |
| Three White Soldiers | Bullish |
| Three Black Crows | Bearish |

## Signal Logic

Bullish patterns score +1, bearish patterns score -1. Go long when the total score is > 0, go short when it is < 0, and stand aside when it equals 0.

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| body_pct | 0.1 | Threshold for body-to-range ratio in a doji |
| shadow_ratio | 2.0 | Ratio of shadow length to body length |

## Dependencies

```bash
pip install pandas numpy requests
```

## Signal Convention

- `1` = long, `-1` = short, `0` = stand aside
