# Sales Agent Workflow SVG Diagrams

这些 SVG 图用于先确定 Sales Agent 的业务架构，再继续落 SDD、PRD、Skill 和飞书自动化实现。

| 文件 | 工作流 | 目的 |
| --- | --- | --- |
| `00-sales-agent-operating-system.svg` | 总览 | 把 Sales Agent 定义为销售工作操作系统 |
| `01-product-knowledge-recommendation.svg` | 产品知识与推荐 | 帮销售理解产品并生成客户推荐理由 |
| `02-customer-intake-diagnosis.svg` | 客户接待与诊断 | 把模糊需求转成可跟进线索 |
| `03-crm-natural-language-entry.svg` | CRM 自然语言填写 | 用自然语言完成 CRM 字段解析、确认和飞书写入 |
| `04-objection-negotiation-closing.svg` | 异议处理与成交推进 | 处理价格、竞品、信任和时机顾虑 |
| `05-followup-aftercare.svg` | 跟进、复购与售后 | 形成客户关系维护闭环 |
| `06-manager-sales-analytics.svg` | 店长数据分析 | 从 CRM 生成经营看板和团队动作建议 |
| `07-wrap-preview.svg` | 改色膜上车效果图 | 用客户实车图和色卡资产生成成交辅助图 |

后续文件树建议围绕这些 workflow 组织，而不是围绕孤立 skills 组织。Skill 是能力零件，Workflow 才是销售每天实际使用的工作单元。
