---
name: crm-quote-entry
description: 有膜有漾 CRM 报价 — 销售说一句报价信息，助理搜索线索和产品，写入「报价表」并关联相关记录
requires:
  - lark-base
base:
  base_url: https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8
  base_token: Q6VQbuLTOaPP5VspfKXc7ZbTnA8
  table: 报价表
  table_id: tblzGNVSFPSXgb9K
---

# CRM报价助手

## 概述

销售跟客户沟通后，用一句话描述报价信息，助理自动搜索线索、匹配产品项目、填入价格信息，写入「报价表」并关联线索、产品和销售人员。

## 共享引用

执行前按需读取：

- `../references/intent-matching.md` — 确认当前请求是否明确是报价、成交、收款或退款意图。
- `../references/base.md` — Base token、身份、日期格式、确认边界。
- `../references/schema.md` — 来源线索、报价项目、报价人、客户档案等关联字段格式。
- `../references/idempotency.md` — 新报价、更新报价、成交更新的查重和 record_id 规则。
- `../references/people-products.md` — 销售人员和产品查找。

**目标表：** 报价表（`tblzGNVSFPSXgb9K`）
**关联表：**
- 产品项目表（`tblbfqLLrnxyOMIt`）— 通过「报价项目」字段关联
- 线索管理（`tblHsrpSsTmJnB0c`）— 通过「来源线索」字段关联
- 销售人员表（`tblhP4v00FNjYQnm`）— 通过「报价人」字段关联
- 客户车辆档案表（`tblV6qrgb7Xef1N7`）— 通过「客户档案」字段关联（成交后）
**Base token：** `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
**身份：** `--as bot`

## ⚡ 快速识别意图（触发条件）

当销售说以下内容时触发本 skill：

| 销售说 | 识别关键词 |
|--------|-----------|
| *给王先生报价，青龙YM-65，9800* | **报价/报个价/给…报价** |
| *王先生问界M9，报白虎+芒种，打包21800* | **报…/报价方案** |
| *成交了，王先生青龙YM-65，成交价9500，已收定金3000* | **成交/定了/付款** |
| *更新报价，王先生青龙YM-65改成9500* | **更新报价/改价** |

### 与 CRM 其他技能的区分

| 说这个 → 走哪个 | 示例 |
|----------------|------|
| 线索录入 | 吕佳豪，王先生问界M9电动踏板抖音来的 |
| 跟进记录 | 今天跟王先生聊了，说价格高要商量 |
| **报价** | **给王先生报价，青龙YM-65，9800** |
| **成交** | **王先生定了，青龙YM-65，成交9500** |

## 产品项目表（关联数据）

销售说产品名时，自动匹配以下产品：

| 产品名字 | 产品编码 | 类型 | record_id |
|---------|---------|------|-----------|
| 貔貅YM-60 | PPF-001 | 隐形车衣 | `rech1WaVpweqay` |
| 青龙YM-65 | PPF-002 | 隐形车衣 | `recjLnrBe01OFc` |
| 白虎YM-70 | PPF-003 | 隐形车衣 | `recdXoL73LwqG3` |
| 朱雀YM-80 | PPF-004 | 隐形车衣 | `recgTtiAqWaLwu` |
| 玄武YM-80Y | PPF-005 | 隐形车衣 | `recPGuPc4Z3zc6` |
| 麒麟YM-10 | PPF-006 | 隐形车衣 | `recLpnHSmysMpF` |
| 凤凰YM-100 | PPF-007 | 隐形车衣 | `recZpkvkKl5KgU` |
| 烛龙YM-1000 | PPF-008 | 隐形车衣 | `recSEBl54NJu6Y` |
| 春分套餐K7+C15 | WIN-001 | 窗膜 | `rec7d8medsnoHl` |
| 谷雨套餐T7+F20 | WIN-002 | 窗膜 | `recbayMPeHB0li` |
| 芒种套餐Z70+Z20 | WIN-003 | 窗膜 | `recLoZCXtsZfCR` |
| 小满套餐Z70+K15 | WIN-004 | 窗膜 | `recDjeb1KY8pZ2` |
| 白露套餐Z80+Z20 | WIN-005 | 窗膜 | `recOq2R9NtVJY9` |
| 网红套餐G7 | WIN-006 | 窗膜 | `recs4iIfqrSYHT` |
| 养生套餐M7+N20 | WIN-007 | 窗膜 | `recdTXsPjs0vjQ` |

> 匹配不到产品时，搜索产品项目表：`+record-search --search-field fldEOYqkRO --keyword "产品名"`

## 报价表字段

### 可写字段

| 字段名 | 字段 ID | 类型 | 必填 | 写入规则 |
|--------|---------|------|:----:|----------|
| 客户姓名 | fldyNnSamc | 文本 | ✅ | 从线索/客户名称填入 |
| 手机号 | fld3IfeGL6 | 电话 | ✅ | 从线索获取 |
| 车辆品牌 | fldDcCh5Mc | 文本 | ✅ | 从线索获取 |
| 车辆型号 | fldvTY3mqY | 文本 | ✅ | 具体车型，如问界M9 |
| 报价金额 | fldHUfuUqV | 数字（货币） | ✅ | 报给客户的价格 |
| 报价方案说明 | fldjujjUu4 | 文本 | ✅ | 含什么产品、套餐说明 |
| 报价状态 | fldSUDMmcw | 单选 | ✅ | 草稿/已发客户/跟进中/已成交/已作废 |
| 报价项目 | fld3gHVPCm | **关联** → 产品项目表 | ✅ | `[{"id": "recXXX"}]` 产品 record_id |
| 来源线索 | fldYquJq3d | **关联** → 线索管理 | ✅ | `[{"id": "recXXX"}]` 线索 record_id |
| 报价人 | fldaPdLFw7 | **关联** → 销售人员表 | ✅ | `[{"id": "recXXX"}]` 销售 record_id |
| 车牌号 | fldkmRBkaR | 文本 | 否 | 有则填 |
| 成交金额 | fld6KPdPjP | 数字（货币） | 条件必填 | 报价状态=已成交时必填 |
| 成交日期 | fld047b1uT | 日期时间 | 条件必填 | 报价状态=已成交时必填 |
| 收款状态 | fld7sVhT3X | 单选 | 条件必填 | 报价状态=已成交时必填 |
| 已收金额 | fldf5Cpafe | 数字（货币） | 条件必填 | 有收款时填 |
| 收款方式 | flddioi9ch | 单选 | 条件必填 | 微信/支付宝/银行转账/现金/其他 |
| 客户档案 | fldSXIrE0b | **关联** → 客户车辆档案表 | 条件必填 | 成交后关联档案 |
| 跟进记录 | fldU7ZM9SF | **关联** → 跟进记录表 | 否 | 可选关联 |

### 只读字段

报价编号（自动编号）、未收金额（公式=成交金额-已收金额）、报价附件（走专用命令）

### 报价状态选项

草稿 → 已发客户 → 跟进中 → 已成交 / 已作废

### 报价状态映射

| 销售说 | 映射为 |
|--------|--------|
| 刚报/还没发/草稿 | 草稿 |
| 发给客户了/报价已发 | 已发客户 |
| 在谈/客户在考虑/跟进中 | 跟进中 |
| 定了/成交了/客户同意/付款了 | 已成交 |
| 客户不要了/过期/作废 | 已作废 |

### 收款状态映射

| 销售说 | 映射为 |
|--------|--------|
| 还没收/未付款 | 未收款 |
| 交了定金/付了定金 | 已收定金 |
| 全款付清/付完了 | 已收全款 |
| 付了部分/还有尾款 | 有尾款 |
| 退了/退款了 | 已退款 |

## 工作流程

### 第一步：搜索客户 → 获取线索

1. 按客户姓名在**线索管理**搜索：`+record-search --search-field fldC6n9VPy --keyword "王" --as bot`
2. 获取线索 record_id，用于「来源线索」字段
3. 从线索中提取：客户姓名、手机号、车辆品牌

### 第二步：匹配产品

1. 从销售说的话中提取产品名（如"青龙YM-65""白虎YM-70+芒种"）
2. 在产品项目表中搜索匹配：`+record-search --search-field fldEOYqkRO --keyword "青龙" --as bot`
3. 获取产品 record_id，用于「报价项目」字段
4. 如有多产品（车衣+窗膜套餐），取多个 record_id

### 第三步：解析报价信息

- 价格数字 → 报价金额
- 产品名+服务说明 → 报价方案说明
- 状态关键词 → 报价状态
- 成交关键词 → 成交金额/成交日期/收款状态

### 第四步：追问缺失（最多3个）

按优先级：
1. 报价金额
2. 报价项目（什么产品？）
3. 报价状态（发出去了还是客户定了？）

### 第五步：确认摘要

```markdown
📋 准备写入 CRM — 报价表

| 字段 | 值 |
|------|-----|
| 客户 | XXX（关联线索：recXXX） |
| 手机号 | XXX |
| 车辆 | XXX XXX |
| 报价项目 | XXX（产品ID：recXXX） |
| 报价金额 | ¥XXX |
| 报价方案 | XXX |
| 报价状态 | XXX |
| 报价人 | XXX |

请回复「确认写入」后我写入 CRM。
```

### 第六步：写入

先按 `../references/idempotency.md` 判断是新建报价还是更新现有报价。成交、收款、退款等状态变更必须更新明确的报价 `record_id`，不得按客户名盲目覆盖。

```bash
lark-cli base +record-upsert \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblzGNVSFPSXgb9K \
  --json '{
    "客户姓名":"王先生",
    "手机号":"17620770627",
    "车辆品牌":"问界",
    "车辆型号":"问界M9",
    "报价金额":9800,
    "报价方案说明":"青龙YM-65隐形车衣，含天窗",
    "报价状态":"已发客户",
    "报价项目":[{"id":"recjLnrBe01OFc"}],
    "来源线索":[{"id":"recvmz6aD0wfTq"}],
    "报价人":[{"id":"rec6gBu3IVdtim"}]
  }' \
  --as bot
```

成交时补充收款信息：

```bash
lark-cli base +record-upsert \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblzGNVSFPSXgb9K \
  --record-id <已有报价记录ID> \
  --json '{
    "报价状态":"已成交",
    "成交金额":9500,
    "成交日期":"2026-06-15 00:00:00",
    "收款状态":"已收定金",
    "已收金额":3000,
    "收款方式":"微信"
  }' \
  --as bot
```

### 第七步：验证回读

```bash
lark-cli base +record-get \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblzGNVSFPSXgb9K \
  --record-id <新记录ID> \
  --as bot
```

## 销售一句话示例

| 销售说 | 解析结果 |
|--------|----------|
| *给王先生报价，青龙YM-65，9800* | 报价项目:青龙YM-65 / 报价金额:9800 / 状态:草稿 |
| *王先生发了报价，白虎YM-70车衣+芒种窗膜，打包21800* | 报价项目:白虎+芒种 / 报价金额:21800 / 状态:已发客户 |
| *王先生定了，青龙YM-65，成交9500，微信付了定金3000* | 状态:已成交 / 成交金额:9500 / 收款:已收定金3000 |
| *更新王先生报价，白虎YM-70改成19800* | 更新已有报价 / 调整金额为19800 |

## 安全规则

- 遵守 `../references/base.md` 的金额确认边界。
- 遵守 `../references/idempotency.md`：报价新建和成交更新必须区分。
- 写入前必须找到对应线索和产品，无法确认时先追问。
- 没有销售确认，不直接写入。
- 不凭空编造价格、折扣。
- 成交金额、收款信息必须由销售明确提供。
- 报价中的价格以销售口述为准，不从产品表自动取价（价格可变）。

## 关联 Skill

- `crm-lead-entry`（CRM线索录入助手）— 先有线索才能报价
- `crm-followup-entry`（CRM跟进记录助手）— 报价前后记录跟进
- `lark-base` — 实际 Base 操作
- `handle-film-objections` — 客户对报价有异议时参考话术
