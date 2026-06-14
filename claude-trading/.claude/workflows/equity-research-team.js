export const meta = {
  name: 'equity-research-team',
  description: 'Equity Research Team — macro → sector → stock three-tier pipeline → aggregated research report. Native Claude Code replacement for run_swarm("equity_research_team").',
  phases: [
    { title: 'Macro', detail: 'Macro environment analysis' },
    { title: 'Sector', detail: 'Sector allocation and ranking' },
    { title: 'Stock Picking', detail: 'Stock screening and analysis' },
    { title: 'Report', detail: 'Final research report synthesis' },
  ],
  whenToUse: 'When the user asks for a full top-down research report across macro → sector → stock, wants equity research, or says "研报" / "行业研究" / "选股".',
}

const MARKET = args.market || 'A-shares'
const GOAL = args.goal || 'identify the most promising investment opportunities'

// ============================================================
// Phase 1: Macro analysis
// ============================================================
phase('Macro')

const MACRO_PROMPT = `You are a senior macroeconomic analyst. Analyze the current macroeconomic environment and its impact on the ${MARKET} market, with focus on ${GOAL}.

## Output Requirements
1. **Macro Overview** — Core indicators: GDP, CPI, PMI, employment
2. **Monetary Policy & Liquidity** — Key signals from interest rates, M2, credit
3. **Global Market Linkages** — Spillover effects of Fed/ECB policy
4. **Risk Factors** — 3-5 major macro risk points
5. **Conclusion for ${MARKET}** — Bullish / bearish / neutral rationale

Use web_search for latest data. Use read_url for official sources (PBOC, NBS, Fed, etc.). Use load_skill("global-macro") for framework reference.`

const macroResult = await agent(MACRO_PROMPT, { label: 'macro_analyst', phase: 'Macro' })

// ============================================================
// Phase 2: Sector analysis
// ============================================================
phase('Sector')

const SECTOR_PROMPT = `You are a senior sector analyst. Based on the macro analysis below, identify the most promising sectors in ${MARKET}, with focus on ${GOAL}.

## Macro Context
${macroResult || '(No macro report available)'}

## Output Requirements
1. **Sector Prosperity Ranking** — Top 5 sectors with scoring rationale
2. **Core Growth Drivers** — Growth logic for each recommended sector
3. **Industry Chain Analysis** — Upstream/midstream/downstream benefit degree
4. **Competitive Landscape** — Concentration, barriers, leading companies
5. **Recommended Sectors** — 2-3 sectors with suggested allocation weights

Use factor_analysis for factor-based sector analysis. Use load_skill("sector-rotation") and load_skill("multi-factor") for frameworks. For A-shares, reference 申万 industry classification.`

const sectorResult = await agent(SECTOR_PROMPT, { label: 'sector_analyst', phase: 'Sector' })

// ============================================================
// Phase 3: Stock picking
// ============================================================
phase('Stock Picking')

const STOCK_PROMPT = `You are a senior stock analyst. Screen specific investment targets from the recommended sectors and conduct combined technical + fundamental assessment.

## Sector Context
${sectorResult || '(No sector report)'}

## Macro Background
${macroResult || '(No macro report)'}

## Output Requirements
1. **Recommended Target List** — Each with ticker, name, sector
2. **Fundamental Assessment** — PE/PB/ROE, revenue growth, earnings quality
3. **Technical Signals** — Trend, support/resistance, price-volume dynamics
4. **Entry Logic** — Buy trigger conditions for each target
5. **Risk Disclosure** — Primary risks per target

Use load_skill("strategy-generate") for documentation standards. Use get_market_data (source="akshare" for A-shares) to fetch real price data. Use backtest to validate stock selection logic where possible.`

const stockResult = await agent(STOCK_PROMPT, { label: 'stock_picker', phase: 'Stock Picking' })

// ============================================================
// Phase 4: Final report synthesis
// ============================================================
phase('Report')

const AGGREGATE_PROMPT = `You are a senior research report editor. Synthesize all analysts' outputs into a complete, professional investment research report.

## Macro Analysis
${macroResult || '(No macro analysis)'}

## Sector Analysis
${sectorResult || '(No sector analysis)'}

## Stock Analysis
${stockResult || '(No stock analysis)'}

## Output Requirements (Markdown report)
1. **Executive Summary** — Key investment points in under 200 words
2. **Macro Environment** — Integrate macro conclusions
3. **Sector Allocation** — Integrate sector recommendations with weights
4. **Stock Recommendations** — Integrate stock selections with entry logic
5. **Risk Disclosures** — Aggregate all risk factors with severity
6. **Action Recommendations** — Clear position and timing guidance

Use load_skill("report-generate") for report standards. Ensure internal consistency, traceable data, and logical support for all conclusions.`

const reportResult = await agent(AGGREGATE_PROMPT, { label: 'aggregator', phase: 'Report' })

// ============================================================
// Return synthesized result
// ============================================================
return {
  preset: 'equity_research_team',
  market: MARKET,
  goal: GOAL,
  macro: macroResult,
  sector: sectorResult,
  stock: stockResult,
  report: reportResult,
}
