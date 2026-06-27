---
description: Event scanning → deep impact analysis → strategy construction: sequential deep-dive chain replicating an event-driven hedge fund special investigation unit workflow
argument-hint: [market] [event_type]
---

# Event-Driven Task Force

Native replacement for the Vibe-Trading `event_driven_task_force` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market, e.g.: A-shares / Hong Kong / US equities / Chinese ADRs
- `<event_type>` = `$2` — Event type filter, e.g.: M&A / insider trading / earnings / policy / litigation / management change; enter 'all types' for no filter

## Phase 1
- **`event-driven-task-force-event-scanner`** — "Scan for major corporate events in the <market> market, focusing on event types: <event_type> (cover all types if blank). Output a quality-filtered list of 10–15 events with materiality ratings and event cluster analysis."

## Phase 2
- **`event-driven-task-force-impact-analyst`** — "Conduct deep impact analysis on high / medium-rated events from the scan list: assess fundamental impact, market pricing status, historical CAR statistics. Output the event impact matrix and Top 5 tradeable event recommendations."
  - Provide as `event_list`: the **Event Scout** (`event-driven-task-force-event-scanner`) output from an earlier phase.

## Phase 3
- **`event-driven-task-force-strategy-builder`** — "Design complete trading strategies for the impact analyst's Top 5 tradeable events: entry conditions, position management, exit rules, stop-loss framework, and backtest validation of strategy performance under historically similar events."
  - Provide as `impact_analysis`: the **Impact Analyst** (`event-driven-task-force-impact-analyst`) output from an earlier phase.
  - Provide as `event_list`: the **Event Scout** (`event-driven-task-force-event-scanner`) output from an earlier phase.

## Final output
Return the **Strategy Builder** output as the team's deliverable, citing the supporting analysis from earlier phases.
