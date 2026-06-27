# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Integration: Vibe-Trading Financial Analysis

Vibe-Trading's core financial analysis capabilities have been ported to Claude Code, bypassing V-T's own ReAct agent loop and using Claude Code's native reasoning for financial analysis.

### Capability Overview

| Capability | Vehicle | Purpose |
|------------|---------|---------|
| Domain knowledge | 75 `.claude/skills/vt-*` skills | Formulas, parameters, methodology reference (auto-discovered, loaded on demand) |
| Data + computation | MCP tools (35, via `.mcp.json`) | Market data, backtesting, factor analysis, Alpha Zoo, options pricing, hypothesis registry, fundamentals, events, etc. |
| Parallel analysis | `.claude/agents/` subagents + `.claude/commands/` slash commands + `Agent` tool | Native replacement for V-T's Swarm — 29 preset teams ported as subagents + `/`-commands |
| Code execution | `Bash` tool | Run Python scripts for custom computation |

### MCP Tools Quick Reference

Connected via `.mcp.json` to the `vibe-trading-mcp` server, exposing 35 tools:

**Market data**: `get_market_data` — fetch OHLCV (A-shares / HK / US / crypto). For A-shares, explicitly specify `source="akshare"` or `source="tushare"`; do not rely on `source="auto"`.

**A-share fundamental data** (new): `get_fundamentals` (daily PE/PB/ROE/market cap via Tushare daily_basic), `get_financial_statements` (income/balancesheet/cashflow/fina_indicator with PIT anti-lookahead), `get_money_flow` (北向/主力资金流向), `get_margin_data` (融资融券余额与买卖额), `get_earnings_forecast` (分析师一致预期, SUE/PEAD), `get_events` (结构化新闻事件+情绪评分 via RSSHub).

**Backtesting & analysis**: `backtest` (requires a pre-prepared directory with `config.json` + `code/signal_engine.py`), `factor_analysis` (factor IC/return analysis), `analyze_options` (options pricing & Greeks), `pattern_recognition` (candlestick pattern recognition).

**Alpha Zoo**: `alpha_zoo` (browse/list/get 452 pre-built alphas), `alpha_bench` (batch benchmark a zoo — IC mean/std/IR/positive-ratio + HTML report), `alpha_compare` (head-to-head ranking of named alphas by IC metric).

**Content & file I/O**: native to Claude Code — use `WebFetch` / `WebSearch` for web content and `Read` / `Write` / `Edit` for files (the MCP `read_url` / `read_document` / `web_search` / `read_file` / `write_file` wrappers were removed in the port).

**Trading connections**: `trading_connections`, `trading_select_connection`, `trading_check`, `trading_account`, `trading_positions`, `trading_orders`, `trading_quote`, `trading_history`.

**Research goals**: `start_research_goal`, `get_research_goal`, `add_goal_evidence`, `update_research_goal_status`.

**Hypothesis registry**: `create_hypothesis`, `update_hypothesis`, `link_backtest` (attach run cards), `search_hypotheses` (text search by status/query).

**Trade journal & shadow**: `analyze_trade_journal`, `extract_shadow_strategy`, `run_shadow_backtest`, `render_shadow_report`, `scan_shadow_signals`.

**Skills & discovery**: native to Claude Code — skills are auto-discovered from `.claude/skills/` and loaded on demand via the `Skill` tool (the MCP `list_skills`/`load_skill` wrappers were removed in the port).

### Skill Usage Guide

75 `vt-*` skills are installed at `.claude/skills/`. Claude Code auto-discovers them at startup and injects one-line summaries into the system prompt. When a task touches a specific financial domain, the corresponding SKILL.md is auto-loaded as context.

**Skills are knowledge documents, not executable code** — they provide formulas, parameters, and methodology references. Actual computation still requires MCP tools or Bash-executed Python.

### Key Usage Patterns

1. **Fetch → analyze → backtest** pipeline: call MCP tools directly in sequence; no agent loop needed.
2. **Swarm replacement (subagents + commands)**: run a ported preset via its slash command (e.g. `/investment-committee <target> <market>`) or dispatch `.claude/agents/*` subagents directly with the `Agent` tool. `run_swarm` has been removed.
3. **Skill guidance + MCP execution**: consult the relevant vt-* skill for methodology first, then execute computation via MCP tools.
4. **Data first, always**: Before any analysis, call `get_market_data` with explicit `source` (A-shares: `source="akshare"` or `source="tushare"`; fallbacks: `tencent` → `baostock` → `mootdx`). For fundamentals/money-flow/margin data, use the new dedicated tools (`get_fundamentals`, `get_money_flow`, etc.) which route through Tushare. Never substitute WebSearch for real market data — WebSearch is for qualitative context only.

**Domain-workflow routing** (detailed step sequences live in the named skills):
- **Strategy → backtest:** consult **vt-strategy-generate** (SignalEngine contract + the author config.json/signal_engine.py → `backtest` → read metrics flow). Do not write a `run_backtest.py`; the engine is built-in.
- **Trade-journal analysis:** consult **vt-trade-journal**, then `analyze_trade_journal`.
- **Shadow strategy:** consult **vt-shadow-account** FIRST (it defines rules, attribution semantics, and the research-only disclaimer), then the `*_shadow_*` tools in order.

### Swarm Replacement: Subagents + Slash Commands

V-T's 29 YAML swarm presets are ported to native Claude Code primitives — no
`run_swarm`, no V-T ReAct loop. Each preset became:

- **Subagents** (`.claude/agents/<preset>-<role>.md`, 113 total) — one per preset
  role, carrying that role's persona, analytical dimensions, and output spec.
- **A slash command** (`.claude/commands/<preset>.md`, 29 total) — orchestrates
  the preset's task DAG: it dispatches the subagents in dependency order
  (phases run sequentially; agents within a phase run in parallel) and feeds
  each downstream role its upstream outputs.

**Usage:**

```
/investment-committee 300274.SZ A-shares
/equity-research-team A-shares "Q2 2026 outlook"
```

The command (read by the orchestrating agent) lays out the phases and dispatches
each `Agent(subagent_type="<preset>-<role>", prompt=...)`. You can also dispatch
the subagents manually with the `Agent` tool for ad-hoc team compositions.

**Regenerating:** the subagents and commands are generated from the YAML presets
by `claude-trading/tools/port_swarm.py` (corpus-tested by `test_port_swarm.py`).
Edit a preset and re-run the converter; do not hand-edit generated files.

### Known Limitations

- `run_swarm` and the swarm run-management tools have been **removed** from the MCP catalogue (the contract test enforces their absence). Use the `/`-commands in `.claude/commands/` instead.
- A-share data: `get_market_data` with `source="auto"` may route to an unsupported source; explicitly specify `source="akshare"` or `source="tushare"`.
- `backtest` requires a pre-prepared directory with `config.json` + `code/signal_engine.py`.
- The 75 skills are knowledge documents, not executable code.
