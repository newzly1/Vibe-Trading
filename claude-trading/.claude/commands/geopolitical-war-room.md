---
description: Geopolitical analysis, energy shock, and supply-chain impact run in parallel, then feed into the Chief Strategist for synthesis, producing emergency asset-allocation playbooks for geopolitical crises.
argument-hint: [crisis] [market]
---

# Geopolitical Risk War Room

Native replacement for the Vibe-Trading `geopolitical_war_room` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<crisis>` = `$1` — Crisis narrative (e.g., Taiwan Strait escalation, Hormuz blockade, full Red Sea Houthi disruption)
- `<market>` = `$2` — Focus market (e.g., A-shares, Hong Kong, global multi-asset)

## Phase 1 (parallel)
- **`geopolitical-war-room-geopolitical-analyst`** — "Analyze geopolitical risk for crisis scenario "<crisis>": rate six hotspots, track GPR Index, with focus on <market>."
- **`geopolitical-war-room-energy-analyst`** — "Assess energy impact of crisis "<crisis>", quantify war risk premium and oil/gas disruption odds, with focus on <market>."
- **`geopolitical-war-room-supply-chain-analyst`** — "Analyze global supply-chain impact (semis/rare earths/shipping/food) of crisis "<crisis>", identify affected industries and companies in <market>."

## Phase 2
- **`geopolitical-war-room-chief-strategist`** — "Synthesize all three streams and craft emergency geopolitical-risk allocation and hedging for <market> under crisis "<crisis>"."
  - Provide as `geopolitical_report`: the **Geopolitical Analyst** (`geopolitical-war-room-geopolitical-analyst`) output from an earlier phase.
  - Provide as `energy_report`: the **Energy Shock Analyst** (`geopolitical-war-room-energy-analyst`) output from an earlier phase.
  - Provide as `supply_chain_report`: the **Supply Chain Analyst** (`geopolitical-war-room-supply-chain-analyst`) output from an earlier phase.

## Final output
Return the **Chief Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
