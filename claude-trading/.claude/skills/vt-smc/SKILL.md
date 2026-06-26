---
name: vt-smc
description: Smart Money Concepts (ICT) signal engine. Uses the smartmoneyconcepts library to implement institutional-trading-school analysis of BOS, ChoCH, FVG, and order blocks (OB).
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
