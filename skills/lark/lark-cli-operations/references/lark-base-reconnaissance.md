# Base 逆向分析 / 全貌侦察 SOP

**适用场景：** 拿到一个未知 Base（多维表格）的链接时，需要全面了解其结构：包含哪些表、每张表的字段与关联关系、视图配置、自动化 Workflow、仪表盘、数据样本以及业务流转逻辑。

**前置条件：** 已安装官方 `lark-base` 技能（`npx skills add larksuite/cli -y -g`）。先加载 `skill_view(name='lark-base')` 了解基础命令。

---

## 0. 前置：从 URL 定位 Base Token

用户给的链接类型不同，提取 Base Token 的方式不同：

| 链接格式 | 操作 | Token 位置 |
|----------|------|------------|
| `/base/{token}` | 直接提取 | `{token}` 就是 `--base-token` |
| `/wiki/{token}` | 先 `wiki +node-get` 判断 obj_type | `data.obj_token` 当 `data.obj_type=bitable` 时 |
| `/base/{token}?table={tblId}` | 提取 base token | `{token}` 用 `--base-token`，参数 `tbl` 用 `--table-id` |
| 只有名称/关键词 | `drive +search --query <keyword> --doc-types bitable --only-title` | 从搜索结果获取 |

### ⚠️ 重要陷阱：wiki token 解析

`wiki +node-get` 只传裸 token（`KDen...`）不带 URL 时会报错要求 `--obj-type`。两种正确做法：
- 传**完整 URL**（`https://.../wiki/KDen...`）让 CLI 自动推断类型
- 或显式传 `--obj-type bitable`

### ⚠️ 身份陷阱

本 profile 已锁定 `--as bot`，所有 lark 命令必须用 `--as bot`。`--as user` 会直接失败。

---

## 1. 第一步：获取 Base 本体信息

```bash
lark-cli base +base-get --base-token <token> --as bot --format json
```

返回：Base 名称、owner、权限、版本等。确认 Base 名称和可继续操作的 token。

---

## 2. 第二步：列出所有数据表

```bash
lark-cli base +table-list --base-token <token> --as bot --format json
```

返回 `data.tables` 数组，每项包含 `{id, name}`。记录每张表的 `table_id` 和名称。

### ⚠️ 陷阱：不要用 `+base-block-list`

`+base-block-list` 需要的 `base:block:read` scope 可能未授权，会报 `99991672` 错误。`+table-list` 是更可靠的表查询入口。

---

## 3. 第三步：逐一分析每张表的字段结构

每张表执行：

```bash
lark-cli base +field-list --base-token <token> --table-id <table_id> --as bot --format json
```

### 3.1 重点关注字段类型

| 字段类型 | 关键返回字段 | 意义 |
|----------|-------------|------|
| `link` | `link_table`, `bidirectional` | **跨表关联关系** — 这是分析 Base 架构的核心 |
| `select` | `options[]` (name/hue/lightness) | 选项枚举值 |
| `lookup` | 只读，无特殊配置 | 从关联表读取的派生字段 |
| `formula` | 只读 | 公式计算结果 |
| `user` | `multiple: true/false` | 人员字段 |
| `attachment` | — | 附件字段 |
| `auto_number` | `style.rules` (length, type) | 自动编号配置 |

### 3.2 批量查询（5 张以上表时推荐）

```bash
for tid in tblXXX tblYYY tblZZZ; do
  echo "=== TABLE: $tid ==="
  lark-cli base +field-list --base-token <token> --table-id $tid --as bot --format json | \
    jq '.data.fields[]? | {name, type, link_table: (.link_table // null)}'
  echo ""
done
```

### 3.3 建立关联图谱

分析完所有表后，汇总 `link` 字段找出关联关系网络：
- 哪些表之间有关联（双向/单向）
- 哪些是中心表（被最多表引用）
- 哪些是字典/配置表（只被引用）

---

## 4. 第四步：查看视图配置

对核心业务表执行：

```bash
lark-cli base +view-list --base-token <token> --table-id <table_id> --as bot --format json
```

关注：
- 视图名称和类型（grid / kanban / calendar / gantt / form）
- `_meta` 中的 filter / group / sort 条件
- 带 `(dashboard_view)` 后缀的视图（被仪表盘引用）

---

## 5. 第五步：查看自动化 Workflow

```bash
lark-cli base +workflow-list --base-token <token> --as bot --format json
```

返回 `items` 数组，关注：
- `title`（名称）、`trigger_type`（`SetRecordTrigger` = 记录变更触发）、`status`（enabled/disabled）

### 5.1 查看 Workflow 详细步骤

```bash
lark-cli base +workflow-get --base-token <token> --workflow-id <wkf_id> --as bot --format json
```

### ⚠️ 陷阱：用 Python 解析而非 jq

`+workflow-get` 返回的 JSON 结构复杂，steps 数组内的 config 嵌套深。直接用 jq 取 steps 类型：

```bash
jq '.data.steps[]?.type'
```

但解析完整 config 推荐用 Python：

```python
import json, sys
data = json.load(sys.stdin)
steps = data.get('data', {}).get('steps', [])
for s in steps:
    print(s.get('type'), list(s.get('config', {}).keys()))
```

常见模式：`SetRecordTrigger` → `LarkMessageAction`（记录变更触发 → 发飞书通知）。

---

## 6. 第六步：查看仪表盘

```bash
lark-cli base +dashboard-list --base-token <token> --as bot --format json
```

返回 `items` 数组，每项含 `dashboard_id` 和 `name`。

如需查看仪表盘内部组件：

```bash
lark-cli base +dashboard-block-list --base-token <token> --dashboard-id <blk_id> --as bot --format json
```

---

## 7. 第七步：采样数据

```bash
lark-cli base +record-list --base-token <token> --table-id <table_id> --as bot --format json
```

### ⚠️ 理解返回格式

`+record-list` 的字段顺序与 `+field-list` 输出顺序一致。返回值在 `data.data`（**不是** `data.records`），是二维数组：

```json
{
  "data": {
    "data": [
      [val_for_field1, val_for_field2, ...],  // 记录1
      [val_for_field1, val_for_field2, ...],  // 记录2
    ]
  }
}
```

值类型对应：
- `text` → 字符串或 null
- `user` → `[{"id": "ou_xxx", "name": "姓名"}]`
- `select` → `["选项名"]` 或 null
- `datetime` → `"YYYY-MM-DD HH:mm:ss"`
- `number` → 数字或 null
- `link` → 关联 record_id 数组
- `attachment` → 附件信息数组

### ⚠️ 陷阱

- **空行问题：** `data.data` 可能包含 `[null, null, ...]` 行（只有系统字段无用户数据）
- **列标头对照：** 必须用 field-list 的输出顺序作为列标头解析记录数组。字段 ID 或名字排序不能代替。

---

## 8. 第八步：提取业务逻辑规则

如果 Base 中有"状态流转规则表"或相似名字的配置表，采样全部记录：

```bash
lark-cli base +record-list --base-token <token> --table-id <rules_table_id> --as bot --format json
```

典型规则表字段：
- 对象（线索/报价/工单/施工/财务/售后）
- 操作人角色（销售/店长/师傅/财务/系统自动）
- 触发动作 / 当前状态 / 下一状态
- 前置条件 / 系统自动动作 / 规则说明

从这些规则可以还原完整**状态机流程图**。

---

## 9. 信息整合输出

最终报告应覆盖以下维度：

| 维度 | 内容 |
|------|------|
| Base 元信息 | 名称、创建者、创建时间、最后编辑时间 |
| 数据表 | 表名称列表 + 每张表的字段概要 |
| 关联关系 | 表间 link 图谱，标示中心表和字典表 |
| 视图配置 | 视图名称、类型、筛选/分组/排序概要 |
| 自动化流程 | Workflow 名称、触发器、启停状态、步骤类型 |
| 仪表盘 | 仪表盘名称和用途推测 |
| 状态流转 | 从规则表还原的完整状态机 |
| 业务全景 | 从线索获取到售后闭环的流程图 |

---

## 📌 快速检查清单

- [ ] 已从 URL 正确解析 base_token（区分 wiki token 和 base token）
- [ ] 已通过 `+table-list` 获得所有表名和表 ID
- [ ] 已通过 `+field-list` 分析每张表字段（特别是 link/select/lookup/formula）
- [ ] 已汇总 link 关系，绘制表间关联图
- [ ] 已查看核心业务表的视图配置
- [ ] 已查看所有 Workflow（启停状态、触发器、步骤类型）
- [ ] 已查看仪表盘
- [ ] 已从关键表采样数据，理解记录值格式
- [ ] 如果存在规则表，已提取全部状态流转规则
- [ ] 最终输出覆盖"数据→流程→自动化"三要素

---

## 在本次 session 中验证的完整流程（有膜有漾 CRM 案例）

本次 session 对一个 10 表、7 Workflow、2 仪表盘的 Base 进行了完整侦察，验证了本 SOP 全流程的可行性：

1. `wiki +node-get` → 识别为 bitable → 提取 base_token
2. `+table-list` → 发现 10 张表（员工角色/线索/报价/产品/客户档案/工单/施工/财务/售后/状态流转规则）
3. `+field-list` × 10 → 识别 100+ 字段、link 关联、选项枚举、lookup/formula 派生字段
4. `+view-list` → 线索表 11 个视图（含 calendar/kanban/query 类型）
5. `+workflow-list` → 6 个已启用 + 1 个已停用 Workflow
6. `+dashboard-list` → 线索管理 + 门店运营 2 个仪表盘
7. `+record-list` → 从线索表、规则表采样真实数据
8. 从规则表提取 25 条状态流转规则 → 还原完整状态机
9. 输出综合报告：表结构、关联、视图、Workflow、状态机、业务全景图
