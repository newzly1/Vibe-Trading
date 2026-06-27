---
description: ETF screening + macro allocation + risk budgeting three-dimensional parallel analysis → portfolio optimizer constructs the final ETF portfolio and backtests
argument-hint: [risk_profile] [market]
---

# ETF Allocation Desk

Native replacement for the Vibe-Trading `etf_allocation_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<risk_profile>` = `$1` — Risk profile (conservative / balanced / aggressive)
- `<market>` = `$2` — Target market (default: A-shares; options: global multi-asset, HK/US equities, A-shares + HK)

## Phase 1 (parallel)
- **`etf-allocation-desk-etf-screener`** — "In the <market> market, screen high-quality ETF candidates across major asset classes for investors with a <risk_profile> risk profile."
- **`etf-allocation-desk-macro-allocator`** — "Based on the current economic cycle and macro environment, develop cross-asset class allocation weight recommendations for <market> suited for investors with a <risk_profile> risk profile."
- **`etf-allocation-desk-risk-budgeter`** — "Compute risk budgets and weight constraints for each asset class for a <market> ETF portfolio suited for investors with a <risk_profile> risk profile."

## Phase 2
- **`etf-allocation-desk-portfolio-optimizer`** — "Synthesize the ETF screening, macro allocation, and risk budget inputs to construct a final ETF portfolio for investors with a <risk_profile> risk profile in the <market> market, and validate through backtesting."
  - Provide as `etf_candidates`: the **ETF Screener** (`etf-allocation-desk-etf-screener`) output from an earlier phase.
  - Provide as `macro_allocation`: the **Macro Allocator** (`etf-allocation-desk-macro-allocator`) output from an earlier phase.
  - Provide as `risk_budget`: the **Risk Budgeter** (`etf-allocation-desk-risk-budgeter`) output from an earlier phase.

## Final output
Return the **Portfolio Optimizer** output as the team's deliverable, citing the supporting analysis from earlier phases.
