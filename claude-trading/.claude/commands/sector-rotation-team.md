---
description: Economic cycle + prosperity + capital flows in parallel → rotation strategist builds and backtests a sector rotation strategy.
argument-hint: [market] [goal]
---

# Sector Rotation Research Team

Native replacement for the Vibe-Trading `sector_rotation_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (default A-shares; can specify HK/US)
- `<goal>` = `$2` — Focus theme (e.g. new energy, tech growth, high dividend, exporters)

## Phase 1 (parallel)
- **`sector-rotation-team-cycle-analyst`** — "Judge <market> economic cycle phase and sector tilts. Focus: <goal>."
- **`sector-rotation-team-prosperity-analyst`** — "Rank <market> sector prosperity and value-for-prosperity. Focus: <goal>."
- **`sector-rotation-team-flow-analyst`** — "Analyze <market> sector flows—accumulation vs distribution. Focus: <goal>."

## Phase 2
- **`sector-rotation-team-rotation-strategist`** — "Merge cycle, prosperity, flows into a <market> rotation strategy and backtest. Focus: <goal>."
  - Provide as `cycle_analysis`: the **Economic Cycle Analyst** (`sector-rotation-team-cycle-analyst`) output from an earlier phase.
  - Provide as `prosperity_analysis`: the **Sector Prosperity Analyst** (`sector-rotation-team-prosperity-analyst`) output from an earlier phase.
  - Provide as `flow_analysis`: the **Capital Flow Analyst** (`sector-rotation-team-flow-analyst`) output from an earlier phase.

## Final output
Return the **Sector Rotation Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
