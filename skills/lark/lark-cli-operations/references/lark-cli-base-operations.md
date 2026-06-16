# Base 多维表格操作参考

## 创建 Base

```bash
lark-cli base +base-create \
  --name "台账名称" \
  --time-zone Asia/Shanghai \
  --as bot \
  --format pretty
```

**关键返回：** `base_token` 和 `url`。
新建 Base 自带 1 张默认表和 5~10 条空记录。

---

## 查看表结构

### 表列表

```bash
lark-cli base +table-list --base-token "<base_token>" --as bot
```

### 字段列表

```bash
lark-cli base +field-list \
  --base-token "<base_token>" \
  --table-id "<table_id>" \
  --offset 0 \
  --limit 100 \
  --as bot
```

---

## 写入记录

### 单条写入/更新

```bash
lark-cli base +record-upsert \
  --base-token "<base_token>" \
  --table-id "<table_id>" \
  --json '{"字段名称":"值","数字字段":123}' \
  --as bot
```

### 批量写入

```bash
lark-cli base +record-batch-create \
  --base-token "<base_token>" \
  --table-id "<table_id>" \
  --json '[
    {"字段1":"值1","字段2":"值2"},
    {"字段1":"值3","字段2":"值4"}
  ]' \
  --as bot
```

---

## 搜索记录

```bash
lark-cli base +record-search \
  --base-token "<base_token>" \
  --table-id "<table_id>" \
  --keyword "搜索关键词" \
  --search-field "字段名称" \
  --as bot
```

---

## CRM 专用

参考 `crm-natural-language-entry` 技能获取详细 CRM 字段映射和表设计。
