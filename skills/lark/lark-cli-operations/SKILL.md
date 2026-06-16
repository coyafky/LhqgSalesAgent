---
name: lark-cli-operations
description: lark-cli 飞书 CLI 通用操作路由 — 将各类型飞书操作路由到正确的官方 lark-* 技能，维护本 profile 的身份约定与避坑知识
triggers:
  - 用户要求创建/更新云文档
  - 用户要求创建 Base 多维表格
  - 用户要求授权文档给他人
  - 用户要求查询飞书资源
  - 用户要求发送飞书消息
  - 用户要求搜索通讯录
  - 用户要求分析/侦察/了解一个未知 Base 的结构
  - 用户要求判断一个 Base 是否适配门店业务
  - 用户要求输出 CRM 底表字段文档或改造方案
version: 2.0.0
tags: [lark-cli, feishu, routing, navigation, umbrella]
---

# lark-cli Operations (v2 — Routing Umbrella)

## When to Use

用户说以下任何一句话时触发：

- "帮我创建一个云文档 / 新建文档"
- "把这个文档授权给我 / 给这个人权限"
- "建一个多维表格 / Base"
- "查询飞书 table / field / record"
- "录一条数据到 Base"
- "发消息给客户 / 群聊"
- "查一下这个人的信息"

## Architecture

本 profile 已安装 **26 个官方 lark 技能**（来自 larksuite/cli）。各技能职责明确：

| 官方技能 | 用途 | 触发关键词 |
|:---------|:-----|:----------|
| **`lark-doc`** | 创建/读取/更新/搜索文档 | 文档、doc、云文档、文章 |
| **`lark-drive`** | 文件上传下载、权限管理、评论 | 授权、权限、上传、下载、云盘 |
| **`lark-base`** | 多维表格全操作（字段、记录、视图、Workflow、仪表盘） | Base、多维表格、bitable、台账、分析Base结构、Base侦察 |
| **`lark-cli-operations` → references/lark-base-reconnaissance.md** | **Base 逆向分析 SOP**（本技能专有补充） | 未知 Base 全貌分析、逆向侦察、表结构发现 |
| **`lark-cli-operations` → references/crm-base-archetype-analysis.md** | **CRM 底表类型识别与改造分析 SOP** | CRM 类型判断（门店运营型 vs 销售管道型）、差距分析、字段替换模式、Workflow 启用策略、报告输出规范 |
| **`lark-shared`** | 认证、身份切换、权限 scope | 认证、登录、scope、权限不足 |
| **`lark-wiki`** | 知识库（空间、节点） | 知识库、wiki、知识空间 |
| **`lark-im`** | 消息发送、群聊管理 | 发消息、群聊、聊天、IM |
| **`lark-contact`** | 通讯录、用户查询 | 查人、通讯录、open_id |
| **`lark-calendar`** | 日程、会议室 | 日程、会议、预约、日历 |
| **`lark-sheets`** | 电子表格 | 表格、sheet、excel |
| **`lark-task`** | 待办任务 | 任务、待办、to-do |
| **`lark-mail`** | 邮箱 | 邮件、邮箱、mail |
| **`lark-openapi-explorer`** | 底层 API 探索（无快捷命令时） | 底层、API、官方接口 |

## Workflow

**不要直接在本技能中查命令或拼参数。** 流程如下：

1. **判断用户意图** → 对照上表找到对应的官方 `lark-*` 技能
2. **加载官方技能** → `skill_view(name='lark-xxx')`
3. **遵循官方技能的指引** → 官方技能内有完整的命令示例、参数说明和避坑
4. **应用本 profile 的身份约定**（见下方）
5. **执行前做安全检查**（见下方）

## Identity Convention

- **一律用 `--as bot`。** 本 profile 没有配置 user 身份。
- `--as user` 的操作会失败（`User identity: missing`）。
- 已在 `lark-cli` 中通过 `config bind --identity bot-only` 锁定。

## Safety Rules

| 操作类型 | 安全要求 |
|---------|---------|
| 读操作（list, get, search, fetch） | 无需确认，直接执行 |
| 写操作（create, update, record-upsert） | 需用户确认后再执行 |
| 高风险写（delete, permission members create） | 需用户确认 + 加 `--yes` 标志 |

## Official lark Skills Installation

本 profile 已通过以下命令安装 26 个官方 lark 技能：

```bash
npx skills add larksuite/cli -y -g
```

安装后技能位于 `~/.agents/skills/lark-*`，通过 symlink 链接到 profile 的 `skills/` 目录下。Hermes 会自动识别 SKILL.md 格式。

**如需重新安装或更新：**
```bash
npx skills add larksuite/cli -y -g
```

## Integration Pattern: Learn → Share (本 session 确立)

小米改装技能（`xiaomi-modification-learning`）确立了双阶段工作流模式，可推广到其他产品线：

```
Phase 1: Learn             Phase 2: Share
                           
产品知识学习  ──────────→   ┌─ A: lark-im 发图文给客户
+ 图片展示                  ├─ B: lark-doc 创建文档
+ 对客话术                  └─ C: lark-im 批量发图册
```

应用这个模式时：
1. 先用对应技能完成产品学习
2. 学习阶段输出末尾主动询问："需要发给客户看吗？"
3. 确认后路由到 `lark-im`（发消息）或 `lark-doc`（创建文档）

## Pitfalls (Session-Proven)

这些是本 profile 实际测试中踩过的坑，官方技能可能未覆盖：

### 1. `docs +create` 的 v1 vs v2 API 差异
- **v1（旧，已废弃）**：用 `--markdown`，用 `--title` 传标题
- **v2（推荐）**：用 `--content` 传 XML 格式内容（标题写 `<title>` 标签内），不再用 `--markdown` 和 `--title`
- `lark-doc` 官方 skill 强制要求 `--api-version v2`，先加载它了解 XML 语法

### 2. `drive permission.members create` 是高风险操作
- 不加 `--yes` 会阻塞：`confirmation_required`
- 调用时必须带上 `--yes` 标志

### 3. `docs +create --as bot` 自动尝试授权给当前 CLI 用户
- user 未登录时 → 授权跳过（`permission_grant.status: skipped`）
- 文档仍可用，但用户需在飞书 UI 手动添加权限

### 4. `lark-cli api` 不支持 `--format` 标志
- `lark-cli api` 没有 `--format`，输出默认为 JSON

### 5. shell 转义导致命令失败
- 当 `--content`（XML）或 `--markdown` 中包含 `$()`、引号、反引号时
- 推荐用 Python `subprocess.run([...])` 传参避免 shell 解释

### 6. lark-im `+messages-send --image` 不支持绝对路径
- 用 `--image /Users/xxx/image.png` 会被拒绝
- 正确做法：先 `cd` 到图片所在目录，用相对路径 `--image ./product.png`
- 或用 `lark-cli im images create` 先上传获取 `image_key`

### 7. 官方技能使用 `~/.npm-global/bin/lark-cli` 绝对路径
- 本 profile 中 `lark-cli` 在 PATH 中也可用，无需绝对路径
- 但如果 `lark-cli` 不在 PATH 中，需改为绝对路径

## CRM Skill Suite (Session-Verified 2026-06-15)

This profile has a complete CRM skill suite organized under `skills/crm/`. All CRM operations use `--as bot` identity and the Base token `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`.

### CRM Skills — User-Activated

| Skill | Path | Table | Trigger Keywords |
|-------|------|-------|-----------------|
| **`crm-lead-entry`** (CRM线索录入助手) | `skills/crm/crm-lead-entry` | 线索管理 | 录客户、新增线索、新客户、帮我填 CRM |
| **`crm-followup-entry`** (CRM跟进记录助手) | `skills/crm/crm-followup-entry` | 跟进记录 | 记录跟进、更新跟进、今天聊了、刚联系了 |
| **`crm-quote-entry`** (CRM报价助手) | `skills/crm/crm-quote-entry` | 报价表 | 报价、报个价、成交、定了 |
| **`crm-archive-entry`** (CRM客户档案助手) | `skills/crm/crm-archive-entry` | 客户车辆档案表 | 建档、归档、记录车辆信息 |
| **`crm-workorder-entry`** (CRM工单助手) | `skills/crm/crm-workorder-entry` | 工单表 | 下工单、派工、到店施工、施工中、完工 |
| **`crm-after-sales-entry`** (CRM售后助手) | `skills/crm/crm-after-sales-entry` | 售后表 | 售后、返工、质保、投诉、回访 |
| **`crm-analytics`** (CRM店长数据分析助手) | `skills/crm/crm-analytics` | 聚合查询7张表 | 运营概况、分析、排名、业绩、统计 |

### CRM Hooks — Automatically Scheduled

| Hook | Path | Schedule | Purpose |
|------|------|----------|---------|
| **`crm-sleeping-lead-hook`** (沉睡线索预警) | `skills/crm/crm-sleeping-lead-hook` | Daily 9:30 | 检查7/14/30天未跟进的线索 |
| **`crm-revisit-reminder-hook`** (客户回访提醒) | `skills/crm/crm-revisit-reminder-hook` | Daily 9:00 | 检查3/7/30天前完工的工单 |

### CRM System Reference

Comprehensive documentation of all 7 tables, field mappings, link relationships, and write rules:
`workspace/08_crm-assistant/crm-system-reference.md`

### CRM Write Rules (Universal)

All CRM skills share these rules:
1. **Parse → Confirm → Write**: Always show a confirmation summary before writing. Sales must reply "确认写入".
2. **Missing fields**: Ask at most 3 questions per turn.
3. **Duplicate check**: Search by phone or name+model before creating.
4. **Link fields** use `[{"id": "recXXX"}]` format with the target table's record_id.
5. **User fields** use `[{"id": "ou_XXX"}]` format with Feishu open_id.
6. **Select fields**: Use exact option names (e.g. "抖音", "已分配", "SUV").
7. **Product intent mapping**: 电动踏板→轻改装, 车衣→隐形车衣, 太阳膜→窗膜, 改色→改色膜.
8. **Privacy**: Phone numbers, VIN only in CRM table, never in workspace documents.
9. **Pricing**: Must be explicitly provided by sales, never invented.

## Connects To

- `crm-lead-entry`: CRM线索录入 → 路由到 `lark-base`
- `crm-lead-entry` → `references/crm-base-archetype-analysis.md`: CRM 底表类型分析（了解 Base 结构后再录数据，减少字段名猜错）
- `xiaomi-modification-learning`: 小米改装产品学习 → 可路由到 `lark-im`（发图文给客户）或 `lark-doc`（创建产品文档）
- `ark-seedream-car-preview`: 改色预览图 → 路由到 `lark-doc` 创建文档存储
- `recommend-film-product`: 产品推荐 → 可路由到 `lark-im`（发推荐给客户）
- **所有 26 个官方 `lark-*` 技能**：详见 `skills_list()` 中的 `lark-` 前缀技能

## References

- `references/lark-cli-pitfalls.md` — 错误码对照表和避坑大全（已验证）
- `references/lark-cli-doc-and-permission.md` — 文档/授权速查（旧版，优先用官方 `lark-doc`）
- `references/lark-cli-base-operations.md` — Base 速查（旧版，优先用官方 `lark-base`）
- `references/lark-base-reconnaissance.md` — **Base 逆向分析 / 全貌侦察 SOP**：从零分析未知 Base 的八步流程，含 URL 解析、表字段发现、关联图谱、Workflow、仪表盘、数据采样和规则提取（在本次 session 中已验证）
- `references/crm-base-archetype-analysis.md` — **CRM 底表类型识别与改造分析 SOP**：判断 Base 属于门店运营型还是销售管道型 CRM，做差距分析，输出字段设计文档和改造方案（在本次 session 中验证）
- `references/lark-base-record-batch-debug.md` — **批量创建记录错误调试 SOP**：`+record-batch-create` 报错时的定位方法（`detail.path` / `detail.value`），跨表 link 写入顺序，record_id 映射提取
