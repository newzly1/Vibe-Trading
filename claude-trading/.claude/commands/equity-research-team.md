---
description: Macro → sector → stock three-tier deep research → research editor consolidates into a complete report
argument-hint: [market] [goal]
---

# Equity Research Team

Native replacement for the Vibe-Trading `equity_research_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (e.g.: A-shares, Hong Kong, Crypto)
- `<goal>` = `$2` — Research focus (e.g.: Q2 2026 outlook, opportunities in the new energy sector)

## Phase 1
- **`equity-research-team-macro-analyst`** — "Analyze the current macroeconomic environment and its impact on the <market> market, with a focus on <goal>."

## Phase 2
- **`equity-research-team-sector-analyst`** — "Based on the macro analysis, identify the most promising sectors in <market>."
  - Provide as `macro_context`: the **Macro Analyst** (`equity-research-team-macro-analyst`) output from an earlier phase.

## Phase 3
- **`equity-research-team-stock-picker`** — "Screen specific targets from the recommended sectors and conduct technical and fundamental analysis."
  - Provide as `sector_context`: the **Sector Analyst** (`equity-research-team-sector-analyst`) output from an earlier phase.
  - Provide as `macro_context`: the **Macro Analyst** (`equity-research-team-macro-analyst`) output from an earlier phase.

## Phase 4
- **`equity-research-team-aggregator`** — "Synthesize all analyst reports and produce a complete investment research report."
  - Provide as `macro`: the **Macro Analyst** (`equity-research-team-macro-analyst`) output from an earlier phase.
  - Provide as `sector`: the **Sector Analyst** (`equity-research-team-sector-analyst`) output from an earlier phase.
  - Provide as `stock`: the **Stock Analyst** (`equity-research-team-stock-picker`) output from an earlier phase.

## Final output
Return the **Research Report Editor** output as the team's deliverable, citing the supporting analysis from earlier phases.
