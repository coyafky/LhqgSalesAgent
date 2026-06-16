---
name: electric-step-learning
description: Use when sales asks to learn, explain, recommend, or check fitment for electric side steps / 电动踏板, including 双灯款, 单灯款/带灯款, 不带灯款, SUV/MPV/越野 SUV fitment, or customer-facing explanation.
requires:
  - lark-cli
  - lark-shared
connects_to:
  - lark-im
  - lark-doc
  - lark-drive
  - lark-contact
---

# Electric Step Learning

## Overview

Use this skill when 有膜有漾 sales wants to learn or explain 蓝辉轻改电动踏板 products.

The skill turns natural-language requests such as "理想 MEGA 能不能装电动踏板", "双灯和不带灯有什么区别", or "给客户讲一下小米 YU7 电动踏板" into a concise sales learning card using:

- `workspace/04_knowledge/eletric-step/products.json` for structured fitment and style modules.
- `workspace/04_knowledge/eletric-step/style-modules.md` for differences between 单灯款/带灯款、双灯款、不带灯款.
- `workspace/04_knowledge/eletric-step/sales-knowledge.md` and `sales-qa.md` for sales wording and customer decision-chain questions.
- `workspace/04_knowledge/eletric-step/source-boundary.md` for guardrails.

The directory keeps the user-provided spelling `eletric-step`.

## Triggers

Use this skill when the message asks about:

- 电动踏板 / 踏板 / 自动踏板 / 侧踏
- 双灯 / 单灯 / 带灯 / 不带灯
- SUV、MPV、越野 SUV 上下车便利
- 车型适配，例如 理想 MEGA、问界 M9、蔚来 ES8、小米 YU7、方程豹豹 5、仰望 U8
- "这台车能不能装踏板"
- "给客户介绍电动踏板"
- "三种款式怎么区分"
- "把这个踏板产品发给客户"（结合 lark-im 发消息）

## Do Not Use When

- The user asks about car film recommendation only; use `recommend-film-product`.
- The user asks about Xiaomi SU7/YU7 modification accessories other than electric side steps; use `xiaomi-modification-learning`.
- The user asks for CRM writing; use `crm-natural-language-entry`.

## Workflow: Learn → Recommend → Share

### Phase 1: 学习与查询

1. Parse the query.
   - If it includes a vehicle brand/model, check fitment first.
   - If it includes 双灯、单灯、带灯、不带灯, explain the style module.
   - If it is broad, explain the three modules and target customer scenarios.
2. Run the bundled script:

```bash
python3 skills/electric-step-learning/scripts/explain.py "理想 MEGA 能不能装电动踏板"
```

3. Return the script output, then adjust wording for the sales context if needed.
4. If image files exist under `workspace/04_knowledge/eletric-step/Image/`, include `MEDIA:/absolute/path/to/image.jpg`.
5. If image files are still missing, say clearly that the product image source file is not yet in the knowledge base.

### Phase 2: 对客推荐

When recommending to a customer, follow this order:

1. Confirm vehicle model and year/configuration if needed.
2. Confirm main pain point: 家人上下车、老人小孩、商务接待、越野车高底盘、夜间识别、预算克制.
3. Recommend style:
   - 单灯款 / 带灯款：实用 + 夜间识别，适合大多数家庭和商务用户。
   - 双灯款：迎宾感更强，适合中大型 SUV/MPV 或更重视展示效果的客户。
   - 不带灯款：更低调，适合只解决上下车便利和预算更克制的客户。
4. State boundaries:
   - 承重、防水、质保按知识库资料表达，不扩展承诺。
   - 价格、库存、施工工时、安装方案、具体质保范围，以门店确认为准。

### Phase 3: 分享给客户（Share）

学习完成后，如果销售想把产品信息发给客户，使用以下方式：

#### 方式 A: 通过 lark-im 发送图文消息给客户

先加载 `lark-im` skill 了解完整的安全规则和参数，然后：

```bash
# 发送产品图文消息给客户（单聊）
lark-cli im +messages-send \
  --user-id ou_xxx \
  --markdown $'## 电动踏板\n\n开门自动伸出，关门自动收回，解决 SUV/MPV 上下车不便。\n\n- 承重：300 kg\n- 防水：支持\n- 质保：1 年\n- 款式：带灯 / 双灯 / 不带灯\n\n> 具体价格、库存和安装方案以门店确认为准。' \
  --image /abs/path/to/product-image.png \
  --as bot

# 发送到群聊
lark-cli im +messages-send \
  --chat-id oc_xxx \
  --markdown $'## 电动踏板产品推荐\n\n[产品摘要]' \
  --as bot
```

**注意：**
- 发图片用 `--image` 参数，传入本地绝对路径（`lark-cli` 会自动上传）
- 图文混排用 `--markdown`（自动转成飞书 post 格式）
- 先通过 `lark-contact` 查客户 open_id
- 发送前务必与销售确认：接收人、内容、发送身份

#### 方式 B: 通过 lark-doc 创建产品介绍文档

先加载 `lark-doc` skill 了解完整的 XML 语法和样式指南，然后：

```bash
# 创建产品介绍文档
lark-cli docs +create --api-version v2 \
  --parent-position my_library \
  --content '<title>电动踏板产品介绍</title>
<note>来源：蓝辉轻改 | 日期：yyyy-mm-dd</note>
<h1>产品概述</h1>
<p>电动踏板主要解决 SUV、MPV 高底盘上下车不便的问题。</p>
<h2>款式对比</h2>
<ul>
  <li>不带灯款：低调实用</li>
  <li>单灯款/带灯款：夜间识别</li>
  <li>双灯款：迎宾展示感更强</li>
</ul>
<h2>技术参数</h2>
<ul>
  <li>承重：300 kg</li>
  <li>防水：支持</li>
  <li>质保：1 年</li>
</ul>'
```

#### 方式 C: 批量发送产品图册

```bash
# 先上传图片获取 image_key
lark-cli im images create --data '{"image_type":"message"}' --file ./step-product.png
# 返回: {"image_key":"img_v3_xxxx"}

# 用 image_key 在 markdown 中引用
lark-cli im +messages-send \
  --user-id ou_xxx \
  --markdown $'## 电动踏板款式\n\n![带灯款](img_v3_xxxx)\n![双灯款](img_v3_yyyy)\n\n更多产品欢迎到店了解。' \
  --as bot
```

## Response Shape

### 学习阶段输出

For broad learning requests:

```markdown
# 电动踏板销售学习

电动踏板可以按 3 个款式模块理解：

1. 单灯款 / 带灯款：实用基础上增加夜间识别。
2. 双灯款：迎宾和展示感更强。
3. 不带灯款：更低调，核心是上下车便利。

适合客户：
- SUV/MPV/越野 SUV 车主
- 家里有老人小孩
- 车身较高、上下车不方便
- 商务接待或夜间用车较多

边界：
- 价格、库存、施工工时和具体质保范围需要门店确认。

需要发给客户看吗？我可以帮你通过飞书直接发图文消息。
```

For fitment requests:

```markdown
# 车型适配查询

理想 MEGA 当前在知识库中有电动踏板适配记录。

- 车型类型：MPV
- 可选款式：带灯、不带灯、双灯
- 承重：300KG
- 防水：支持防水
- 质保：1年

建议话术：
> 这类电动踏板主要解决 MPV/SUV 上下车便利，同时能提升迎宾感。您如果夜间用车多，可以优先看带灯或双灯款；如果想低调实用，可以看不带灯款。

边界：
- 最终安装方案、价格、库存和工时以门店确认为准。

需要我把这个发给客户吗？提供客户 open_id 或群聊 ID，我可以通过飞书直接发送。
```

### 分享阶段输出

```markdown
已通过飞书将电动踏板产品信息发送给客户。

- 发送方式：lark-im +messages-send
- 内容：电动踏板介绍（图文）
- 接收人：ou_xxx
- 发送身份：bot

下一步建议：
- 等客户回复后确认是否到店看实物
- 或确认具体款式偏好（带灯/双灯/不带灯）
```

## Quick Reference: lark-im 常用命令

| 场景 | 命令 |
|:----|:-----|
| 查客户 open_id | `lark-cli contact +search-user --query "客户姓名/手机号"` |
| 发文本消息 | `lark-cli im +messages-send --user-id ou_xxx --text "您好"` |
| 发图文消息 | `lark-cli im +messages-send --user-id ou_xxx --markdown $'## 标题\n\n内容'` |
| 发图片 | `lark-cli im +messages-send --user-id ou_xxx --image ./product.png` |
| 发到群聊 | `lark-cli im +messages-send --chat-id oc_xxx --markdown $'## 通知'` |
| 上传图片获取 key | `lark-cli im images create --data '{"image_type":"message"}' --file ./img.png` |
| 预览不发 | 加 `--dry-run` 参数 |

## Quick Reference: lark-doc 常用命令

| 场景 | 命令 |
|:----|:-----|
| 创建文档 | `lark-cli docs +create --api-version v2 --content '<title>标题</title><p>内容</p>'` |
| 创建到知识库 | `lark-cli docs +create --api-version v2 --parent-token <token> --content '...'` |
| 追加内容 | `lark-cli docs +update --api-version v2 --doc <token> --command append --content '...'` |

## Important Sources

- Product data: `workspace/04_knowledge/eletric-step/products.json`
- Style modules: `workspace/04_knowledge/eletric-step/style-modules.md`
- Fitment table: `workspace/04_knowledge/eletric-step/fitment-table.md`
- Sales knowledge: `workspace/04_knowledge/eletric-step/sales-knowledge.md`
- QA: `workspace/04_knowledge/eletric-step/sales-qa.md`
- Guardrails: `workspace/04_knowledge/eletric-step/source-boundary.md`

Read `references/response-patterns.md` when you need extra wording examples.

## Connects To

- `lark-im`：发送产品图文消息给客户或群聊
- `lark-doc`：创建产品介绍飞书文档
- `lark-drive`：管理产品图片和文件权限
- `lark-shared`：认证和身份管理（所有操作前自动加载）
- `lark-contact`：查询客户 open_id
- `xiaomi-modification-learning`：小米车型改装配件（含碳纤维件、包覆件等）

## Safety Rules

- 发消息前必须与销售确认：发送对象、内容、发送身份
- 不要编造客户的 open_id 或 chat_id
- 不要一次发过多图片给客户（建议 1-3 张）
- 所有价格、库存、安装、质保以门店确认为准
- 只说"支持防水"，不说具体 IP 等级
- 不超过 1 年质保承诺