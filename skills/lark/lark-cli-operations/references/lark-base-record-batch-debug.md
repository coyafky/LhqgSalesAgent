# 批量创建记录：错误调试与跨表链接构造（lark-cli base）

## 适用场景

使用 `+record-batch-create` 或 `+record-upsert` 时遇到以下错误：

- `code: 800030005, message: "not_found"` — select 选项值不存在
- `code: 800030201, message: "not_found"` — 字段名不匹配或值非法
- `code: 1254015` — 字段值类型不匹配
- 写入成功但 `ignored_fields` 中有 READONLY 字段被跳过

## 错误诊断流程

### 1. 从 detail 定位出错的字段

`+record-batch-create` 的 payload 是 `{"fields": [...], "rows": [[...], ...]}` 格式。
当字段值不合法时，API 返回 `detail` 对象：

| detail 字段 | 含义 |
|-------------|------|
| `path` | 出错索引。`fields.16` = fields 数组第 16 个元素（0-indexed） |
| `value` | 你传入的错误值。可能是字段名或 CellValue |
| `type` | `not_found` = 字段名或选项值不存在 |

**判断规则：**

- `detail.value` 是 fields 数组中的字段名 → 该字段在目标表中不存在
- `detail.value` 是 select 选项值 → 该选项不在字段定义中

### 2. 读 hint 中的可用字段

```
"hint": "The first 5 available fields are: \"fldBG0DbC7(\\\"跟进记录\\\")\", ..."
```

对比 hint 中的字段名定位不匹配项。

### 3. 用 `+field-list` 确认字段结构

```bash
lark-cli base +field-list --base-token <token> --table-id <table> --as bot --format json
```

核心检查项：

- `type`：确认字段类型（text / select / link / user / datetime / number 等）
- select → `options[].name`：唯一可用选项列表
- link → `link_table`：目标表 ID
- `multiple`：true 表示多选

### 4. 常见错误码

| 错误码 | 原因 | 修复 |
|--------|------|------|
| `800030005` | select 值不在 options 中 | 用 `+field-list` 查 options 后重写。注意有的字段（如客户类型）选项为空 |
| `800030201` | 字段名不存在或值非法 | 用 `detail.path` 定位索引，对照 `+field-list` 修正 |
| `1254015` | 值类型不对 | 按 [lark-base-cell-value.md](../../lark-base/references/lark-base-cell-value.md) 重写 |

## 跨表 link 字段写入

### 格式

link 通过 record_id 关联，不传标题/名称：

```json
{
  "客户档案": [{ "id": "recvmr3zLnRG7H" }],
  "销售负责人": [{ "id": "rec6gBu3IVdtim" }]
}
```

- 单值：`[{ "id": "rec_xxx" }]`
- 多值（multiple=true）：`[{ "id": "rec_1" }, { "id": "rec_2" }]`

### 获取目标 record_id

`+record-list` 返回：

```json
{
  "data": {
    "data": [[val1, val2, ...], ...],         // flat arrays
    "record_id_list": ["rec_xxx", "rec_yyy"],  // 按行索引对应
    "field_id_list": ["fld_aaa", "fld_bbb"],
    "fields": ["字段名1", "字段名2"]
  }
}
```

Python 提取映射：

```python
rids = data['data']['record_id_list']
rows = data['data']['data']
for i, rid in enumerate(rids):
    name = rows[i][0]
    print(f'{rid} -> {name}')
```

### 写入顺序（依赖管理）

| 步骤 | 表 | 可被下游关联 |
|------|-----|-------------|
| 1 | 客户档案、产品、人员（无 link 依赖） | 线索、报价、工单 |
| 2 | 线索（→ 销售人员） | 报价、跟进 |
| 3 | 报价（→ 产品+客户+线索+报价人） | 工单 |
| 4 | 工单（→ 客户+报价+项目+师傅） | 售后 |
| 5 | 售后（→ 原工单+客户） | — |

### 空值处理

- 可选 link/user/select/日期 → 传 `null`
- **不传**空字符串 `""` 给 select/user 字段

## 写入后验证

```bash
lark-cli base +record-list --base-token <token> --table-id <table> --as bot --format json | jq '.data.data | length'
lark-cli base +record-get --base-token <token> --table-id <table> --record-id <rid> --as bot --format json
```

## 完整示例

参见 `蓝火改装/有膜有漾-销售知识库/mock_data_generator.py`，演示了：

1. 按依赖顺序创建 6 个表（客户档案→线索→报价→跟进→工单→售后）
2. 创建后收集 record_id 建立映射字典供下游引用
3. 构造正确的 CellValue：link / user / select / datetime / location
4. 处理 select 选项空问题（客户类型字段选项为空）
5. 处理字段名不匹配（线索表中无"一句话进展"字段）
