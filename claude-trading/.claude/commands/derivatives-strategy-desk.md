---
description: Volatility analysis → strategy design → Greeks risk management: sequential options trading desk workflow
argument-hint: [target] [view]
---

# Derivatives Strategy Desk

Native replacement for the Vibe-Trading `derivatives_strategy_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Underlying (e.g.: BTC, CSI 300 ETF, AAPL)
- `<view>` = `$2` — Market view (bullish / bearish / neutral / long volatility / short volatility)

## Phase 1
- **`derivatives-strategy-desk-vol-analyst`** — "Analyze the historical volatility, implied volatility surface, term structure, and skew of <target> to provide a volatility environment assessment for options strategy design."

## Phase 2
- **`derivatives-strategy-desk-strategy-designer`** — "Based on the volatility analysis of <target> and the market view '<view>', design the optimal options combination strategy and specify all contract details."
  - Provide as `vol_context`: the **Volatility Analyst** (`derivatives-strategy-desk-vol-analyst`) output from an earlier phase.

## Phase 3
- **`derivatives-strategy-desk-greeks-manager`** — "Conduct Greeks risk quantification, scenario analysis, and stress testing for the <target> options strategy, and provide dynamic adjustment recommendations."
  - Provide as `strategy_context`: the **Strategy Designer** (`derivatives-strategy-desk-strategy-designer`) output from an earlier phase.
  - Provide as `vol_context`: the **Volatility Analyst** (`derivatives-strategy-desk-vol-analyst`) output from an earlier phase.

## Final output
Return the **Greeks Risk Manager** output as the team's deliverable, citing the supporting analysis from earlier phases.
