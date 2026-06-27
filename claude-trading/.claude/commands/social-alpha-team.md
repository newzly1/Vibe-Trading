---
description: Twitter, Telegram, and Reddit analyzed in parallel → Alpha synthesizer extracts tradable social sentiment factors.
argument-hint: [target] [timeframe]
---

# Social-Media Alternative Data Team

Native replacement for the Vibe-Trading `social_alpha_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Focus name or market (e.g. BTC, Tesla, A-share tech, Nasdaq)
- `<timeframe>` = `$2` — Horizon (real-time / daily / weekly)

## Phase 1 (parallel)
- **`social-alpha-team-twitter-analyst`** — "Analyze FinTwit on "<target>": KOL views, topic heat, sentiment extremes. Horizon: <timeframe>."
- **`social-alpha-team-telegram-analyst`** — "Analyze Telegram crypto/quant channels on "<target>": signal quality, heat, alpha clues. Horizon: <timeframe>."
- **`social-alpha-team-reddit-analyst`** — "Analyze Reddit (WSB/investing/crypto) on "<target>": hot names, options anomalies, retail sentiment. Horizon: <timeframe>."

## Phase 2
- **`social-alpha-team-alpha-synthesizer`** — "Synthesize Twitter/Telegram/Reddit into social-media alpha for "<target>": build factors and validate. Horizon: <timeframe>."
  - Provide as `twitter_report`: the **Twitter Analyst** (`social-alpha-team-twitter-analyst`) output from an earlier phase.
  - Provide as `telegram_report`: the **Telegram Analyst** (`social-alpha-team-telegram-analyst`) output from an earlier phase.
  - Provide as `reddit_report`: the **Reddit Analyst** (`social-alpha-team-reddit-analyst`) output from an earlier phase.

## Final output
Return the **Alpha Synthesizer** output as the team's deliverable, citing the supporting analysis from earlier phases.
