---
description: Pair scanning and microstructure analysis in parallel → converge into the arbitrage strategist to build the strategy → final risk-control review.
argument-hint: [market] [goal] [sector]
---

# Statistical Arbitrage Desk

Native replacement for the Vibe-Trading `statistical_arbitrage_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (e.g. A-shares, Hong Kong, crypto)
- `<goal>` = `$2` — Research focus (e.g. CSI 300 pair book, crypto arb ideas)
- `<sector>` = `$3` — Sector filter (e.g. banks, consumer); empty = full market

## Phase 1 (parallel)
- **`statistical-arbitrage-desk-pair-scanner`** — "Scan <market> for stat-arb pairs (<sector> sector constraint). Focus: <goal>."
- **`statistical-arbitrage-desk-microstructure-analyst`** — "Analyze microstructure and trading costs for candidate pairs in <market>. Focus: <goal>."

## Phase 2
- **`statistical-arbitrage-desk-arb-strategist`** — "Integrate pair scan and microstructure work; design and backtest a <market> stat-arb strategy. Focus: <goal>."
  - Provide as `pair_scan_result`: the **Pair Scanner** (`statistical-arbitrage-desk-pair-scanner`) output from an earlier phase.
  - Provide as `microstructure_report`: the **Microstructure Analyst** (`statistical-arbitrage-desk-microstructure-analyst`) output from an earlier phase.

## Phase 3
- **`statistical-arbitrage-desk-risk-monitor`** — "Full risk review of the <market> stat-arb strategy. Focus: <goal>."
  - Provide as `strategy_report`: the **Arbitrage Strategist** (`statistical-arbitrage-desk-arb-strategist`) output from an earlier phase.
  - Provide as `pair_scan_result`: the **Pair Scanner** (`statistical-arbitrage-desk-pair-scanner`) output from an earlier phase.
  - Provide as `microstructure_report`: the **Microstructure Analyst** (`statistical-arbitrage-desk-microstructure-analyst`) output from an earlier phase.

## Final output
Return the **Risk Monitor** output as the team's deliverable, citing the supporting analysis from earlier phases.
