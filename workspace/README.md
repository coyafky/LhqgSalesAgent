# 有膜有漾 Sales Agent Workspace

这个目录是 `ymyy-sales-agent` 的项目级工作区，用来沉淀销售团队与 Hermes agent 协作时需要共同遵守的规范、流程、验收标准和维护记录。

它不是 Hermes 运行时目录，也不替代 `skills/`、`knowledge-base/`、`SOUL.md` 或 `profile.yaml`。它的作用是把这些能力组织成销售人员能理解、能执行、能反馈、能迭代的工作台。

## Workspace 结构

- `00_project-spec/`：项目 PRD、SDD、角色边界、路线图。
- `01_sales-scenarios/`：一线销售场景 SOP，包括接待、诊断、推荐、异议、跟进、售后、改色生图。
- `02_sales-assets/`：销售资产索引，包括产品知识、FAQ、话术、案例素材。
- `03_prompt-and-skills/`：Agent 提示词、技能路由和输出契约。
- `04_knowledge-rag/`：知识库来源、入库规范、检索策略、数据质量待办。
- `05_evaluation/`：验收问题、评估指标、回归记录。
- `06_operations/`：日常运营、销售反馈收集、版本变更。
- `07_delivery/`：飞书交付、生图交付、部署协作说明。
- `08_crm-assistant/`：CRM 表销售填写助理，支持销售用自然语言补全、更新和质检 CRM 记录。

## 现有核心资产

- Agent 定位：`SOUL.md`
- Profile 配置：`profile.yaml`
- 主知识库：`knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl`
- 知识库说明：`knowledge-base/ymyy-sales-agent/README.md`
- 验收问题：`knowledge-base/ymyy-sales-agent/queries.md`
- 改色生图技能：`skills/ark-seedream-car-preview/`

## 销售核心能力地图

| 销售任务 | 对应能力 |
| --- | --- |
| 客户需求不清楚 | `skills/diagnose-with-spin-selling` |
| 客户问价格、风险、对比 | `skills/answer-customer-faq-transparently` |
| 推荐车衣/窗膜/改色方向 | `skills/recommend-film-product` |
| 客户嫌贵、有疑虑 | `skills/handle-film-objections` |
| 客户压价、犹豫、比较竞品 | `skills/negotiate-with-tactical-empathy` |
| 话术需要更自然、更有说服力 | `skills/strengthen-sales-wording-with-influence` |
| 生成微信/飞书跟进消息 | `skills/write-sales-followup` |
| 客户要看改色上车效果 | `skills/ark-seedream-car-preview` |
| 销售要填写 CRM 表 | `workspace/08_crm-assistant` |

## 工作原则

1. 先规范，再生成：重要销售输出必须能对应到场景 SOP、技能路由和知识来源。
2. 先诊断，再推荐：没有明确诉求时，不直接堆套餐或催成交。
3. 先事实，再话术：参数、质保、售后必须来自知识库；价格、活动、库存、排期以门店最新确认为准。
4. 先低风险推进，再成交：常见下一步是确认车型、看样膜、对比套餐、到店检查、预约施工。
5. AI 预览不等于交付承诺：改色效果图用于辅助确认，最终以实物色卡、车辆光线和施工结果为准。
