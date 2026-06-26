---
name: vt-seasonal
description: Seasonal/calendar-effect strategy. Generates trading signals from time-based patterns such as month-of-year effects and day-of-week effects. Suitable for any OHLCV data.
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
# Seasonal / Calendar Effect Strategy

## Purpose

Uses time-based regularities in financial markets (month effects, day-of-week effects, and similar patterns) to generate trading signals. Examples include the China A-share "spring rally" (January-March) and the "sell in May" effect.

## Signal Logic

### Month Effect (Default)

- Specified bullish months → go long
- Specified bearish months → go short / stay out
- All other months → stay flat

### Day-of-Week Effect (Optional Overlay)

- Monday / Friday effects
- Start-of-month / end-of-month effects

### Combined Mode

Month signal × weekday signal; open a position only when both confirm.

## Common Calendar Effects Reference

| Effect | Description | Reference Configuration |
|------|------|---------|
| Spring rally | Higher probability of gains in China A-shares from January to March | bullish_months=[1,2,3] |
| Sell in May | Weaker performance from May to October | bearish_months=[5,6,7,8,9,10] |
| Year-end effect | Institutional rebalancing in December | bullish_months=[11,12] |
| Monday effect | Lower returns on Mondays | bearish_weekdays=[0] |
| Friday effect | Higher returns on Fridays | bullish_weekdays=[4] |

## Parameters

| Parameter | Default | Description |
|------|--------|------|
| bullish_months | [1, 2, 3, 11, 12] | Bullish months |
| bearish_months | [5, 6, 7, 8, 9] | Bearish months |
| use_weekday | False | Whether to enable weekday effects |
| bullish_weekdays | [4] | Bullish weekdays (0=Monday, 4=Friday) |
| bearish_weekdays | [0] | Bearish weekdays |

## Common Pitfalls

- `pd.DatetimeIndex.month` starts from 1 (1=January)
- `pd.DatetimeIndex.weekday` starts from 0 (0=Monday, 4=Friday)
- Seasonal strategies are statistical regularities, not deterministic signals, so pay attention to sample size in backtests
- Neutral months (neither in `bullish` nor `bearish`) should output 0 and must not be skipped

## Dependencies

```bash
pip install pandas numpy
```

## Signal Convention

- `1` = long (bullish window), `-1` = short (bearish window), `0` = stand aside
