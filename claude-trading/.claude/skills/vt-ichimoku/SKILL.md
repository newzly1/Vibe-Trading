---
name: vt-ichimoku
description: Ichimoku Kinko Hyo five-line system signal engine. A standalone Japanese technical-analysis school that generates trading signals from Tenkan/Kijun crossovers, cloud position, and Chikou confirmation. Pure pandas implementation.
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
