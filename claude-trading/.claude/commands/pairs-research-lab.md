---
description: Correlation scan and cointegration testing in parallel → converge into the pair strategist for strategy design → final microstructure review for execution feasibility.
argument-hint: [market] [sector]
---

# Pairs Trading Research Lab

Native replacement for the Vibe-Trading `pairs_research_lab` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (e.g. A-shares, Hong Kong, US, crypto)
- `<sector>` = `$2` — Sector filter (e.g. banks, consumer, semis); empty = full market

## Phase 1 (parallel)
- **`pairs-research-lab-correlation-scanner`** — "Scan <market> (<sector> sector; empty = full market) for highly correlated pairs—comovement and sector clustering."
- **`pairs-research-lab-cointegration-tester`** — "Strict cointegration tests on <market> pair candidates (<sector> constraint); half-life and dynamic hedge; keep significant pairs."

## Phase 2
- **`pairs-research-lab-pair-strategist`** — "Integrate correlation and cointegration; design full pair strategy for <market> (<sector>) and backtest."
  - Provide as `correlation_report`: the **Correlation Scanner** (`pairs-research-lab-correlation-scanner`) output from an earlier phase.
  - Provide as `cointegration_report`: the **Cointegration Tester** (`pairs-research-lab-cointegration-tester`) output from an earlier phase.

## Phase 3
- **`pairs-research-lab-microstructure-reviewer`** — "Microstructure review of <market> (<sector>) pair strategy—feasibility, costs, liquidity limits."
  - Provide as `strategy_report`: the **Pair Strategist** (`pairs-research-lab-pair-strategist`) output from an earlier phase.
  - Provide as `correlation_report`: the **Correlation Scanner** (`pairs-research-lab-correlation-scanner`) output from an earlier phase.
  - Provide as `cointegration_report`: the **Cointegration Tester** (`pairs-research-lab-cointegration-tester`) output from an earlier phase.

## Final output
Return the **Microstructure Reviewer** output as the team's deliverable, citing the supporting analysis from earlier phases.
