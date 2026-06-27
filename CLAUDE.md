# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Integration: Vibe-Trading Financial Analysis

Vibe-Trading's core financial-analysis capabilities have been ported to Claude Code
as the primary harness: Claude Code's native reasoning replaces V-T's own ReAct agent
loop, and the V-T harness/services (loop, session, providers, CLI, REST API, web
frontend, live-order engine, swarm engine) have been removed.

**The canonical Claude Code integration reference is
[`claude-trading/CLAUDE.md`](claude-trading/CLAUDE.md)** — read it for the full MCP
tool catalogue, the skills usage guide, and the swarm-replacement (subagents +
slash commands) workflow. Summary:

| Capability | Vehicle | Purpose |
|------------|---------|---------|
| Domain knowledge | 75 `claude-trading/.claude/skills/vt-*` skills | Formulas, parameters, methodology (auto-discovered, loaded on demand) |
| Data + computation | MCP tools (35, via `.mcp.json` → `vibe-trading-mcp`) | Market/fundamental data, backtesting, factors, Alpha Zoo, options, registries |
| Parallel analysis | `claude-trading/.claude/agents/*` subagents + `.claude/commands/*` slash commands + `Agent` tool | Native replacement for V-T's Swarm (29 presets ported) |
| Code execution | `Bash` tool | Run Python scripts for custom computation |

**Key usage patterns:**
1. **Data first, always.** Before any analysis, call `get_market_data` with an explicit
   `source` (A-shares: `source="akshare"` or `source="tushare"`). For
   fundamentals/money-flow/margin, use the dedicated tools (`get_fundamentals`,
   `get_money_flow`, …). Never substitute WebSearch for real market data.
2. **Fetch → analyze → backtest** in sequence — call MCP tools directly; no agent loop.
3. **Swarm replacement:** run a ported preset via its slash command
   (e.g. `/investment-committee 300274.SZ A-shares`) or dispatch
   `claude-trading/.claude/agents/*` subagents with the `Agent` tool. `run_swarm` and
   the run-management tools have been removed (contract-locked absent).
4. **No live orders.** No order-placement tool (`place_order`/`cancel_order`/
   `trading_place_order`/`trading_cancel_order`/`propose_mandate`) is exposed; the
   contract test pins them absent. The `trading_*` tools are read-only.

---

## Project Architecture (Vibe-Trading Codebase)

The sections below describe the repo's surviving architecture, for reference when
modifying code, maintaining the MCP server, or extending skills. After the Claude
Code port the codebase is the MCP backend (capabilities) plus the
`claude-trading/` port artifacts — the V-T harness, services, live-order engine,
and swarm engine were removed.

### Package Layout

`pyproject.toml` maps `package-dir = {"" = "agent"}` — **`agent/` is the Python package
root**. Inside it, `src/` and `backtest/` are top-level packages. The sole entry point
is `vibe-trading-mcp` → `mcp_server:main`.

### Essential Commands

```bash
# Install
pip install -e ".[dev]"

# Full test suite (exclude e2e and live-LLM tests)
pytest --ignore=agent/tests/e2e_backtest --ignore=agent/tests/test_e2e_harness_v2.py --tb=short -q

# Alpha zoo gates only
pytest agent/tests/factors/test_alpha_purity.py agent/tests/factors/test_lookahead.py -q

# MCP capability surface (catalogue lock + server smoke)
pytest agent/tests/test_mcp_capability_contract.py agent/tests/test_mcp_server_smoke.py -q

# Syntax check (run before tests)
cd agent && python -m py_compile mcp_server.py

# Regenerate the ported skills / subagents+commands from their sources
python claude-trading/tools/port_skills.py
python claude-trading/tools/port_swarm.py

# Lint
ruff check agent/
```

### MCP Server (`agent/mcp_server.py`)

Built on `fastmcp`. Exposes V-T's capabilities as 35 MCP tools via stdio (default) or
SSE transport. Each `@mcp.tool` wrapper is defined explicitly; data/goal/hypothesis
tools are inline, and the heavier tools (backtest, factors, alpha zoo, options,
pattern, shadow, trade journal, read-only `trading_*`) are dispatched by name through
`build_registry()` (`registry.execute("<name>", …)`). The catalogue is selective — the
registry may hold more tools than the server exposes.

**Adding a new MCP tool**:
1. Create a file in `agent/src/tools/` with a class extending `BaseTool`
2. Set a non-empty `name`, implement `execute(**kwargs) -> str` (return JSON)
3. Add an `@mcp.tool` wrapper in `mcp_server.py` that calls `registry.execute(...)`
4. Restart the MCP server for the new tool to take effect

The catalogue is contract-locked by `agent/tests/test_mcp_capability_contract.py`:
order tools and harness-duplicate I/O / skill / swarm tools are pinned **absent**;
the core analysis tools are pinned **present**.

### Skills System (`agent/src/skills/`)

Bundled financial-analysis skills, one directory per skill under
`agent/src/skills/<name>/` with a `SKILL.md` (frontmatter: name, description,
category). These are the canonical SOURCE; the Claude Code skills under
`claude-trading/.claude/skills/vt-*/` are GENERATED from them by
`claude-trading/tools/port_skills.py` (corpus-tested by `test_port_skills.py`). Claude
Code auto-discovers the generated skills and loads each `SKILL.md` on demand.

### Tool Auto-Discovery (`agent/src/tools/__init__.py`)

**No manual registration.** `build_registry()` discovers `BaseTool` subclasses by
scanning `BaseTool.__subclasses__()`, wires local tools first, then optionally appends
remote MCP tools from `AgentConfig.mcp_servers`. Goal tools receive special constructor
injection (session_id, event_callbacks); shell tools are gated by `include_shell_tools`.

### Alpha Zoo / Factors (`agent/src/factors/`)

452 pre-built cross-sectional alphas across 4 zoos under `zoo/`:
- `alpha101/` — Kakushadze 101 Formulaic Alphas
- `gtja191/` — Guotai Junan 2014 short-horizon factors
- `qlib158/` — Microsoft Qlib (Apache-2.0 attributed)
- `academic/` — Fama-French 5 + Carhart price-based proxies

**Architecture**: `registry.py` AST-scans zoo modules to extract `__alpha_meta__` dicts
(Pydantic-validated) without importing code. Each alpha file defines `__alpha_meta__`
(id, theme, formula_latex, columns_required, universe, frequency, etc.) and a pure
`compute(panel) -> DataFrame` function. **Purity gate** (`test_alpha_purity.py`)
AST-scans for forbidden imports — only `pandas`, `numpy`, `scipy.*`, and
`src.factors.base` are allowed. **Lookahead gate** (`test_lookahead.py`) verifies no
forward leakage. `bench_runner.py` evaluates zoos via IC/IR; `compare_runner.py` does
head-to-head comparisons with subset filtering.

### Backtest System (`agent/backtest/`)

- **`runner.py`**: Entry point that reads `config.json` from a run directory, resolves
  the loader, imports the signal engine, and runs the backtest.
- **`loaders/`**: DataLoader Protocol with 7 sources (tushare, yfinance, okx, ccxt,
  akshare, mootdx, futu) and auto-fallback chains.
- **`engines/`**: 7 asset-class engines + `CompositeEngine` (cross-market with shared
  capital pool) + options portfolio engine. Market detection lives in
  `engines/_market_hooks.py`.
- **`optimizers/`**: 4 portfolio optimizers (mean_variance, risk_parity,
  equal_volatility, max_diversification).
- Config validation uses Pydantic (`BacktestConfigSchema`). The `--interval` flag
  supports `1m`/`5m`/`15m`/`30m`/`1H`/`4H`/`1D`.

### Trading Connectors (`agent/src/trading/`)

Read-only broker access for the `trading_*` tools (connections, account, positions,
open orders, quote, history). 10 connectors: ibkr, robinhood, alpaca, binance, okx,
futu, tiger, longbridge, dhan, shoonya. Connector-first design: users select a
profile and all `trading_*` tools route through it. **No order-placement path is
exposed in this port** — the live-order engine, mandate, kill switch, order guard,
and audit ledger were removed (decision: no live trading in the Claude Code harness).

### Other Packages

- **`agent/src/hypotheses/`** — Durable research hypothesis registry with status
  tracking and backtest linking.
- **`agent/src/shadow_account/`** — Extracts trading patterns from user broker
  statements; generates PDF reports via Jinja2 + WeasyPrint.
- **`agent/src/goal/`** — Research goal runtime: persistent objectives with criteria,
  evidence, claims, and completion policy.
- **`agent/src/security/`** — Path containment, secret redaction, and sandbox
  enforcement.

Free-form cross-session memory now uses Claude Code's native file-based memory; V-T's
`src/memory/persistent.py` and the `remember` tool were removed.

### Config System (`agent/src/config/`)

Pydantic-based schema for `~/.vibe-trading/agent.json`. Validates MCP server entries
(used when `build_registry` appends remote MCP tools).

## Key Environment Variables

| Variable | Role |
|----------|------|
| `VIBE_TRADING_ENABLE_SHELL_TOOLS` | Opt-in for shell tools in networked MCP deployments |
| `VIBE_TRADING_DATA_CACHE` | Opt-in local data caching (`~/.vibe-trading/cache`) |
| `TUSHARE_TOKEN` | Optional A-share data token (falls back to mootdx/AKShare) |

## Test Organization

Tests live in `agent/tests/`. `conftest.py` provides shared fixtures. Test files are
named by feature (not by source module). Key markers: `@pytest.mark.unit` (fast, no
network), `@pytest.mark.integration` (may need network). `test_e2e_harness_v2.py` is
gated behind `VIBE_TRADING_RUN_LIVE_E2E=1` (real LLM calls). The converter corpus tests
live under `claude-trading/tools/`.

## Code Style

- **DCO**: Every community commit MUST carry `Signed-off-by:` trailer (`git commit -s`). No CLA required.
- **No AI-attribution trailers**: Do not add `Co-Authored-By:` or AI-assistant attribution lines.
- **Alpha zoo files** (`src/factors/zoo/**/*.py`) are exempt from `F401` (unused-import) — the full `base.py` surface is imported verbatim to match research formulas.
- Type annotations on all public function/method signatures.
- Google-style docstrings (`Args:` / `Returns:` / `Raises:`).
- File length: prefer under 400 lines, 800 hard cap.
- No hardcoded paths, secrets, or URLs — config via `.env`, YAML, or module-level constants.
- Format with Black; lint with ruff (E/F/W rules, 120-char lines).
- Do not commit secrets, `.env` files with real values, token caches, or private trading exports.
