---
description: On-chain data + DeFi protocol + market sentiment three-dimensional parallel analysis → Alpha synthesizer converges investment recommendations
argument-hint: [target] [timeframe]
---

# Crypto Asset Research Lab

Native replacement for the Vibe-Trading `crypto_research_lab` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Target asset (e.g.: BTC / ETH / SOL; default BTC/ETH/SOL)
- `<timeframe>` = `$2` — Analysis time horizon (short-term 1–4 weeks / medium-term 1–3 months / long-term 3–12 months)

## Phase 1 (parallel)
- **`crypto-research-lab-onchain-analyst`** — "Analyze on-chain data for <target>, including active addresses, holder distribution, exchange net flows, and MVRV/SOPR cycle indicators. Provide a <timeframe> on-chain directional signal."
- **`crypto-research-lab-defi-analyst`** — "Analyze the DeFi ecosystem related to <target>, including TVL trends, lending rates, liquidity depth, and protocol revenues. Provide a <timeframe> DeFi-layer signal."
- **`crypto-research-lab-crypto-sentiment-analyst`** — "Analyze market sentiment for <target>, including funding rates, open interest, fear & greed index, and options market structure. Provide a <timeframe> sentiment-based timing signal."

## Phase 2
- **`crypto-research-lab-alpha-synthesizer`** — "Integrate the on-chain, DeFi, and sentiment three-dimensional analyses for <target> and provide a composite <timeframe> investment recommendation with position allocation."
  - Provide as `onchain`: the **On-Chain Data Analyst** (`crypto-research-lab-onchain-analyst`) output from an earlier phase.
  - Provide as `defi`: the **DeFi Protocol Analyst** (`crypto-research-lab-defi-analyst`) output from an earlier phase.
  - Provide as `sentiment`: the **Crypto Sentiment Analyst** (`crypto-research-lab-crypto-sentiment-analyst`) output from an earlier phase.

## Final output
Return the **Alpha Synthesizer** output as the team's deliverable, citing the supporting analysis from earlier phases.
