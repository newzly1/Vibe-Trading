---
description: Parallel deep-dive on supply and demand, synthesized by a cycle strategist into an investment thesis — DAG workflow
argument-hint: [commodity] [horizon]
---

# Commodity Research Team

Native replacement for the Vibe-Trading `commodity_research_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<commodity>` = `$1` — Commodity type, e.g.: crude oil / gold / copper / iron ore / natural gas / soybeans / aluminum / rebar
- `<horizon>` = `$2` — Investment horizon, e.g.: 1 month / 3 months / 6 months / 1 year

## Phase 1 (parallel)
- **`commodity-research-team-supply-analyst`** — "Conduct a comprehensive supply-side analysis of <commodity>: production landscape, inventory cycle, capacity utilization, OPEC policy or mine output, supply disruption risks, and cost curve. Output a supply tightness score and inventory cycle assessment to inform a <horizon> investment strategy."
- **`commodity-research-team-demand-analyst`** — "Conduct a comprehensive demand-side analysis of <commodity>: downstream demand structure, leading macro indicators, China demand tracking, seasonal patterns, and structural energy-transition demand. Output a demand strength score and seasonality calendar to inform a <horizon> investment strategy."

## Phase 2
- **`commodity-research-team-cycle-strategist`** — "Synthesize the supply and demand research to construct a supply-demand balance sheet for <commodity>, identify the commodity cycle phase, overlay seasonal timing, and develop a complete cycle investment strategy for a <horizon> horizon. Output investment recommendations, price range forecasts, and optimal entry windows."
  - Provide as `supply_analysis`: the **Supply Analyst** (`commodity-research-team-supply-analyst`) output from an earlier phase.
  - Provide as `demand_analysis`: the **Demand Analyst** (`commodity-research-team-demand-analyst`) output from an earlier phase.

## Final output
Return the **Cycle Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
