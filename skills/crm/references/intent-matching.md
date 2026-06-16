# CRM Intent Matching

Use this reference to decide whether a user request directly matches a CRM skill. This is not a central router. Each skill should trigger only when the user's intent clearly matches that skill's job.

## Principle

- Prefer explicit user intent over keyword priority.
- Do not redirect just because another CRM object is mentioned.
- Do not let one skill preempt another by priority. A skill should activate only when its own intent is directly matched.
- If the user clearly names the target action, use that matching skill.
- If the intent is ambiguous, ask one short clarification instead of guessing.
- Multi-step requests may use multiple skills in dependency order, but each step should still match a concrete intent.

## Intent Matches

| Skill | Match when the user intent is... | Strong phrases |
|---|---|---|
| `crm-lead-entry` | Create or update a lead/customer source record | 录线索, 新增线索, 新客户, 填CRM, 线索状态 |
| `crm-followup-entry` | Record communication or follow-up notes | 跟进记录, 记录跟进, 今天聊了, 电话沟通, 微信沟通, 客户反馈 |
| `crm-quote-entry` | Create/update a quote, deal, payment, or refund | 报价填写, 报价, 报个价, 成交价, 定金, 收款, 退款 |
| `crm-archive-entry` | Create/update a closed customer vehicle archive | 建档, 归档, 客户档案, 车辆档案, VIN, 车牌 |
| `crm-workorder-entry` | Create/update an installation workorder | 工单填写, 下工单, 派工, 安排施工, 施工中, 交付, 完工 |
| `crm-after-sales-entry` | Create/update an after-sales issue or service visit | 售后填写, 售后, 返工, 质保, 投诉, 保养, 售后回访 |
| `crm-analytics` | Query or summarize CRM data | 数据分析, 运营概况, 销售排名, 转化率, 统计, 报表 |
| Hook skills | Configure or run scheduled checks | 定时检查, hook, 沉睡线索, 回访提醒 |

## Clarify Ambiguity

Ask a clarification when a phrase can reasonably mean two intents:

| User says | Ask |
|---|---|
| "记录一下王先生" | "你要记录跟进沟通，还是补充客户车辆档案？" |
| "王先生成交了" | "这是要更新报价成交状态，还是成交后建客户档案？" |
| "回访王先生" | "这是普通跟进记录，还是售后/满意度回访？" |
| "王先生到店了" | "是新线索到店，还是要下施工工单？" |

## Multi-Step Requests

If the user explicitly asks for a full chain, execute only the requested steps, in dependency order:

`crm-lead-entry` -> `crm-followup-entry` -> `crm-quote-entry` -> `crm-archive-entry` -> `crm-workorder-entry` -> `crm-after-sales-entry`

Carry created `record_id` values forward for relation fields.
