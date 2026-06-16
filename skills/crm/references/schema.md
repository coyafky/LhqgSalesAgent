# CRM Schema Quick Reference

Use this for cross-skill searches and relation writes. Each skill may still contain its full writable field table.

## Search Fields

| Table | Search purpose | Field name | Field ID |
|---|---|---|---|
| 线索管理 | Customer name | 客户姓名 | `fldC6n9VPy` |
| 线索管理 | Phone | 电话 | `fldYJlqFkx` |
| 跟进记录 | Customer name | 客户名称 | `fld8wfwVkS` |
| 报价表 | Customer name | 客户姓名 | `fldyNnSamc` |
| 客户车辆档案表 | Customer name | 客户名称 | `fld1lpoKfI` |
| 产品项目表 | Product name | 产品名字 | `fldEOYqkRO` |

## Relation Field Rules

| Source table | Field | Target table | Value shape |
|---|---|---|---|
| 线索管理 | 销售负责人 | 销售人员表 | `[{"id":"recXXX"}]` |
| 跟进记录 | 线索 | 线索管理 | `[{"id":"recXXX"}]` |
| 跟进记录 | 跟进人 | Feishu user | `[{"id":"ou_xxx"}]` |
| 跟进记录 | 销售人员表 | 销售人员表 | `[{"id":"recXXX"}]` |
| 报价表 | 报价项目 | 产品项目表 | `[{"id":"recXXX"}]` |
| 报价表 | 来源线索 | 线索管理 | `[{"id":"recXXX"}]` |
| 报价表 | 报价人 | 销售人员表 | `[{"id":"recXXX"}]` |
| 报价表 | 客户档案 | 客户车辆档案表 | `[{"id":"recXXX"}]` |
| 客户车辆档案表 | 销售负责人 | Feishu user | `[{"id":"ou_xxx"}]` |
| 客户车辆档案表 | 销售人员表 | 销售人员表 | `[{"id":"recXXX"}]` |
| 工单表 | 客户 | 客户车辆档案表 | `[{"id":"recXXX"}]` |
| 工单表 | 来源报价 | 报价表 | `[{"id":"recXXX"}]` |
| 工单表 | 施工项目 | 产品项目表 | `[{"id":"recXXX"}]` |
| 工单表 | 销售负责人 | 销售人员表 | `[{"id":"recXXX"}]` |
| 工单表 | 施工师傅 | Feishu user | `[{"id":"ou_xxx"}]` |
| 工单表 | 施工师傅表 | 施工师傅表 | `[{"id":"recXXX"}]` |
| 售后表 | 客户 | 客户车辆档案表 | `[{"id":"recXXX"}]` |
| 售后表 | 原工单 | 工单表 | `[{"id":"recXXX"}]` |
| 售后表 | 负责销售 | 销售人员表 | `[{"id":"recXXX"}]` |

## Field Value Shapes

- Single select: write the option name string, for example `"已成交"`.
- Multi select: write an array of option names, for example `["隐形车衣","窗膜"]`.
- Relation: write an array of record objects, for example `[{"id":"recXXX"}]`.
- Person: write an array of Feishu user objects, for example `[{"id":"ou_xxx"}]`.
- Number/currency: write numeric JSON values, not strings.
