---
name: xiaomi-modification-learning
description: Use when sales asks to learn, explain, introduce, browse, or recommend Xiaomi SU7/YU7 modification products with pictures, including phrases like 小米改装, SU7改装, YU7改装, 小米产品款式, 米沃套件, 了解小米改装, 有哪些改装件, 图文讲解.
requires:
  - lark-cli
  - lark-shared
connects_to:
  - lark-im
  - lark-doc
  - lark-drive
---

# Xiaomi Modification Learning

## Overview

Use this skill when 有膜有漾 sales wants a fast, visual learning explanation of Xiaomi SU7/YU7 modification products.

The skill turns a natural-language request such as "我想了解小米的改装" into a concise image-text learning card using:

- `workspace/04_knowledge/xiaomi/products.json` for product names and product images.
- `workspace/04_knowledge/xiaomi/miwo/products.json` for supplier catalog specs when available.
- `workspace/04_knowledge/xiaomi/miwo/source-boundary.md` for sales guardrails.

## Triggers

Use this skill when the message asks about:

- 小米改装 / 小米汽车改装
- SU7 改装 / YU7 改装
- 小米产品款式 / 产品图片 / 图文介绍
- 米沃套件 / 米沃图册
- 外观套件、内饰套件、碳纤维件、包覆件
- "我想了解小米的改装"
- "给我讲一下 SU7 有哪些可以改"
- "YU7 有哪些产品可以给客户看"
- "把这个产品发给客户"（结合 lark-im 发消息）
- "给客户做个产品介绍文档"（结合 lark-doc 创建文档）

## Do Not Use When

- The user asks about car film recommendation only; use `recommend-film-product`.
- The user asks for CRM writing; use `crm-natural-language-entry`.
- The user asks for car wrap AI rendering; use `ark-seedream-car-preview`.

## Workflow: Learn → Share

小米改装技能的核心工作流分为两个阶段：

### Phase 1: 学习产品（Learn）

1. Parse intent.
   - If query includes `SU7` or `YU7`, focus on that model.
   - If query includes product names such as `前包围`、`方向盘`、`尾翼`、`迎宾踏板`, focus on matching products.
   - If query is broad like "了解小米改装", give a learning overview by model and category.
2. Run the bundled script to generate a first-pass image-text card:

```bash
python3 skills/xiaomi-modification-learning/scripts/explain.py "我想了解小米的改装"
```

3. Return the script output, then adjust wording for the sales context if needed.
4. Include images sparingly.
   - Broad overview: show 4-6 representative images.
   - Specific product query: show 1-3 matching images.
   - In Feishu/gateway responses, include `MEDIA:/absolute/path/to/image.png` for each image that should be sent as a native image attachment.
   - You may also include Markdown image syntax for desktop/local readability, but `MEDIA:` is the reliable Feishu delivery mechanism.
5. Always include source boundaries:
   - Do not call these Xiaomi official or original factory parts.
   - Do not invent price, inventory, construction duration, warranty, or legal/registration conclusions.
   - Ask sales to confirm stock, quote, installation plan, and warranty before customer commitment.

### Phase 2: 分享给客户（Share）

学习完成后，如果销售想把产品信息发给客户，使用以下方式：

#### 方式 A: 通过 lark-im 发送图文消息给客户

先加载 `lark-im` skill 了解完整的安全规则和参数，然后：

```bash
# 发送产品图文消息给客户（单聊）
lark-cli im +messages-send \
  --user-id ou_xxx \
  --markdown $'## SU7 侧裙\n\n干碳纤维材质，降低视觉重心，车身更贴地。\n\n- 材质：PP+EPDM-TD20+干碳纤维\n- 重量：约 4.9 kg\n- 适配：2024 年 SU7 全系\n\n> 具体价格、库存、安装工时和质保以门店确认为准。' \
  --image /abs/path/to/product-image.png \
  --as bot

# 发送到群聊
lark-cli im +messages-send \
  --chat-id oc_xxx \
  --markdown $'## 小米 SU7 改装配件推荐\n\n[产品摘要]' \
  --as bot
```

**注意：**
- 发图片用 `--image` 参数，传入本地绝对路径（`lark-cli` 会自动上传）
- 图文混排用 `--markdown`（自动转成飞书 post 格式）
- 先通过 `lark-contact` 查客户 open_id
- 发送前务必与销售确认：接收人、内容、发送身份
- 绝对路径如 `/Users/xxx/.../image.png` 会被拒绝，需改为工作目录相对路径或先 copy 到当前目录

#### 方式 B: 通过 lark-doc 创建产品介绍文档

先加载 `lark-doc` skill 了解完整的 XML 语法和样式指南，然后：

```bash
# 创建产品介绍文档
lark-cli docs +create --api-version v2 \
  --parent-position my_library \
  --content '<title>SU7 改装产品介绍</title>
<note>资料日期：yyyy-mm-dd</note>
<h1>外观套件</h1>
<h2>前包围</h2>
<p>干碳纤维材质，改变前脸姿态，适配 2024 SU7 全系。</p>
<image src="img_v3_xxxx"></image>
<hr/>
<h2>侧裙</h2>
<p>材质：PP+EPDM-TD20+干碳纤维，重量：4.9 kg。</p>
<image src="img_v3_xxxx"></image>
<hr/>
<h1>内饰套件</h1>
<h2>方向盘</h2>
<p>碳纤维+真皮，提升座舱运动感。</p>'
```

**注意：**
- XML 中插入图片需先上传到飞书拿到 `image_key`
- 创建到知识库传 `--parent-token`，创建到个人空间传 `--parent-position my_library`
- 详细 XML 语法参考 `lark-doc` skill 的 `references/lark-doc-xml.md`

#### 方式 C: 通过 lark-im 批量发送产品图册（多图）

```bash
# 先上传图片获取 image_key
lark-cli im images create --data '{"image_type":"message"}' --file ./product-01.png
# 返回: {"image_key":"img_v3_xxxx"}

# 用 image_key 在 markdown 中引用
lark-cli im +messages-send \
  --user-id ou_xxx \
  --markdown $'## SU7 外观套件\n\n![前包围](img_v3_xxxx)\n![侧裙](img_v3_yyyy)\n![尾翼](img_v3_zzzz)\n\n更多产品欢迎到店了解。' \
  --as bot
```

## Response Shape

### 学习阶段输出

For broad learning requests:

```markdown
小米改装可以先按 3 条线理解：

1. 外观姿态：前包围、侧裙、机盖、尾翼、后视镜等。
2. 内饰质感：方向盘、中控、门饰条、出风口、迎宾踏板等。
3. 包覆升级：座椅、顶棚、ABC 柱、门板、中控仪表台等，当前主要来自米沃 SU7 图册。

代表产品：

MEDIA:/abs/path/Image/SU7/SU7-01-前包围.png

...

销售怎么讲：
> 这类产品不是单纯"装饰"，客户真正买的是外观姿态、座舱质感和个性化识别度。先确认车型，再确认客户想改外观还是内饰。

边界：
- 资料来自内部款式表和米沃供应商图册，不要说成小米官方原厂件。
- 价格、库存、安装工时、质保和备案需要门店确认。

需要发给客户看吗？我可以帮你通过飞书直接发图文消息给客户。
```

For specific product requests:

```markdown
你问的是：SU7 方向盘

产品理解：
- 车型：SU7
- 部位：方向盘
- 学习重点：这是内饰视觉和握感升级件，适合客户想提升座舱运动感。
- 供应商参数：如图册有编码、材质、重量，按来源列出。

图片：
MEDIA:/abs/path/Image/SU7/SU7-05-方向盘.png

对客话术：
> 如果您想让车内更有运动感，方向盘是很直观的位置。具体安装方式、价格和质保我们需要按门店方案确认。

需要我把这个发给客户吗？提供客户的 open_id 或群聊 ID，我可以通过飞书直接发送。
```

### 分享阶段输出

```markdown
已通过飞书将产品信息发送给客户。

- 发送方式：lark-im +messages-send
- 内容：SU7 侧裙（图文）
- 接收人：ou_xxx
- 发送身份：bot

下一步建议：
- 等客户回复后确认是否到店看实物
- 或再发送其他产品做对比
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

- Product image index: `workspace/04_knowledge/xiaomi/products.json`
- Human browsing pages: `workspace/04_knowledge/xiaomi/products.md`, `SU7.md`, `YU7.md`
- Supplier catalog specs: `workspace/04_knowledge/xiaomi/miwo/products.json`
- Sales knowledge: `workspace/04_knowledge/xiaomi/miwo/sales-knowledge.md`
- QA examples: `workspace/04_knowledge/xiaomi/miwo/sales-qa.md`
- Guardrails: `workspace/04_knowledge/xiaomi/miwo/source-boundary.md`

Read `references/response-patterns.md` when you need extra wording examples.

## Connects To

- `lark-im`：发送产品图文消息给客户或群聊
- `lark-doc`：创建产品介绍飞书文档
- `lark-drive`：管理产品图片和文件权限
- `lark-shared`：认证和身份管理（所有操作前自动加载）
- `lark-contact`：查询客户 open_id
- `ark-seedream-car-preview`：生成装车改色预览图

## Safety Rules

- 发消息前必须与销售确认：发送对象、内容、发送身份
- 不要编造客户的 open_id 或 chat_id
- 不要一次发过多图片给客户（建议 1-3 张）
- 所有价格、库存、安装、质保以门店确认为准
- 产品来源为供应商图册，不要说成小米官方原厂件
