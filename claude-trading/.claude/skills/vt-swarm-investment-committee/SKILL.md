---
name: vt-swarm-investment-committee
description: Investment committee pattern — parallel bull/bear debate → risk officer review → PM final decision. Replaces the deprecated run_swarm("investment_committee") preset with native Claude Code Agent dispatch.
---

<!--
Available Vibe-Trading MCP tools for this skill:
  - get_market_data(codes, start_date, end_date, source, interval) — fetch OHLCV. A-shares MUST use source="akshare" or source="tushare"
  - backtest(run_dir) — run backtest from config.json + signal_engine.py
  - factor_analysis(codes, factor_name, start_date, end_date, ...) — factor IC/returns
  - pattern_recognition(run_dir) — chart pattern detection
  - analyze_options(...) — options pricing & greeks
  - web_search(query) / read_url(url) / read_document(path) — content tools
  - write_file(path, content) / read_file(path) — file I/O

IMPORTANT: Do NOT call run_swarm. Use the Agent tool dispatch pattern below instead.
-->

# Investment Committee (Native Claude Code)

## Purpose

代替已弃用的 `run_swarm("investment_committee")`。使用 Claude Code 原生 `Agent` 工具实现**多空辩论 → 风险审查 → PM 最终决策**的买方投研流程。

## DAG Structure

```
bull_advocate ──┐
                 ├──→ risk_officer ──→ portfolio_manager (最终决策)
bear_advocate ──┘
```

- **Layer 1 (并行)**: 多头研究员 + 空头研究员同时分析
- **Layer 2**: 首席风险官审查多空双方论点
- **Layer 3**: 基金经理综合所有输入做最终决策

## 变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `target` | 目标证券代码 | `300274.SZ`、`AAPL.US`、`BTC-USDT` |
| `market` | 市场 | `A-shares`、`US`、`HK`、`crypto` |

## Agent 角色定义

### 1. bull_advocate — 多头研究员

从技术面、基本面、情绪面三个维度构建做多逻辑。每一个观点必须数据支撑。

**分析维度**：
- 技术面：均线排列 (MA5/20/60/250)、MACD 金叉/底背驰、RSI 区间、量价配合
- 基本面：PE/PB 历史分位 vs 行业折价、ROE/ROIC 趋势、FCF 转化率、营收/利润增速
- 情绪面：机构持仓变化、北向资金流向、分析师评级上调、恐贪指数

**必须产出的 7 项**：
1. 多头论点（3-5 条，标注置信度）
2. 技术面详细分析（含关键支撑/目标位）
3. 基本面量化空间（估值修复 + 盈利增长）
4. 情绪与资金面支撑
5. 催化剂日历（未来 1-3 个月）
6. 多头目标价区间（估值重估/盈利增长/技术目标三个角度）
7. 多头案例的主要风险（诚实列出 2-3 个可能推翻多头逻辑的场景）

**参考技能**: `vt-technical-basic`, `vt-fundamental-filter`, `vt-sentiment-analysis`, `vt-earnings-revision`

**MCP 工具**: `get_market_data` (必须用 `source="akshare"` 拉 A 股数据), `factor_analysis`, `web_search`

---

### 2. bear_advocate — 空头研究员

独立审视风险，系统性挖掘做空逻辑。挑战共识，不被市场情绪裹挟。

**分析维度**：
- 技术风险：关键阻力、顶部形态（头肩顶/双顶/三重顶）、顶背驰、量价背离、死亡交叉
- 估值泡沫：PE/PB/PS vs 历史分位和行业溢价、DCF 内在价值 vs 市价缺口
- 基本面恶化：毛利/净利率结构性下行、竞争加剧、债务负担、管理层减持
- 风险量化：历史最大回撤、VaR/CVaR、波动率、beta、尾部事件

**必须产出的 7 项**：
1. 空头风险点（3-5 条，标注严重程度）
2. 技术面崩溃风险（含阻力位和止损位）
3. 估值泡沫评估（量化溢价 vs 公允价值、均值回归下行目标）
4. 基本面恶化证据
5. 风险指标（VaR、预期最大回撤、压力场景）
6. 空头目标价区间（估值收缩 + 盈利下修场景）
7. 什么会推翻空头逻辑（即多头反驳点）

**参考技能**: `vt-technical-basic`, `vt-fundamental-filter`, `vt-risk-analysis`, `vt-volatility`

**MCP 工具**: `get_market_data`, `factor_analysis`, `web_search`

---

### 3. risk_officer — 首席风险官

不站队多头或空头，独立审查双方论点，量化风险，给出仓位建议。

**审查框架**：
- 检验多头是否有确认偏差（cherry-picking）
- 检验空头是否有情绪驱动的过度悲观
- 识别双方都未覆盖的盲点风险
- 评估双方目标价方法论严谨性
- 从波动率推算合理仓位上限（Kelly / 固定分数法）
- 流动性评估：ADV 能否支撑目标仓位快速进出
- 三个压力场景：基准 / 看空 / 极端看空
- 止损纪律：建议止损位和触发条件

**必须产出的 7 项**：
1. 风险审查结论（支持/有条件支持/反对，附核心理由）
2. 多头论点评分卡（每条 1-5 分 + 质疑）
3. 空头论点评分卡（每条 1-5 分 + 质疑）
4. 盲点风险（双方都未强调但 CRO 认为重要的风险）
5. 仓位建议（明确范围，如"不超过组合 X%"）
6. 止损与对冲方案（具体价格、触发条件、对冲工具和规模）
7. 审批条件（如有条件通过，明确前置条件）

**参考技能**: `vt-risk-analysis`, `vt-volatility`, `vt-correlation-analysis`

---

### 4. portfolio_manager — 基金经理

主持投委会，做最终投资决策。综合分析多空辩论和风险审查，给出可执行的决策。**每个关键数字必须明确，不可含糊**。

**决策框架**：
- 综合多空论点相对强弱（加权，不是简单计数投票）
- 宏观背景对这笔交易的助益或阻碍
- 时机判断：现在是最好的进出场窗口吗
- 使用 `backtest` 验证核心逻辑（如果能量化为规则）
- 明确行动：做多 / 做空 / 等待 / 对冲
- 分批进出（避免一次性满仓）
- 最终目标价和止损位

**必须产出的 7 项**：
1. PM 决策声明（方向、仓位、核心逻辑，不模棱两可）
2. 对各论点的裁决（采纳/拒绝哪些，附 PM 理由）
3. 风险输入的使用说明（接受/调整/拒绝 CRO 每条建议的理由）
4. 执行计划（首批仓位、加仓触发、减仓触发、时间线）
5. 目标价与止损（PM 最终的多/基准/空价格目标，硬止损位）
6. 置信度与复核触发（0-100% 置信度，什么条件触发重新评估）
7. 回测摘要（如运行：历史胜率、平均收益、最大回撤）

**参考技能**: `vt-strategy-generate`, `vt-asset-allocation`

**MCP 工具**: `backtest`

---

## 派发方式（推荐用 Workflow）

对于批量/标准化执行，使用 `investment-committee` workflow：

```
/workflow investment-committee
```

Workflow 自动处理并行派发和 DAG 编排。

对于手动/灵活执行，按以下顺序派发 Agent：

### Step 1: 并行派发多空双方

```
Agent("bull_advocate", prompt="对 {target} ({market}) 做全面多头分析...")
Agent("bear_advocate", prompt="对 {target} ({market}) 做全面空头分析...")
```

### Step 2: 风险审查（等 Step 1 返回后）

```
Agent("risk_officer", prompt="审查以下多空论点...\n\n多头报告: {bull_result}\n\n空头报告: {bear_result}")
```

### Step 3: PM 最终决策（等 Step 2 返回后）

```
Agent("portfolio_manager", prompt="综合以下材料做最终决策...\n\n多头: {bull}\n空头: {bear}\n风险审查: {risk}")
```

## 数据拉取前置步骤

在派发 agent 之前，先拉取目标标的的市场数据：

```
get_market_data(codes="{target}", source="akshare", start_date="2024-01-01", end_date="2026-06-11")
```

A 股 **必须** 用 `source="akshare"` 或 `source="tushare"`，不能用 `source="auto"`。

将拉取的数据摘要提供给多空双方 agent，确保分析基于真实数据而非训练记忆。
