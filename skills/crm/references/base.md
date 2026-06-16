# CRM Shared Base Rules

Use this reference before any CRM write, update, query, or scheduled hook.

## Base

- Base URL: `https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- Base token: `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- Identity: always pass `--as bot`
- Default timezone: `Asia/Shanghai`

## Tables

| Logical table | Table ID | Main use |
|---|---:|---|
| 线索管理 | `tblHsrpSsTmJnB0c` | New leads and lead status |
| 跟进记录 | `tblx0u6u4N1Vv2vY` | Communication history |
| 报价表 | `tblzGNVSFPSXgb9K` | Quotes and deal status |
| 客户车辆档案表 | `tblV6qrgb7Xef1N7` | Closed customer archive |
| 工单表 | `tblntyv0q6aS6Y3v` | Installation jobs |
| 售后表 | `tbliYr7rZow5cBIq` | After-sales issues and visits |
| 产品项目表 | `tblbfqLLrnxyOMIt` | Product lookup |
| 销售人员表 | `tblhP4v00FNjYQnm` | Salesperson relation records |
| 施工师傅表 | `tblrT7o18eeUEs9z` | Technician relation records |

## Date Handling

- Store datetime values in `YYYY-MM-DD HH:mm:ss`.
- If the user gives only a date for an appointment, ask for time unless the skill explicitly allows a default.
- For sales follow-up records, if no time is stated, use `00:00:00` on the resolved date.
- Resolve relative dates such as "今天", "明天", "下周六" in `Asia/Shanghai`.
- Never write unresolved natural language dates into CRM fields.

## Confirmation Boundary

Before a write or destructive update, show a confirmation summary and wait for explicit confirmation, except when the user clearly asks for immediate recording with enough required fields.

Always require confirmation when any of these are involved:

- Quote amount, deal amount, collected amount, refund amount
- Customer identity is ambiguous
- Multiple matching records exist
- Updating an existing record instead of creating a new one
- Closing, canceling, marking lost, refunding, or resolving a record

## Privacy

- Customer phone numbers, VINs, plate numbers, and WeChat IDs may be written to CRM.
- Do not copy private customer data into workspace documents or reference files.
- In chat summaries, mask private values unless the user needs exact values for verification.
