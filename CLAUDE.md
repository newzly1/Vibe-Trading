# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code Integration: Vibe-Trading Financial Analysis

Vibe-Trading's core financial analysis capabilities have been ported to Claude Code, bypassing V-T's own ReAct agent loop and using Claude Code's native reasoning for financial analysis.

### Capability Overview

| Capability | Vehicle | Purpose |
|------------|---------|---------|
| Domain knowledge | 77 `.claude/skills/vt-*` skills | Formulas, parameters, methodology reference (auto-discovered, loaded on demand) |
| Data + computation | MCP tools (43, via `.mcp.json`) | Market data, backtesting, factor analysis, Alpha Zoo, options pricing, hypothesis registry, etc. |
| Parallel analysis | `vt-swarm-*` skills + `.claude/workflows/` + `Agent` tool | Replaces V-T's Swarm multi-agent framework (3 presets ported, 25 remaining) |
| Code execution | `Bash` tool | Run Python scripts for custom computation |

### MCP Tools Quick Reference

Connected via `.mcp.json` to the `vibe-trading-mcp` server, exposing 43 tools:

**Market data**: `get_market_data` — fetch OHLCV (A-shares / HK / US / crypto). For A-shares, explicitly specify `source="akshare"` or `source="tushare"`; do not rely on `source="auto"`.

**Backtesting & analysis**: `backtest` (requires a pre-prepared directory with `config.json` + `code/signal_engine.py`), `factor_analysis` (factor IC/return analysis), `analyze_options` (options pricing & Greeks), `pattern_recognition` (candlestick pattern recognition).

**Alpha Zoo**: `alpha_zoo` (browse/list/get 452 pre-built alphas), `alpha_bench` (batch benchmark a zoo — IC mean/std/IR/positive-ratio + HTML report), `alpha_compare` (head-to-head ranking of named alphas by IC metric).

**Content tools**: `read_url`, `read_document`, `web_search`, `read_file`, `write_file`.

**Trading connections**: `trading_connections`, `trading_select_connection`, `trading_check`, `trading_account`, `trading_positions`, `trading_orders`, `trading_quote`, `trading_history`.

**Research goals**: `start_research_goal`, `get_research_goal`, `add_goal_evidence`, `update_research_goal_status`.

**Hypothesis registry**: `create_hypothesis`, `update_hypothesis`, `link_backtest` (attach run cards), `search_hypotheses` (text search by status/query).

**Other**: `list_skills`, `load_skill`, `list_runs`, `get_run_result`, `list_swarm_presets`, `run_swarm`, `get_swarm_status`, `reap_stale_runs`, `retry_run`, `analyze_trade_journal`, `extract_shadow_strategy`, `run_shadow_backtest`, `render_shadow_report`, `scan_shadow_signals`.

### Skill Usage Guide

77 `vt-*` skills are installed at `.claude/skills/`. Claude Code auto-discovers them at startup and injects one-line summaries into the system prompt. When a task touches a specific financial domain, the corresponding SKILL.md is auto-loaded as context.

**Skills are knowledge documents, not executable code** — they provide formulas, parameters, and methodology references. Actual computation still requires MCP tools or Bash-executed Python.

### Key Usage Patterns

1. **Fetch → analyze → backtest** pipeline: call MCP tools directly in sequence; no agent loop needed.
2. **Swarm replacement (Skills + Workflows)**: V-T's 28 Swarm presets are being ported as `vt-swarm-*` skills (knowledge) + `.claude/workflows/*.js` (deterministic orchestration). 3 presets ported so far — see [Swarm Replacement](#swarm-replacement-skills--workflows) below. Do NOT use `run_swarm`.
3. **Skill guidance + MCP execution**: consult the relevant vt-* skill for methodology first, then execute computation via MCP tools.
4. **Data first, always**: Before any analysis, call `get_market_data` with explicit `source` (A-shares: `source="akshare"`). Never substitute WebSearch for real market data — WebSearch is for qualitative context only.

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
- The 77 skills are knowledge documents, not executable code.

---

## Project Architecture (Vibe-Trading Codebase)

The sections below describe the repo's own architecture, for reference when modifying code, maintaining the MCP server, or extending skills.

### Package Layout

`pyproject.toml` maps `package-dir = {"" = "agent"}` — **`agent/` is the Python package root**. Inside it, `src/`, `backtest/`, and `cli/` are top-level packages. CLI entry points: `vibe-trading` → `cli:main`, `vibe-trading-mcp` → `mcp_server:main`.

### Essential Commands

```bash
# Install
pip install -e ".[dev]"

# Full test suite (exclude e2e and live-LLM tests)
pytest --ignore=agent/tests/e2e_backtest --ignore=agent/tests/test_e2e_harness_v2.py --tb=short -q

# Alpha zoo gates only
pytest agent/tests/factors/test_alpha_purity.py agent/tests/factors/test_lookahead.py -q

# Live trading safety tests
pytest agent/tests/test_sdk_order_gate.py agent/tests/test_mandate_enforcement.py agent/tests/test_killswitch_blocks_orders.py agent/tests/test_readonly_default.py -q

# Syntax check (run before tests)
cd agent && python -m compileall -q cli && python -m py_compile api_server.py mcp_server.py

# Frontend
cd frontend && npm ci && npm run build      # build
cd frontend && npx vitest run               # test
cd frontend && npm run dev                   # dev server (port 5899)

# Lint
ruff check agent/

# Docker
docker compose up --build
```

### MCP Server (`agent/mcp_server.py`)

Built on `fastmcp`. Exposes V-T's tool registry as MCP tools via stdio (default) or SSE transport. Tools are read from the auto-discovery mechanism in `agent/src/tools/` — no manual registration needed.

**Adding a new MCP tool**:
1. Create a file in `agent/src/tools/` with a class extending `BaseTool`
2. Set a non-empty `name`, implement `execute(**kwargs) -> str` (return JSON)
3. Optional: implement `check_available() -> False` to silently skip tools with missing deps
4. Restart the MCP server for the new tool to take effect

### Skills System (`agent/src/skills/`)

76+ bundled financial analysis skills. Each skill is a directory under `agent/src/skills/<name>/` containing at minimum a `SKILL.md` with frontmatter (name, description, category).

**Loading mechanism** (progressive disclosure): the system prompt injects only one-line summaries (`get_descriptions()`), and full documentation is loaded on demand by the `load_skill` tool (`get_content()`). The loader lives in `agent/src/agent/skills.py` (`SkillsLoader` class).

**Converting a V-T skill to a Claude Code skill**:
1. Copy `agent/src/skills/<name>/SKILL.md` to `.claude/skills/vt-<name>/SKILL.md`
2. Replace `load_skill("xxx")` references with cross-skill links (`See the **vt-xxx** skill guide`)
3. Inject the available MCP tool list at the top (HTML comment — visible to Claude, hidden from user)

### Tool Auto-Discovery (`agent/src/tools/__init__.py`)

**No manual registration.** Tools are discovered by scanning `BaseTool.__subclasses__()`. `build_registry()` wires local tools first, then optionally appends MCP tools from `AgentConfig.mcp_servers`. Shell tools, goal tools, and swarm tools receive special constructor injection (persistent memory, session_id, event_callbacks). Live-broker MCP channels route through the `trading_*` connector surface, not raw `mcp_<broker>_*` wrappers.

### Alpha Zoo / Factors (`agent/src/factors/`)

452 pre-built cross-sectional alphas across 4 zoos under `zoo/`:
- `alpha101/` — Kakushadze 101 Formulaic Alphas
- `gtja191/` — Guotai Junan 2014 short-horizon factors
- `qlib158/` — Microsoft Qlib (Apache-2.0 attributed)
- `academic/` — Fama-French 5 + Carhart price-based proxies

**Architecture**: `registry.py` AST-scans zoo modules to extract `__alpha_meta__` dicts (Pydantic-validated) without importing code. Each alpha file defines `__alpha_meta__` (id, theme, formula_latex, columns_required, universe, frequency, etc.) and a pure `compute(panel) -> DataFrame` function. **Purity gate** (`test_alpha_purity.py`) AST-scans for forbidden imports — only `pandas`, `numpy`, `scipy.*`, and `src.factors.base` are allowed. **Lookahead gate** (`test_lookahead.py`) verifies no forward leakage. `bench_runner.py` evaluates zoos via IC/IR; `compare_runner.py` does head-to-head comparisons with subset filtering.

### Backtest System (`agent/backtest/`)

- **`runner.py`**: Entry point that reads `config.json` from a run directory, resolves the loader, imports the signal engine, and runs the backtest.
- **`loaders/`**: DataLoader Protocol with 7 sources (tushare, yfinance, okx, ccxt, akshare, mootdx, futu) and auto-fallback chains.
- **`engines/`**: 7 asset-class engines + `CompositeEngine` (cross-market with shared capital pool) + options portfolio engine. Market detection lives in `engines/_market_hooks.py`.
- **`optimizers/`**: 4 portfolio optimizers (mean_variance, risk_parity, equal_volatility, max_diversification).
- Config validation uses Pydantic (`BacktestConfigSchema`). The `--interval` flag supports `1m`/`5m`/`15m`/`30m`/`1H`/`4H`/`1D`.

### Trading Connectors (`agent/src/trading/connectors/`)

10 broker connectors: ibkr, robinhood, alpaca, binance, okx, futu, tiger, longbridge, dhan, shoonya. Connector-first design: users select a profile, and all `trading_*` tools route through it. Paper/live is a structural per-broker attribute (account-id format, host, demo flag, trade environment). Brokers without a runtime paper/live discriminator (Longbridge, Dhan, Shoonya) are capped at paper + read-only.

### Live Trading Safety (`agent/src/live/`)

All broker order paths pass through: mandate (symbol universe, size, exposure, leverage, daily cap) → kill switch (filesystem, instant halt) → pre-trade order guard (fail-closed) → audit ledger. The mandate is read-only at the agent loop — no write path reachable from a tool. The **runtime** subsystem (`live/runtime/`) provides a persistent autonomous scheduler with a durable crash-safe job store, runner liveness monitoring, trade reconciliation, preemptive halt, and position flattening.

### Swarm (`agent/src/swarm/`)

DAG execution engine with YAML-defined presets. `runtime.py` orchestrates workers, each with a filtered tool registry. Status reconciles from live task files (crash recovery). **Not recommended in the Claude Code integration** — use `dispatching-parallel-agents` + `Agent` tool instead.

### Other Packages

- **`agent/src/hypotheses/`** — Durable research hypothesis registry with status tracking and backtest linking.
- **`agent/src/memory/`** — Persistent cross-session memory with FTS search and CJK-safe slugs.
- **`agent/src/shadow_account/`** — Extracts trading patterns from user broker statements; generates PDF reports via Jinja2 + WeasyPrint.
- **`agent/src/goal/`** — Research goal runtime: persistent objectives with criteria, evidence, claims, and completion policy.
- **`agent/src/security/`** — Path containment, secret redaction, and sandbox enforcement.

### API Server (`agent/api_server.py`)

FastAPI server (~3100 LOC) serving the React frontend as static files plus REST API routes: agent chat, runs, sessions, alpha bench/compare, swarm, settings, correlation, uploads, goals, hypotheses. SPA deep-link support for `/runs/{id}` and `/correlation`. SSE event streaming for real-time agent progress.

### Frontend (`frontend/`)

React 19 + Vite + TypeScript + Tailwind CSS. Zustand for state management (`stores/agent.ts` is the main agent store). ECharts for charts. React Router v7 with pages: Agent (chat), AlphaZoo, RunDetail, Compare, Correlation, Home, Settings. The Vite dev server proxies `/api`, `/runs`, `/sessions`, `/alpha`, `/swarm`, `/settings`, `/uploads`, `/correlation` to `localhost:8899`.

### Session Layer (`agent/src/session/`)

Multi-turn chat stored as JSONL files with `flush + fsync` on each append for crash safety. FTS5-backed cross-session search. SSE event streaming via `sse-starlette`. Corrupted JSONL lines are skipped with first-200-char logging.

### CLI (`agent/cli/`)

Interactive REPL with Rich-based rendering, slash-command router, `prompt_toolkit` input (with readline fallback), live status bar, and progress indicators. Subcommands: `chat`, `alpha bench/compare`, `connector`, `swarm`, `goal`, `hypothesis`, `memory`, `provider login`, `serve`.

### LLM Provider System (`agent/src/providers/`)

Multi-provider support registered in `llm_providers.json`. Each provider entry defines: name, label, `api_key_env` / `base_url_env`, `default_model`, `default_base_url`, and optional `auth_type` (api_key or oauth). The `llm.py` module wraps langchain, handling provider-specific quirks (e.g., Gemini `thought_signature` round-tripping for multi-turn tool calls). OpenAI Codex uses ChatGPT OAuth via `vibe-trading provider login openai-codex`.

### Config System (`agent/src/config/`)

Pydantic-based schema for `~/.vibe-trading/agent.json`. Validates MCP server entries, detects live-broker URLs by host suffix (not config key) to prevent bypass, and enforces wildcard-tool rejection for live brokers.

### Docker

Multi-stage build: Node 20 frontend build → Python 3.11-slim runtime. Runs as non-root user `vibe` with healthcheck on `/health`. Port 8899 (bound to loopback by default). Two named volumes (`vibe-runs`, `vibe-sessions`). `VIBE_TRADING_TRUST_DOCKER_LOOPBACK=1` skips `API_AUTH_KEY` for Docker Desktop host-gateway connections.

## Key Environment Variables

| Variable | Role |
|----------|------|
| `LANGCHAIN_PROVIDER` | LLM provider name (openrouter, deepseek, groq, ollama, etc.) |
| `<PROVIDER>_API_KEY` / `<PROVIDER>_BASE_URL` | Per-provider credentials |
| `LANGCHAIN_MODEL_NAME` | Model name |
| `API_AUTH_KEY` | Required for non-loopback API access |
| `VIBE_TRADING_ENABLE_SHELL_TOOLS` | Opt-in for shell tools in remote deployments |
| `VIBE_TRADING_DATA_CACHE` | Opt-in local data caching (`~/.vibe-trading/cache`) |
| `TUSHARE_TOKEN` | Optional A-share data token (falls back to mootdx/AKShare) |

## Test Organization

Tests live in `agent/tests/`. `conftest.py` provides shared fixtures. Test files are named by feature (not by source module). Key markers: `@pytest.mark.unit` (fast, no network), `@pytest.mark.integration` (may need network). `test_e2e_harness_v2.py` is gated behind `VIBE_TRADING_RUN_LIVE_E2E=1` (real LLM calls).

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
