export const meta = {
  name: 'investment-committee',
  description: 'Investment Committee — parallel bull/bear debate → risk review → PM final decision. Native Claude Code replacement for run_swarm("investment_committee").',
  phases: [
    { title: 'Debate', detail: 'Parallel bull and bear research' },
    { title: 'Risk Review', detail: 'CRO reviews both cases independently' },
    { title: 'Decision', detail: 'PM synthesizes and makes final call' },
  ],
  whenToUse: 'When the user asks for a multi-perspective investment analysis on a specific stock or crypto, wants a bull vs bear debate, or says "investment committee" / "投委会" / "多空辩论".',
}

const TARGET = args.target
const MARKET = args.market || 'A-shares'

// ============================================================
// Phase 1: Parallel bull + bear research
// ============================================================
phase('Debate')

const BULL_PROMPT = `You are a senior bull-side researcher at a buy-side fund. Your mission is to systematically identify upside drivers for ${TARGET} (market: ${MARKET}) and build a strong long thesis.

## Analysis Dimensions

### Technical Analysis
- Use load_skill("technical-basic") for methodology
- Check MA stack (MA5/20/60/250), MACD golden cross / histogram compression, RSI regime
- Volume expansion on rallies (bullish volume confirmation)

### Fundamental Analysis
- Use load_skill("fundamental-filter") for framework
- PE/PB vs historical percentile and industry discount
- ROE/ROIC trends, FCF conversion, operating leverage
- Revenue/earnings growth, industry ceiling

### Sentiment & Positioning
- Use load_skill("sentiment-analysis") for methods
- Institutional positioning, northbound flows (A-shares)
- Analyst upgrades and target-price lifts

## Required Outputs (7 items)
1. **Bull thesis bullets** — 3-5 strongest bull points, each with confidence (high/medium)
2. **Technical detail** — All bullish signals with key levels (support, target)
3. **Fundamental upside** — Quantified valuation room, earnings leverage, core catalysts
4. **Sentiment & flow support** — Capital flows, institutional stance, sentiment cycle stage
5. **Catalyst calendar** — Specific events next 1-3 months that could drive upside
6. **Bull target prices** — Range from valuation re-rating, earnings growth, technical objectives
7. **Main risk to the bull case** — 2-3 scenarios that would invalidate the bull thesis

CRITICAL: Call get_market_data(codes="${TARGET}", source="akshare", ...) to fetch real data. For A-shares, use source="akshare" NOT "auto". Every specific price or number must be traceable to a tool call.`

const BEAR_PROMPT = `You are a senior bear-side researcher at a buy-side fund. Your mission is to systematically surface risks and build the bear case for ${TARGET} (market: ${MARKET}). Stay independent — challenge consensus.

## Analysis Dimensions

### Technical Risk
- Use load_skill("technical-basic") for methodology
- Key resistance, topping patterns (head-and-shoulders, double top)
- Bearish divergence: price new highs but MACD/RSI not
- Death cross, break of critical support

### Valuation Bubble
- Use load_skill("fundamental-filter") for framework
- PE/PB/PS vs historical percentile and industry premium
- DCF intrinsic value vs market price gap
- Red flags: goodwill, deferred revenue, receivables

### Fundamental Deterioration
- Structural drivers of margin decline
- Intensifying competition: entrants, price war, substitutes
- Debt load: leverage, interest coverage, refinancing risk

### Risk & Volatility
- Use load_skill("risk-analysis") and load_skill("volatility")
- Historical max drawdown; VaR/CVaR
- Beta vs market/industry; macro headwinds

## Required Outputs (7 items)
1. **Bear risk bullets** — 3-5 top bear points, each with severity (high/medium)
2. **Technical breakdown risk** — Topping patterns, divergences, resistance and stop levels
3. **Valuation bubble assessment** — Quantify premium vs fair value; downside target
4. **Fundamental deterioration evidence** — Concrete data for weakening quality
5. **Risk metrics** — VaR, expected max drawdown, downside under stress scenarios
6. **Bear target prices** — Downside range from multiple mean reversion and earnings cuts
7. **What would disprove the bear case** — Signals that invalidate the bear thesis

CRITICAL: Call get_market_data(codes="${TARGET}", source="akshare", ...) to fetch real data. For A-shares, use source="akshare" NOT "auto".`

const [bullResult, bearResult] = await parallel([
  () => agent(BULL_PROMPT, { label: 'bull_advocate', phase: 'Debate' }),
  () => agent(BEAR_PROMPT, { label: 'bear_advocate', phase: 'Debate' }),
])

// ============================================================
// Phase 2: Risk Officer review
// ============================================================
phase('Risk Review')

const RISK_PROMPT = `You are the Chief Risk Officer of a buy-side fund. Review the bull and bear arguments on ${TARGET} (market: ${MARKET}) independently.

## Bull Case
${bullResult || '(No bull report produced)'}

## Bear Case
${bearResult || '(No bear report produced)'}

## Review Framework

### Validity of Arguments
- Check bull side for confirmation bias (cherry-picking)
- Check bear side for emotion-driven excessive pessimism
- Identify blind-spot risks neither side covered
- Assess rigor of price-target methodology

### Position Risk Assessment
- Use load_skill("risk-analysis") and load_skill("volatility")
- From current vol, infer reasonable position upper bound (Kelly / fixed fraction)
- Liquidity: can ADV support rapid entry/exit at target size

### Tail Risk & Extreme Scenarios
- Three stress scenarios: base / bearish / extreme bear
- Potential loss under tail events
- Stop discipline: recommended stop levels and triggers

## Required Outputs (7 items)
1. **Risk review conclusion** — support / conditional support / oppose, with core reasons
2. **Risk scorecard on bull points** — Reliability 1-5 per point plus pushback
3. **Risk scorecard on bear points** — Reliability 1-5 per point plus pushback
4. **Blind-spot risks** — Important risks neither analyst stressed
5. **Position sizing** — Explicit range (e.g., not more than X% of portfolio)
6. **Stop & hedge** — Specific stop prices, triggers, recommended hedges
7. **Risk conditions** — If approval is conditional, state prerequisites`

const riskResult = await agent(RISK_PROMPT, { label: 'risk_officer', phase: 'Risk Review' })

// ============================================================
// Phase 3: PM final decision
// ============================================================
phase('Decision')

const PM_PROMPT = `You are a senior Portfolio Manager chairing the investment committee. Make the final investment decision on ${TARGET} (market: ${MARKET}).

## Bull Case
${bullResult || '(No bull report)'}

## Bear Case
${bearResult || '(No bear report)'}

## Risk Review
${riskResult || '(No risk review)'}

## Decision Framework

### Synthesis
- Use load_skill("strategy-generate") for documentation standards
- Relative strength of bull vs bear (weighting, not head-count voting)
- How the macro backdrop helps or hurts this name
- Timing: is now the best entry/exit window

### Decision Making
- Clear action: long / short / wait / hedge — no ambiguity
- Staged entry/exit (avoid one-shot full size)
- Final target and stop levels
- Expected holding horizon (short / medium / long)
- Final position size within risk bounds

## Required Outputs (7 items)
1. **PM decision statement** — One paragraph: direction, size, core rationale
2. **Ruling on arguments** — Which points adopted/rejected, with PM reasoning
3. **How risk input was used** — Accept / adjust / reject each CRO item with reasons
4. **Execution plan** — First tranche, add triggers, trim triggers, timeline
5. **Targets & stops** — PM-final bull/base/bear price objectives and hard stop
6. **Confidence & review triggers** — Confidence 0-100%, what forces re-evaluation
7. **Backtest summary** — If core thesis is rule-based: run backtest and report win rate, mean return, max drawdown

DECISIONS MUST BE EXECUTABLE. Every key number must be explicit. No "it depends."`

const pmResult = await agent(PM_PROMPT, { label: 'portfolio_manager', phase: 'Decision' })

// ============================================================
// Return synthesized result
// ============================================================
return {
  preset: 'investment_committee',
  target: TARGET,
  market: MARKET,
  bull: bullResult,
  bear: bearResult,
  risk: riskResult,
  decision: pmResult,
}
