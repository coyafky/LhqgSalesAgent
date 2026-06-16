# CRM 通用字段写规则

> 所有 CRM skill 共享的字段写入规范。Base token: `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`，身份：`--as bot`

## 字段类型与写入格式

| 字段类型 | 写入格式 | 示例 |
|---------|---------|------|
| 文本 | 字符串 | `"王先生"` |
| 电话 | 字符串 | `"17628889999"` |
| 数字/货币 | 数字（不带¥） | `9800` |
| 单选 | 选项名字符串 | `"已分配"`、`"SUV"` |
| 多选 | 选项名数组 | `["轻改装"]`、`["隐形车衣","窗膜"]` |
| 日期时间 | `"YYYY-MM-DD HH:mm:ss"` | `"2026-06-15 00:00:00"` |
| 人员（user） | `[{"id": "ou_xxx"}]` | `[{"id":"ou_1c91ab71d9b6714030442cb1c6b85457"}]` |
| 关联（link） | `[{"id": "recXXX"}]` 目标表 record_id | `[{"id":"rec6gBu3IVdtim"}]` |

## 关键注意事项

### 1. 销售负责人字段类型因表而异

| 表 | 字段名 | 字段类型 | 写入方式 |
|---|--------|---------|---------|
| 线索管理 | 销售负责人 | **关联** → 销售人员表 | record_id |
| 跟进记录 | 跟进人 | **人员** | open_id |
| 跟进记录 | 销售人员表 | **关联** → 销售人员表 | record_id |
| 报价表 | 报价人 | **关联** → 销售人员表 | record_id |
| 客户档案 | 销售负责人 | **人员** | open_id |
| 客户档案 | 销售人员表 | **关联** → 销售人员表 | record_id |
| 工单表 | 施工师傅 | **人员** | open_id |
| 工单表 | 销售负责人 | **关联** → 销售人员表 | record_id |
| 售后表 | 负责销售 | **关联** → 销售人员表 | record_id |
| 售后表 | 店长/处理人 | **人员** | open_id |

**⚠️ 写入前先用 `+field-list` 确认字段类型，不要凭字段名猜测。** 同名"销售负责人"在不同表中可能是不同类型。

### 2. 关联字段要用 record_id

所有 `link` 类型字段用 `[{"id": "recXXX"}]` 格式，不是字段名也不是标题。

例如线索管理的「销售负责人」字段：
- ❌ `"吕佳豪"` — 错误，不是文本字段
- ❌ `[{"id":"ou_xxx"}]` — 错误，这是人员字段格式
- ✅ `[{"id":"rec6gBu3IVdtim"}]` — 正确，销售人员表 record_id

### 3. 只读字段不要写

| 类型 | 说明 |
|------|------|
| `created_at` / `updated_at` | 自动时间戳 |
| `created_by` / `updated_by` | 自动记录人 |
| `auto_number` | 自动编号 |
| `formula` | 公式计算结果 |
| `lookup` | 跨表查找结果 |
| `not_support` | 不支持 API 操作 |

写入只读字段会导致 `ignored_fields` 响应，不会报错但也不会生效。

### 4. 必填字段要保证

写入前确认必填字段不为空。各表的必填字段见 `crm-system-reference.md`。

### 5. 选项值要精确

`select` 字段的值必须与表中选项**完全一致**（区分大小写、全角半角）。

```bash
# 写入前确认可用选项
lark-cli base +field-list --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --table-id <table_id> --as bot
```

未知选项名写入时，平台可能会自动新增选项，因此不要把近义词当成已有选项传入。

## 跨表关联总图

```
线索管理.销售负责人    [link] → 销售人员表.record_id
     ↑
跟进记录.线索          [link] → 线索管理.record_id
跟进记录.跟进人        [user] → 飞书 open_id
     ↑
报价表.来源线索        [link] → 线索管理.record_id
报价表.报价项目        [link] → 产品项目表.record_id
报价表.报价人          [link] → 销售人员表.record_id
报价表.客户档案        [link] → 客户车辆档案表.record_id
     ↑
客户档案.销售负责人     [user] → 飞书 open_id
客户档案.销售人员表     [link] → 销售人员表.record_id
     ↑
工单表.客户            [link] → 客户车辆档案表.record_id
工单表.来源报价         [link] → 报价表.record_id
工单表.施工项目         [link] → 产品项目表.record_id
工单表.施工师傅         [user] → 飞书 open_id
工单表.销售负责人       [link] → 销售人员表.record_id
     ↑
售后表.客户            [link] → 客户车辆档案表.record_id
售后表.原工单           [link] → 工单表.record_id
售后表.负责销售         [link] → 销售人员表.record_id
```
