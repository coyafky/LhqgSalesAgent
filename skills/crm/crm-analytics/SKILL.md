---
name: crm-analytics
description: 有膜有漾 店长数据分析 — 店长说一句话问经营情况，助理聚合查询7张CRM表，生成结构化运营报告
requires:
  - lark-base
base:
  base_url: https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8
  base_token: Q6VQbuLTOaPP5VspfKXc7ZbTnA8
---

# CRM店长数据分析助手

## 概述

店长用一句话问经营情况，助理自动聚合查询 7 张 CRM 表的数据，生成结构化运营报告。支持按时间范围、销售、产品、渠道等多维度分析。

## 参考文件

本 skill 附带以下参考文件，执行前按需读取：

- `../references/intent-matching.md` — 确认当前请求是否明确是数据分析、统计或运营报表意图。
- `references/scheduled-check-pattern.md` — 定时 Hook 模式（沉睡预警/回访提醒的通用设计）

**Base token：** `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
**主要查询方式：** `lark-cli base +data-query`（聚合查询） + `lark-cli base +record-list`（列表查询）
**身份：** `--as bot`

## 数据表总览

| 表名 | 表 ID | 关键分析字段 |
|------|-------|-------------|
| 线索管理 | `tblHsrpSsTmJnB0c` | 来源渠道、线索状态、意向产品类型、创建时间、销售负责人 |
| 跟进记录 | `tblx0u6u4N1Vv2vY` | 跟进日期、跟进结果、跟进方式、记录分类、跟进人 |
| 报价表 | `tblzGNVSFPSXgb9K` | 报价状态、报价金额、成交金额、报价人、创建时间 |
| 客户车辆档案表 | `tblV6qrgb7Xef1N7` | 客户状态、客户标签、销售负责人 |
| 工单表 | `tblntyv0q6aS6Y3v` | 工单状态、预约施工时间、实际完工时间、施工师傅、销售负责人 |
| 售后表 | `tbliYr7rZow5cBIq` | 售后类型、售后状态、客户满意度、负责销售 |
| 产品项目表 | `tblbfqLLrnxyOMIt` | 产品类型、产品名字 |

## ⚡ 快速识别意图（触发条件）

| 店长说 | 识别关键词 | 分析方向 |
|--------|-----------|---------|
| *本月运营概况/整体怎么样* | **运营概况/整体/总览** | 全表概览 |
| *本月新增了多少线索* | **线索/新增/线索量** | 线索分析 |
| *各销售的业绩排名* | **销售排名/业绩/谁做得好** | 销售分析 |
| *各渠道来源的线索量* | **渠道/来源/抖音/小红书** | 渠道分析 |
| *本月成交了多少单* | **成交/业绩/销售额** | 成交分析 |
| *工单完成情况* | **工单/施工/完工** | 工单分析 |
| *售后问题统计* | **售后/返工/质保/投诉** | 售后分析 |
| *哪个产品卖得最好* | **产品/哪个最** | 产品分析 |

## 分析模块

### 模块 1：运营总览

查询维度：本月整体数据

```bash
# 线索总数（本月）
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblHsrpSsTmJnB0c"}},
  "measures":[{"field_name":"创建时间","aggregation":"count_all","alias":"total_leads"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"创建时间","operator":"is","value":["CurrentMonth"]}]},
  "shaper":{"format":"flat"}
}'

# 已成交报价总额（本月）
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblzGNVSFPSXgb9K"}},
  "measures":[{"field_name":"报价金额","aggregation":"sum","alias":"total_quote_amount"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"报价状态","operator":"is","value":["已成交"]},{"field_name":"成交日期","operator":"is","value":["CurrentMonth"]}]},
  "shaper":{"format":"flat"}
}'

# 工单完成数（本月）
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblntyv0q6aS6Y3v"}},
  "measures":[{"field_name":"工单编号","aggregation":"count_all","alias":"completed_orders"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"工单状态","operator":"is","value":["已关闭"]},{"field_name":"实际完工时间","operator":"is","value":["CurrentMonth"]}]},
  "shaper":{"format":"flat"}
}'

# 待处理售后数
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tbliYr7rZow5cBIq"}},
  "measures":[{"field_name":"售后编号","aggregation":"count_all","alias":"pending_after_sales"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"售后状态","operator":"isNot","value":["已解决","已关闭"]}]},
  "shaper":{"format":"flat"}
}'
```

### 模块 2：销售排名分析

按销售分组统计成交额和成交量：

```bash
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblzGNVSFPSXgb9K"}},
  "dimensions":[{"field_name":"报价人","alias":"salesperson"}],
  "measures":[
    {"field_name":"报价金额","aggregation":"sum","alias":"total_amount"},
    {"field_name":"报价编号","aggregation":"count_all","alias":"deal_count"}
  ],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"报价状态","operator":"is","value":["已成交"]},{"field_name":"成交日期","operator":"is","value":["CurrentMonth"]}]},
  "sort":[{"field_name":"total_amount","order":"desc"}],
  "shaper":{"format":"flat"}
}'
```

按销售分组统计线索量：

```bash
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblHsrpSsTmJnB0c"}},
  "dimensions":[{"field_name":"销售负责人","alias":"salesperson"}],
  "measures":[{"field_name":"创建时间","aggregation":"count_all","alias":"lead_count"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"创建时间","operator":"is","value":["CurrentMonth"]}]},
  "sort":[{"field_name":"lead_count","order":"desc"}],
  "shaper":{"format":"flat"}
}'
```

### 模块 3：渠道来源分析

```bash
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblHsrpSsTmJnB0c"}},
  "dimensions":[{"field_name":"来源渠道","alias":"channel"}],
  "measures":[{"field_name":"创建时间","aggregation":"count_all","alias":"lead_count"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"创建时间","operator":"is","value":["CurrentMonth"]}]},
  "sort":[{"field_name":"lead_count","order":"desc"}],
  "shaper":{"format":"flat"}
}'
```

### 模块 4：产品分析

```bash
# 各产品成交统计
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblzGNVSFPSXgb9K"}},
  "dimensions":[{"field_name":"报价项目","alias":"product"}],
  "measures":[
    {"field_name":"报价金额","aggregation":"sum","alias":"total_amount"},
    {"field_name":"报价编号","aggregation":"count_all","alias":"deal_count"}
  ],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"报价状态","operator":"is","value":["已成交"]}]},
  "sort":[{"field_name":"total_amount","order":"desc"}],
  "pagination":{"limit":10},
  "shaper":{"format":"flat"}
}'
```

### 模块 5：工单分析

```bash
# 工单状态分布
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblntyv0q6aS6Y3v"}},
  "dimensions":[{"field_name":"工单状态","alias":"status"}],
  "measures":[{"field_name":"工单编号","aggregation":"count_all","alias":"count"}],
  "shaper":{"format":"flat"}
}'

# 各师傅施工量
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblntyv0q6aS6Y3v"}},
  "dimensions":[{"field_name":"施工师傅","alias":"tech"}],
  "measures":[{"field_name":"工单编号","aggregation":"count_all","alias":"order_count"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"实际完工时间","operator":"is","value":["CurrentMonth"]}]},
  "sort":[{"field_name":"order_count","order":"desc"}],
  "shaper":{"format":"flat"}
}'
```

### 模块 6：售后分析

```bash
# 售后类型分布
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tbliYr7rZow5cBIq"}},
  "dimensions":[{"field_name":"售后类型","alias":"type"}],
  "measures":[{"field_name":"售后编号","aggregation":"count_all","alias":"count"}],
  "filters":{"type":1,"conjunction":"and","conditions":[{"field_name":"创建时间","operator":"is","value":["CurrentMonth"]}]},
  "sort":[{"field_name":"count","order":"desc"}],
  "shaper":{"format":"flat"}
}'

# 客户满意度分布
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tbliYr7rZow5cBIq"}},
  "dimensions":[{"field_name":"客户满意度","alias":"satisfaction"}],
  "measures":[{"field_name":"售后编号","aggregation":"count_all","alias":"count"}],
  "shaper":{"format":"flat"}
}'
```

## 工作流程

### 第一步：识别分析意图

从店长的问题中提取：
- 分析对象：线索/跟进/报价/成交/工单/售后/整体
- 时间范围：今天/本周/本月/上月/今年
- 分组维度：按销售/按渠道/按产品/按师傅
- 排序：最多/最少/最好/最差

### 第二步：时间范围映射

| 店长说 | DSL time filter |
|--------|----------------|
| 今天/今日 | `["Today"]` |
| 本周/这周 | `["CurrentWeek"]` |
| 本月/这个月 | `["CurrentMonth"]` |
| 上月/上个月 | `["LastMonth"]` |
| 最近7天/近一周 | `["TheLastWeek"]` |
| 最近30天/近一个月 | `["TheLastMonth"]` |
| 今年/今年度 | 使用 `isGreater` + `ExactDate` |
| 没说时间 | 默认 `["CurrentMonth"]`（本月） |

### 第三步：构造查询

根据意图选择对应的 DSL 模板，填入正确的表 ID 和字段名。

⚠️ **坑点注意：**
- **alias 不支持中文** — 必须用英文别名如 `total_amount`、`lead_count`
- **field_name 必须精确匹配** — 与表中字段名完全一致（区分大小写）
- **select 筛选用选项名** — 如 `"已成交"`、`"抖音"`，不是 ID
- **人员筛选用 open_id** — 如 `["ou_xxx"]`
- **日期关键字首字母大写** — `CurrentMonth` 不是 `currentMonth`

### 第四步：格式化输出

将查询结果呈现为店长易读的结构化报告：

```markdown
📊 【关键词】分析报告

📅 时间范围：本月（2026年6月）

🔹 核心数据
- 新增线索：XX 条
- 已成交订单：XX 单
- 成交总额：¥XX
- 工单完成：XX 单
- 待处理售后：XX 单

🔹 按销售排名
1. 吕佳豪 — ¥XX（XX 单）
2. 张秋苑 — ¥XX（XX 单）
3. 刘志培 — ¥XX（XX 单）

🔹 按渠道来源
- 抖音：XX 条
- 小红书：XX 条
- …

💡 建议：{基于数据的运营建议}
```

### 第五步：多表联合查询

对于需要跨表对比的复杂问题（如转化率），依次查询多张表后汇总：

1. 查线索管理 → 总线索数
2. 查报价表 → 已成交数
3. 计算转化率 = 成交数 / 线索数

## 常见分析场景与 DSL 模板

### 场景 1：本月运营总览

查询 5 张表的核心指标，输出概览报告。

### 场景 2：各销售业绩排名

查询报价表（按报价人分组，已成交，求和报价金额）+ 线索表（按销售负责人分组，计数）

### 场景 3：渠道效果分析

查询线索表（按来源渠道分组，计数）+ 报价表（筛选已成交，看各渠道转化情况）

### 场景 4：工单进度看板

查询工单表（按工单状态分组，计数）

### 场景 5：售后质量分析

查询售后表（按售后类型分组，计数 + 按满意度分组，计数）

```markdown
📊 本月售后质量报告

售后类型分布：
- 返工：X 单
- 质保：X 单
- 投诉：X 单
- 保养：X 单
- 复购回访：X 单

客户满意度：
- 满意：X%
- 一般：X%
- 不满意：X%
```

## 店长一句话示例

| 店长说 | 分析内容 |
|--------|---------|
| *这个月整体怎么样？* | 运营总览：线索、成交、工单、售后 |
| *各销售这个月做了多少业绩？* | 销售排名：成交额+成交量 |
| *线索都是从哪来的？* | 渠道分析：来源分布 |
| *哪个产品卖得最好？* | 产品分析：各产品成交额 |
| *工单完成情况如何？* | 工单分析：状态分布+师傅工作量 |
| *最近有没有售后问题？* | 售后分析：类型+满意度 |
| *上个月的业绩怎么样？* | 时间切换为上月 |
| *抖音来的客户成交了多少？* | 渠道转化分析 |

## 安全规则

- 数据分析结果基于 CRM 表实时数据，不编造数字。
- 查询结果仅作为经营参考，不作为最终财务依据。
- 涉及销售排名的数据仅限内部管理使用，不对外公开。
- 如果查询超时或返回空数据，提示店长检查数据是否已录入。

## 关联 Skill

- 所有 `crm-*` 技能 — 数据分析的基础数据来源
- `lark-base` — 实际查询操作
- `crm-sleeping-lead-hook` — 沉睡线索预警（每日自动检查，使用本 skill 的查询模式）
- `crm-revisit-reminder-hook` — 客户回访提醒（每日自动检查，使用本 skill 的查询模式）

---

## 定时 Hook 的配合

本 skill 的 `+data-query` 模板同时被两个 cron-based hook 使用：

| Hook | 用途 | 定时 | 用到的查询模板 |
|------|------|:----:|---------------|
| 沉睡线索预警 | 检查超过7/14/30天未跟进的线索 | 每日9:30 | 线索管理 + 跟进记录 |
| 客户回访提醒 | 检查完工后3/7/30天的工单，提醒回访 | 每日9:00 | 工单表 + 客户档案 |

具体模式见 `references/scheduled-check-pattern.md`。
