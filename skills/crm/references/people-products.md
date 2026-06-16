# CRM People and Product Lookups

Use this reference when filling relation fields for salespeople, technicians, or products.

## Salespeople

| Name | Feishu open_id | 销售人员表 record_id |
|---|---|---|
| 吕佳豪 | `ou_a6d0078cfe6dad2776c08d9ea9117a3d` | `rec6gBu3IVdtim` |
| 张秋苑 | `ou_24446a42d53adf9c2515fafce699a1b8` | `reciu97dvVdCDK` |
| 刘志培 | `ou_1c91ab71d9b6714030442cb1c6b85457` | `recERZnykdciRR` |

Rule: person fields use `open_id`; relation fields to 销售人员表 use `record_id`.

## Technicians

| Name | Feishu open_id | 施工师傅表 record_id |
|---|---|---|
| 梁增炯 | `ou_42e63b7978f1a6417d2bfe1263ed9de0` | `recvmpyLSelJsO` |
| 阮其梓 | `ou_7e6f20380a065b1ef6cb31e8d83c538b` | `recvmpyLSeubpW` |

Rule: 工单表 `施工师傅` uses `open_id`; `施工师傅表` uses technician table `record_id`.

## Product Lookup

Known products may be used directly when names match exactly. If the product name is partial, ambiguous, or not listed in the active skill, search 产品项目表:

```bash
lark-cli base +record-search \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblbfqLLrnxyOMIt \
  --search-field fldEOYqkRO \
  --keyword "<产品名>" \
  --as bot
```

If multiple products match, ask the user to choose before writing relation fields.
