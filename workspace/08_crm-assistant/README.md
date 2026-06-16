# CRM 表销售填写助理

这个模块定义一个面向销售人员的 CRM 表填写 assistant：销售不需要逐格找字段，只要用自然语言描述客户情况，assistant 负责解析、追问缺失信息、映射字段、生成确认摘要，并在确认后写入飞书多维表格。

## 接入状态（✅ 已就绪）

- **正确的 Base：** `https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- **Base token：** `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- **目标表：** 线索管理（`tblHsrpSsTmJnB0c`）
- **关联表：** 销售人员表（`tblhP4v00FNjYQnm`）、跟进记录表（`tblx0u6u4N1Vv2vY`）
- **角色：** 所有操作使用 `--as bot` 身份

## 目标体验

销售输入：

```text
今天小王加了一个理想 L7 客户，想贴车衣，主要怕高速石子和鸟粪，预算中等，约了周六到店看样膜，微信已经加上了。
```

Assistant 输出：

```markdown
我识别到这是一条新线索：

- 客户称呼：小王
- 车型：SUV（理想 L7）
- 产品意向：隐形车衣
- 主要诉求：高速石子、鸟粪、漆面保护
- 预算：中等
- 当前阶段：待跟进
- 下一步：周六到店看样膜

还缺 2 个字段：
1. 客户手机号或微信备注
2. 来源渠道

确认后我可以写入 CRM 表。
```

## 工作流

1. 解析自然语言，提取客户、车辆、需求、阶段、跟进时间、负责人等信息。
2. 对照 CRM 字段映射（见 `field-mapping.md`），判断哪些字段可直接填写。
3. 对必填缺失字段做最多 3 个追问。
4. 搜索重复客户（按电话→客户名+车型）。
5. 生成「写表前确认摘要」。
6. 销售确认后写入 CRM 表。
7. 返回记录 ID 和下一步跟进建议。

## 相关文档

| 文件 | 用途 |
|------|------|
| `crm-system-reference.md` | 📖 CRM 系统说明书（表结构·字段·关联·写规则） |
| `field-mapping.md` | 字段映射表，含标准化规则和销售负责人 ID |
| `natural-language-examples.md` | 自然语言填写示例 |
| `销售一句话录线索指南.md` | 销售速查卡，一句话录客户 |
| `销售一句话记跟进指南.md` | 销售速查卡，一句话记跟进 |
| `销售一句话报价指南.md` | 销售速查卡，一句话报价/成交 |
| `销售一句话建档指南.md` | 销售速查卡，一句话建客户档案 |
| `销售一句话下工单指南.md` | 销售速查卡，一句话下工单 |
| `销售一句话售后指南.md` | 销售速查卡，一句话记售后 |
| `data-quality-rules.md` | CRM 数据质量规则 |
| `prd-crm-natural-language-entry.md` | 产品需求文档 |
| `sdd-crm-write-workflow.md` | 写入规范 |

## Hermes Skill

已创建对应 skill：

| `skills/crm/crm-lead-entry`（CRM线索录入助手） | 自然语言→线索管理表 |
| `skills/crm/crm-followup-entry`（CRM跟进记录助手） | 自然语言→跟进记录表 |
| `skills/crm/crm-quote-entry`（CRM报价助手） | 自然语言→报价表（含产品匹配） |
| `skills/crm/crm-archive-entry`（CRM客户档案助手） | 自然语言→客户车辆档案表 |
| `skills/crm/crm-workorder-entry`（CRM工单助手） | 自然语言→工单表（关联报价+师傅） |
| `skills/crm/crm-after-sales-entry`（CRM售后助手） | 自然语言→售后表（关联客户+工单） |
| `skills/crm/crm-analytics`（CRM店长数据分析助手） | 一句话问经营→聚合查询7张表→运营报告 |

销售在 Hermes 中说出「录客户」「写 CRM」「新增线索」等指令时，自动触发该 skill。

## 边界

- 没有销售确认，不直接写入 CRM。
- 不凭空补手机号、预算、成交金额、门店、负责人。
- 对同名客户或同一手机号疑似重复时，先提示可能重复记录。
- 不把客户隐私写入 workspace 文档；真实客户信息只进入 CRM 表。
- 不编造价格、折扣或活动政策。
