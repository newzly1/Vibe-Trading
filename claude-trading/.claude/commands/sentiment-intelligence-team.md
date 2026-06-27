---
description: News intel / social sentiment / capital flows in parallel → sentiment signal synthesizer outputs composite score and reversal signals.
argument-hint: [market] [timeframe]
---

# Market Sentiment Intelligence Unit

Native replacement for the Vibe-Trading `sentiment_intelligence_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market, e.g. A-shares / HK / US / crypto / CSI 300
- `<timeframe>` = `$2` — Horizon: daily or weekly

## Phase 1 (parallel)
- **`sentiment-intelligence-team-news-analyst`** — "Analyze <market> at <timeframe>: finance news, policy, sell-side summaries. Output news sentiment −100..+100, key events, policy phase."
- **`sentiment-intelligence-team-social-analyst`** — "Analyze <market> at <timeframe>: social sentiment, fear/greed, retail behavior, extremes. Output social score and extreme alerts."
- **`sentiment-intelligence-team-flow-analyst`** — "Analyze <market> at <timeframe>: main / Northbound / margin / block / dragon-tiger flows. Output flow score and smart-money signals."

## Phase 2
- **`sentiment-intelligence-team-signal-synthesizer`** — "Merge news, social, and flow for <market> <timeframe>: composite score, percentile calibration, reversal call, position advice."
  - Provide as `news_sentiment`: the **News Intelligence Analyst** (`sentiment-intelligence-team-news-analyst`) output from an earlier phase.
  - Provide as `social_sentiment`: the **Social Sentiment Analyst** (`sentiment-intelligence-team-social-analyst`) output from an earlier phase.
  - Provide as `flow_sentiment`: the **Capital Flow Analyst** (`sentiment-intelligence-team-flow-analyst`) output from an earlier phase.

## Final output
Return the **Sentiment Signal Synthesizer** output as the team's deliverable, citing the supporting analysis from earlier phases.
