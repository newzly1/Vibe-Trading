---
name: vt-harmonic
description: Harmonic Patterns signal engine. Identifies XABCD five-point structures such as Gartley/Bat/Butterfly/Crab based on Fibonacci geometry, and generates trading signals in the PRZ (Potential Reversal Zone).
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
# Harmonic Patterns

## Purpose

The Fibonacci geometry school uses precise ratio relationships to identify price patterns:

| Pattern | B-Point Retracement | D-Point Retracement | Direction |
|------|---------|---------|------|
| Gartley | 0.618 XA | 0.786 XA | Reversal |
| Bat | 0.382-0.5 XA | 0.886 XA | Reversal |
| Butterfly | 0.786 XA | 1.27 XA | Reversal |
| Crab | 0.382-0.618 XA | 1.618 XA | Reversal |

## Core Concepts

- **XABCD five-point pattern**: a price structure defined by precise Fibonacci ratios
- **PRZ (Potential Reversal Zone)**: the convergence area around point D, where reversal probability is high
- Bullish pattern (point D at the bottom) → buy signal
- Bearish pattern (point D at the top) → sell signal

## Dependencies

```bash
pip install pyharmonics pandas numpy requests
```

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| is_stock | False | Whether the instrument is a stock (affects analysis parameters) |

## Signal Convention

- `1` = long, `-1` = short, `0` = stand aside
