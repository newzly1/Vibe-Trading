---
description: Execution-oriented crypto desk: funding/basis analyst + liquidation/microstructure analyst + on-chain/flow analyst + risk manager. Goes beyond research into position sizing, execution timing, and risk gating.
argument-hint: [target] [timeframe]
---

# Crypto Trading & Risk Desk

Native replacement for the Vibe-Trading `crypto_trading_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Target asset (e.g., BTC-USDT, ETH-USDT, SOL-USDT)
- `<timeframe>` = `$2` — Trading horizon (intraday / swing 1-2 weeks / position 1-3 months)

## Phase 1 (parallel)
- **`crypto-trading-desk-funding-basis-analyst`** — "Analyze funding rates, basis structure, and carry opportunities for <target>. Timeframe: <timeframe>."
- **`crypto-trading-desk-liquidation-analyst`** — "Map liquidation levels, cascade risks, and microstructure conditions for <target>. Timeframe: <timeframe>."
- **`crypto-trading-desk-flow-analyst`** — "Analyze stablecoin flows, on-chain positioning, and capital rotation signals for <target>. Timeframe: <timeframe>."

## Phase 2
- **`crypto-trading-desk-desk-risk-manager`** — "Integrate all desk analyses and deliver an executable trading plan for <target> with position sizing and risk gates. Timeframe: <timeframe>."
  - Provide as `funding_basis`: the **Funding Rate & Basis Analyst** (`crypto-trading-desk-funding-basis-analyst`) output from an earlier phase.
  - Provide as `liquidation_micro`: the **Liquidation & Microstructure Analyst** (`crypto-trading-desk-liquidation-analyst`) output from an earlier phase.
  - Provide as `flow_analysis`: the **On-Chain & Stablecoin Flow Analyst** (`crypto-trading-desk-flow-analyst`) output from an earlier phase.

## Final output
Return the **Trading Desk Risk Manager** output as the team's deliverable, citing the supporting analysis from earlier phases.
