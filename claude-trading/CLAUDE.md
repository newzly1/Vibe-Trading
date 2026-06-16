# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Integration: Vibe-Trading Financial Analysis

Vibe-Trading's core financial analysis capabilities have been ported to Claude Code, bypassing V-T's own ReAct agent loop and using Claude Code's native reasoning for financial analysis.

### Capability Overview

| Capability | Vehicle | Purpose |
|------------|---------|---------|
| Domain knowledge | 80 `.claude/skills/vt-*` skills | Formulas, parameters, methodology reference (auto-discovered, loaded on demand) |
| Data + computation | MCP tools (42, via `.mcp.json`) | Market data, backtesting, factor analysis, Alpha Zoo, options pricing, hypothesis registry, fundamentals, events, etc. |
| Parallel analysis | `vt-swarm-*` skills + `.claude/workflows/` + `Agent` tool | Replaces V-T's Swarm multi-agent framework (3 presets ported, 25 remaining) |
| Code execution | `Bash` tool | Run Python scripts for custom computation |

### MCP Tools Quick Reference

Connected via `.mcp.json` to the `vibe-trading-mcp` server, exposing 42 tools:

**Market data**: `get_market_data` — fetch OHLCV (A-shares / HK / US / crypto). For A-shares, explicitly specify `source="akshare"` or `source="tushare"`; do not rely on `source="auto"`.

**A-share fundamental data** (new): `get_fundamentals` (daily PE/PB/ROE/market cap via Tushare daily_basic), `get_financial_statements` (income/balancesheet/cashflow/fina_indicator with PIT anti-lookahead), `get_money_flow` (北向/主力资金流向), `get_margin_data` (融资融券余额与买卖额), `get_earnings_forecast` (分析师一致预期, SUE/PEAD), `get_events` (结构化新闻事件+情绪评分 via RSSHub).

**Backtesting & analysis**: `backtest` (requires a pre-prepared directory with `config.json` + `code/signal_engine.py`), `factor_analysis` (factor IC/return analysis), `analyze_options` (options pricing & Greeks), `pattern_recognition` (candlestick pattern recognition).

**Alpha Zoo**: `alpha_zoo` (browse/list/get 452 pre-built alphas), `alpha_bench` (batch benchmark a zoo — IC mean/std/IR/positive-ratio + HTML report), `alpha_compare` (head-to-head ranking of named alphas by IC metric).

**Content tools**: `read_url`, `read_document`, `web_search`, `read_file`, `write_file`.

**Trading connections**: `trading_connections`, `trading_select_connection`, `trading_check`, `trading_account`, `trading_positions`, `trading_orders`, `trading_quote`, `trading_history`.

**Research goals**: `start_research_goal`, `get_research_goal`, `add_goal_evidence`, `update_research_goal_status`.

**Hypothesis registry**: `create_hypothesis`, `update_hypothesis`, `link_backtest` (attach run cards), `search_hypotheses` (text search by status/query).

**Trade journal & shadow**: `analyze_trade_journal`, `extract_shadow_strategy`, `run_shadow_backtest`, `render_shadow_report`, `scan_shadow_signals`.

**Skills & discovery**: `list_skills`, `load_skill`.

### Skill Usage Guide

80 `vt-*` skills are installed at `.claude/skills/`. Claude Code auto-discovers them at startup and injects one-line summaries into the system prompt. When a task touches a specific financial domain, the corresponding SKILL.md is auto-loaded as context.

**Skills are knowledge documents, not executable code** — they provide formulas, parameters, and methodology references. Actual computation still requires MCP tools or Bash-executed Python.

### Key Usage Patterns

1. **Fetch → analyze → backtest** pipeline: call MCP tools directly in sequence; no agent loop needed.
2. **Swarm replacement (Skills + Workflows)**: V-T's 28 Swarm presets are being ported as `vt-swarm-*` skills (knowledge) + `.claude/workflows/*.js` (deterministic orchestration). 3 presets ported so far — see [Swarm Replacement](#swarm-replacement-skills--workflows) below. Do NOT use `run_swarm`.
3. **Skill guidance + MCP execution**: consult the relevant vt-* skill for methodology first, then execute computation via MCP tools.
4. **Data first, always**: Before any analysis, call `get_market_data` with explicit `source` (A-shares: `source="akshare"` or `source="tushare"`; fallbacks: `tencent` → `baostock` → `mootdx`). For fundamentals/money-flow/margin data, use the new dedicated tools (`get_fundamentals`, `get_money_flow`, etc.) which route through Tushare. Never substitute WebSearch for real market data — WebSearch is for qualitative context only.

### Swarm Replacement: Skills + Workflows

V-T's 28 YAML swarm presets are being ported to a two-layer architecture: **Skills** (knowledge/roles) + **Workflows** (deterministic DAG orchestration). This gives you the preset knowledge without V-T's ReAct agent loop.

**Ported presets (3/28)**:

| Preset | Skill | Workflow | Use Case |
|--------|-------|----------|----------|
| `investment_committee` | `vt-swarm-investment-committee` | `/workflow investment-committee` | Bull/bear debate → risk review → PM decision |
| `equity_research_team` | `vt-swarm-equity-research-team` | `/workflow equity-research-team` | Macro → sector → stock → aggregated report |
| `quant_strategy_desk` | `vt-swarm-quant-strategy-desk` | `/workflow quant-strategy-desk` | Screening + factor mining → backtest → risk audit |

**Usage pattern**:

```
# Option A: Use the workflow (recommended — deterministic DAG)
/workflow investment-committee target="300274.SZ" market="A-shares"

# Option B: Manual Agent dispatch (flexible, follow skill guidance)
Skill("vt-swarm-investment-committee")  # load the recipe
Agent("bull_advocate", prompt="...")    # dispatch bull
Agent("bear_advocate", prompt="...")    # dispatch bear (parallel)
# ... then risk_officer → portfolio_manager sequentially
```

**Why this replaces `run_swarm`**:
- Workflows use `parallel()` → `agent()` for deterministic DAG execution (no LLM guessing parallelism)
- Skills provide the role definitions, output templates, and tool assignments from YAML presets
- All agents are native Claude Code sub-agents with full MCP tool access
- No V-T ReAct loop, no Python ThreadPoolExecutor, no swarm crash recovery

**Adding more presets**: See the 3 existing skills + workflows as templates. Each YAML preset maps to one `SKILL.md` (role definitions, output specs) + one `.js` workflow (DAG structure in `parallel()`/`pipeline()`).

### Known Limitations

- `run_swarm` is **deprecated** — use `vt-swarm-*` skills + workflows instead. The MCP tool still exists for backward compatibility but goes through V-T's ReAct agent loop.
- A-share data: `get_market_data` with `source="auto"` may route to an unsupported source; explicitly specify `source="akshare"` or `source="tushare"`.
- `backtest` requires a pre-prepared directory with `config.json` + `code/signal_engine.py`.
- The 80 skills are knowledge documents, not executable code.
