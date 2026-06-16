# CRM Idempotency and Write Policy

Use this reference before calling `+record-upsert`, `+record-create`, or updating an existing CRM record.

## Default Policy

- Prefer search-then-create/update over blind upsert.
- Use `+record-upsert` only when the command has a reliable unique key or an explicit `--record-id`.
- If no stable key exists, create a new record after duplicate search and confirmation.
- If multiple possible matches exist, ask the user to choose by customer, vehicle, sales owner, date, amount, or record ID.

## Object Rules

| Object | Create or update rule | Duplicate key |
|---|---|---|
| Lead | Search first. Update existing only after confirmation. | Phone exact match, then customer name + vehicle + sales owner |
| Follow-up | Usually create a new record. Do not upsert by customer name. | Same lead + same follow-up date + very similar summary only for duplicate warning |
| Quote | Create new quote unless updating a named/current quote. | Source lead + quote project + quote date/status |
| Deal update | Update existing quote by `record_id`. | Existing quote record ID |
| Archive | Search existing archive first; update if same customer/vehicle. | Customer name + vehicle basic info, or linked deal quote |
| Workorder | Create new unless changing status of a known workorder. | Customer archive + quote + project + appointment time |
| After-sales | Create new issue unless resolving/updating known issue. | Customer archive + original workorder + issue type + issue date |
| Revisit reminder | Never duplicate reminders. | Workorder record ID + reminder day |
| Sleeping lead alert | Alert once per lead per alert level per day. | Lead record ID + alert level + date |

## Confirmation Text

When duplicates are found, present choices like:

```markdown
找到多条可能记录，请选择要更新哪一条：

1. recXXX | 王先生 | 问界M9 | 吕佳豪 | 最近更新 2026-06-15
2. recYYY | 王先生 | 宝马3系 | 刘志培 | 最近更新 2026-06-13

回复序号或 record_id。
```

## Failure Handling

- If a write command fails, do not report success.
- Return the failed table, operation, error summary, and the JSON payload that was attempted with private fields masked.
- If verification readback fails after a successful write, say "写入可能已成功，但回读验证失败" and include the record ID if available.
