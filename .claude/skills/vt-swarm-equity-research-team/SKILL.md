---
name: vt-swarm-equity-research-team
description: Equity research team pattern — macro → sector → stock three-tier pipeline → aggregated research report. Replaces the deprecated run_swarm("equity_research_team") preset with native Claude Code Agent dispatch.
---

<!--
Available Vibe-Trading MCP tools for this skill:
  - get_market_data(codes, start_date, end_date, source, interval) — fetch OHLCV. A-shares MUST use source="akshare" or source="tushare"
  - backtest(run_dir) — run backtest from config.json + signal_engine.py
  - factor_analysis(codes, factor_name, start_date, end_date, ...) — factor IC/returns
  - web_search(query) / read_url(url) / read_document(path) — content tools
  - write_file(path, content) / read_file(path) — file I/O

IMPORTANT: Do NOT call run_swarm. Use the Agent tool dispatch pattern below instead.
-->

# Equity Research Team (Native Claude Code)

## Purpose

代替已弃用的 `run_swarm("equity_research_team")`。使用 Claude Code 原生 `Agent` 工具实现**宏观 → 行业 → 选股 → 汇总报告**的三层递进研究流程。

## DAG Structure

```
macro_analyst ──→ sector_analyst ──→ stock_picker ──→ aggregator (最终报告)
```

- **Layer 1**: 宏观分析师（独立起点）
- **Layer 2**: 行业分析师（依赖宏观分析）
- **Layer 3**: 股票分析师（依赖行业 + 宏观）
- **Layer 4**: 研报编辑（汇总所有输入，产出完整报告）

## 变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `market` | 目标市场 | `A-shares`、`HK`、`US`、`crypto` |
| `goal` | 研究目标 | `Q2 2026 新能源板块机会`、`寻找低估值高股息标的` |

## Agent 角色定义

### 1. macro_analyst — 宏观分析师

分析全球宏观环境、央行货币政策和地缘政治风险，判断当前宏观周期位置及其对目标市场的影响。

**必须产出的 5 项**：
1. 宏观全景 — 核心指标解读：GDP、CPI、PMI、就业
2. 货币政策与流动性 — 利率、M2、信贷等关键信号
3. 全球市场联动 — 美联储/欧央行政策的溢出效应
4. 风险因素 — 识别 3-5 个主要宏观风险点
5. 对 {market} 的结论 — 总结看多/看空/中性的宏观逻辑

**参考技能**: `vt-global-macro`, `vt-macro-analysis`

**MCP 工具**: `web_search`, `read_url`, `get_market_data`

---

### 2. sector_analyst — 行业分析师

基于宏观分析，识别目标市场中最有前景的行业板块。结合行业景气度、产业链传导和竞争格局。

**必须产出的 5 项**：
1. 行业景气度排名 — Top 5 行业及评分逻辑
2. 核心增长驱动力 — 每个推荐行业的增长逻辑
3. 产业链分析 — 上中下游受益程度
4. 竞争格局 — 集中度、进入壁垒、龙头公司
5. 推荐行业及配置建议 — 明确推荐 2-3 个行业，建议配置权重

**参考技能**: `vt-sector-rotation`, `vt-multi-factor`, `vt-fundamental-filter`

**MCP 工具**: `factor_analysis`, `get_market_data`

---

### 3. stock_picker — 股票分析师

从推荐行业中筛选具体标的，结合技术面和基本面做综合评估。

**必须产出的 5 项**：
1. 推荐标的列表 — 代码、名称、所属行业
2. 基本面评估 — PE/PB/ROE/营收增速等核心指标
3. 技术信号 — 趋势方向、支撑/阻力、量价配合
4. 入场逻辑 — 每只标的的买入触发条件
5. 风险披露 — 每只标的主要风险

**参考技能**: `vt-strategy-generate`, `vt-technical-basic`, `vt-earnings-revision`

**MCP 工具**: `backtest`, `factor_analysis`, `get_market_data`

---

### 4. aggregator — 研报编辑

综合所有分析师的输出，产出逻辑自洽、数据可追溯的完整投资研报。

**必须产出的 6 项**：
1. 执行摘要 — 200 字以内，核心投资要点
2. 宏观环境 — 整合宏观分析师结论
3. 行业配置 — 整合行业分析师推荐
4. 个股推荐 — 整合股票分析师选股
5. 风险披露 — 汇总所有风险因素
6. 行动建议 — 明确的仓位和时机指引

**参考技能**: `vt-report-generate`

---

## 派发方式（推荐用 Workflow）

```
/workflow equity-research-team
```

对于手动执行，按顺序串行派发（每层依赖上层输出）：

```
Step 1: Agent("macro_analyst", prompt="分析当前宏观环境对 {market} 的影响...")
Step 2: Agent("sector_analyst", prompt="基于宏观分析，识别 {market} 最有前景的行业...\n\n宏观报告: {macro_result}")
Step 3: Agent("stock_picker", prompt="从推荐行业中筛选标的...\n\n行业报告: {sector_result}\n宏观背景: {macro_result}")
Step 4: Agent("aggregator", prompt="汇总所有分析产出完整研报...\n\n宏观: {macro}\n行业: {sector}\n选股: {stock}")
```

## 数据拉取前置步骤

在派发 agent 之前，先拉取关键市场数据：

```
get_market_data(codes="000001.SZ", source="akshare", ...)  # 大盘基准
web_search("2026年 中国宏观 GDP CPI PMI 最新数据")
```

A 股数据**必须**用 `source="akshare"` 或 `source="tushare"`。
