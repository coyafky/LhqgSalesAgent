---
name: ark-seedream-car-preview
description: Hermes 车膜改色图生图技能。根据客户上传的实车原图和车膜色卡资产库，优先调用 xinghu gpt-image-2 图生图 API，输出保留原车结构和场景的改色预览图，并可通过 OpenClaw 回传到微信或飞书。
---

# Hermes 车膜改色预览生图

当用户、销售或 Hermes profile 需要根据"客户实车照片 + preview 色卡图"生成真实改色膜上车效果图时，使用本技能。

本技能面向车膜销售工作流，不是普通修图技能，也不是文生图技能。核心目标是：客户上传原车图后，以该原图为主体做图生图，只改变车身贴膜覆盖区域的颜色和膜面质感，保持车辆、场景、角度、轮毂、车灯、车牌、玻璃、背景和光影关系尽量不变，输出可发给客户确认的写实预览图。

## 首选图生图 Provider

首选 provider 是 xinghu gpt-image-2 图生图接口，接口文档：

```text
https://xinghuapi.apifox.cn/8703402m0
```

默认 provider chain 必须把 `xinghu_primary` 放第一位：

```text
WRAP_PROVIDER_CHAIN=xinghu_primary,4sapi_primary,apiyi_primary,relay_backup
```

xinghu 请求契约：

- API Base URL：`https://xinghuapi.com/v1`
- Endpoint：`POST /images/generations`
- Content-Type：`application/json`
- Model：`gpt-image-2`
- Request style：`extra_body`
- 必须把客户原车图作为 `payload.extra_body.image` 传入
- `watermark` 必须放在 `payload.extra_body.watermark`
- 禁止在缺少客户原图时调用 provider；缺原图时应追问/等待上传，不做文生图

## Hermes 触发条件

满足以下任一情况时触发：

- 客户上传实车图，并指定车膜色号，如 `A-001`、`D-325`
- 客户或销售说"帮我生成上车效果图""改色预览""贴膜效果图""这个颜色上车看看"
- 输入中包含车膜中文名、英文名、色系或色卡图片
- Hermes 需要从本地 JSON 资产库查询颜色，并调用图像模型生成结果

不要在以下情况触发：

- 只是查询库存、报价、施工时间，不需要生成图片
- 用户要求完全重设计车辆外观、换车型、换轮毂、改装套件
- 用户没有提供实车图，且当前任务要求直接生成客户车辆效果图

## 输入结构

Hermes profile 推荐传入 JSON：

```json
{
  "task": "vehicle_wrap_preview",
  "vehicle_ref": "/absolute/path/to/customer-car.jpg",
  "color_asset_id": "A-001",
  "delivery": {
    "enabled": false,
    "channel": "openclaw-weixin",
    "target": ""
  },
  "generation": {
    "size": "auto",
    "quality": "high"
  }
}
```

当色号不在资产库中时，使用手动颜色字段：

```json
{
  "task": "vehicle_wrap_preview",
  "vehicle_ref": "/absolute/path/to/customer-car.jpg",
  "color_ref": "/absolute/path/to/color-card.jpg",
  "color_name": "勃艮第酒红",
  "color_code": "LPR803",
  "color_value": "#8B2942",
  "finish": "哑光",
  "description": "低饱和高级感，偏暖红酒色"
}
```

## 资产库

颜色资产库位于：

```text
{baseDir}/references/color_assets.json
```

资产库由 Lab 色卡表、`Card-color` 数据库中的 `preview_hex` 和本 skill 内置的 `assets/previews/` 色卡图生成。每个颜色资产包含：

- `id` / `serial`：稳定色号，例如 `A-001`
- `names.zh` / `names.en`：中英文名称
- `images.swatch`：preview 色卡图，路径应指向 `../assets/previews/...`，这是生图的主要颜色依据
- `color.hex`：色卡 PNG / `Card-color` 数据库标注的 HEX，只作为辅助标注和销售摘要字段
- `color.lab`：实体色卡 Lab 测量值，只作为辅助测量记录，不用来重新换算目标颜色
- `color.family`：色系
- `material` / `finish`：材质与膜面提示
- `prompt`：可直接注入生图脚本的结构化字段

查询颜色资产：

```bash
python3 {baseDir}/scripts/query_color_assets.py "宝马阿布扎比蓝"
python3 {baseDir}/scripts/query_color_assets.py A-001
python3 {baseDir}/scripts/query_color_assets.py 蓝色系 --limit 5
```

重建颜色资产库：

```bash
python3 {baseDir}/scripts/build_color_assets.py \
  --source /absolute/path/to/MGS-PET改色膜-飞书色卡画廊_色卡档案_全部色卡.xlsx \
  --preview-dir {baseDir}/assets/previews \
  --card-db /absolute/path/to/Card-color/data/color-lab.db
```

## 执行流程

1. 确认有客户实车图，作为 `--vehicle-ref`。
2. 优先用色号或色名查询 `references/color_assets.json`。
3. 如果查到资产，使用 `--asset-id`，由脚本自动注入色名、色号、HEX/Lab 辅助值、材质提示，并自动把资产库 `images.swatch` 作为 `--color-ref` 传入。
4. 如果查不到资产，必须使用 `--color-ref` 传入人工提供的色卡图；手动 HEX/Lab 只能作为辅助字段。
5. 调用 `gen.py` 生成图片；默认读取 `WRAP_PROVIDER_CHAIN`，首选 `xinghu_primary`。这是图生图调用：客户原车图必须作为第一参考图传入，xinghu 会通过 `payload.extra_body.image` 接收该图。所有 provider 均走 `POST /images/generations` + `application/json`，通过 `image` 字段（数组或 `extra_body` 嵌套）传参考图。详见 `references/provider-api-contracts.md`。
6. 如果需要直接回传客户，调用 `gen_and_send.py`，它会把 provider 参数透传到生图脚本。
7. 输出结果返回给 Hermes，由 Hermes 决定展示、发送或进入人工质检。

## 只解析不生图

Hermes 路由或调试阶段可先 dry-run，检查最终 prompt 和引用图。命中资产时，`refs` 必须同时包含客户实车图和 preview 色卡图：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --dry-run
```

## 生成图片

使用资产库色号生成，默认走 provider chain，首位为 xinghu 图生图：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --response-format b64_json \
  --quality high
```

上面命令会自动把客户原车图作为第一参考图，把 `references/color_assets.json` 中的 `images.swatch` 追加为色卡参考图，不需要销售手动传 `--color-ref`。缺少 `--vehicle-ref` 时必须停止并追问客户原图。

显式指定某个 OpenAI-compatible 中转站生成：

```bash
python3 {baseDir}/scripts/gen.py \
  --provider relay \
  --base-url "$IMAGE_RELAY_BASE_URL" \
  --model gpt-image-2 \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --size auto \
  --response-format b64_json \
  --quality high
```

OpenAI-compatible 路径会把客户车型图和资产库 preview 色卡图一起转成可上传的图片引用，并调用：

```text
{BASE_URL}/images/generations
```

其中客户原车图必须排在第一张，preview 色卡图必须排在第二张。星狐 `extra_body` 风格会把第一张客户原车图写入 `payload.extra_body.image`，确保接口执行图生图而不是文生图。色卡图仍是目标颜色和膜面视觉的主要依据，HEX/Lab 只进入 prompt 作为辅助识别字段。

默认 `response-format=b64_json`，这样模型结果会直接解码保存到本地，避免某些中转站返回的临时 URL 在下载阶段出现 403 权限问题。只有明确需要保留远程 URL 时，才手动传 `--response-format url`。

默认 `size=auto`，表示输出尺寸交给图像模型根据客户车型图的比例和内容决定；不要在飞书自动流程中固定为横版或方图。只有明确要做横版展示图、竖版海报或方图时，才手动传 `1536x1024`、`1024x1536` 或 `1024x1024`。

禁止回退到文生图或纯 HEX / Lab 生图：如果没有客户原车图，必须追问上传；如果没有 `--asset-id` 命中的 `images.swatch`，就必须手动传 `--color-ref`。脚本会拒绝只有 `--color-value`、Lab 或文字描述的生图请求。

使用手动颜色字段生成：

```bash
python3 {baseDir}/scripts/gen.py \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --color-ref /absolute/path/to/color-card.jpg \
  --color-name "勃艮第酒红" \
  --color-code "LPR803" \
  --color-value "#8B2942" \
  --finish "哑光" \
  --description "低饱和高级感，偏暖红酒色" \
  --response-format b64_json
```

## 生成并回传

回传到微信：

```bash
python3 {baseDir}/scripts/gen_and_send.py \
  --channel openclaw-weixin \
  --target o9cq805uzekq7fioq4n5czimsgpk@im.wechat \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --message "这是基于实车图和色卡生成的车膜预览图"
```

回传到飞书：

```bash
python3 {baseDir}/scripts/gen_and_send.py \
  --channel feishu \
  --target oc_xxx \
  --provider relay \
  --base-url "$IMAGE_RELAY_BASE_URL" \
  --model gpt-image-2 \
  --vehicle-ref /absolute/path/to/customer-car.jpg \
  --asset-id A-001 \
  --response-format b64_json \
  --message "这是基于实车图和色卡生成的车膜预览图"
```

## Prompt 约束

图生图时必须遵守：

- 以客户车辆原图为唯一主体基础
- 必须将客户车辆原图传给图生图 API；不得只把车辆信息写进 prompt 后做文生图
- 只修改贴膜覆盖的车身漆面区域
- 保持车型、外观结构、轮毂、车灯、车窗、车牌、背景、角度、透视、光影和反射关系
- 色彩优先参考随输入传入的 preview 色卡图；`color.hex` 和 Lab 只作为辅助标注，不要只靠数值生成颜色，也不要用 Lab 重新换算目标颜色
- 膜面质感按资产库 `finish.prompt_hint` 或手动 `finish` 体现
- 不要生成概念车、海报、插画、棚拍大片或重新设计效果
- 不要新增文字、水印、装饰、配件或任何不在原图中的物体
- 给飞书/微信返回操作摘要时，说明本次生图依据为"客户车型图 + preview 色卡图"；色值字段可展示资产库 `color.hex`，可附带 Lab 辅助值；不要展示"明亮正黄"等非资产库实测描述

## 输出

`gen.py` 输出 JSON，关键字段包括：

- `prompt`：最终生图 prompt
- `files`：生成图片的本地绝对路径
- `relative_files`：相对路径
- `media_tokens`：OpenClaw 可识别媒体 token
- `color_asset`：本次命中的颜色资产摘要
- `provider`：本次成功调用的 provider 名称
- `provider_attempts`：provider 轮询尝试记录，失败时包含错误摘要
- `image_urls`：模型返回的原始图片 URL；如果 provider 返回 base64，脚本会直接解码保存到本地

## 依赖

- `python3`
- xinghu gpt-image-2 图生图 API，文档：`https://xinghuapi.apifox.cn/8703402m0`
- 一个或多个 OpenAI-compatible 图生图 API 中转站作为备用
- provider chain 环境变量，必须配置在 `{skillDir}/.env.local` 或 `{profileDir}/.env` 中

### 环境变量命名规则

每个 provider 一组变量，前缀为 `WRAP_PROVIDER_{NAME}_`，其中 `{NAME}` 是 chain 中声明的名字（大写）：

| 变量 | 必需 | 说明 |
|------|------|------|
| `WRAP_PROVIDER_{NAME}_BASE_URL` | ✅ | 中转站 API 地址，如 `https://4sapi.com/v1` |
| `WRAP_PROVIDER_{NAME}_API_KEY` | ✅ | API Key（占位符值如 `replace-with-xxx` 会被跳过） |
| `WRAP_PROVIDER_{NAME}_MODEL` | ❌ | 模型名，默认 `gpt-image-2` |
| `WRAP_PROVIDER_{NAME}_AUTH_SCHEME` | ❌ | `bearer`（默认）或 `raw`（直接当 Authorization 头发送） |
| `WRAP_PROVIDER_{NAME}_REQUEST_STYLE` | ❌ | `refs_array`（默认，传图片数组），`single_image`（只传第一张），或 `extra_body`（`image`+`watermark` 放 `extra_body` 内，适配星狐等 API） |
| `WRAP_PROVIDER_{NAME}_WATERMARK` | ❌ | `true`/`false`，是否添加水印 |
| `WRAP_PROVIDER_{NAME}_RESPONSE_FORMAT` | ❌ | `b64_json`（推荐）或 `url` |
| `WRAP_PROVIDER_{NAME}_ENDPOINT_PATH` | ❌ | 请求路径，默认 `/images/generations`；可为 `/images/edits`（备用） |
| `WRAP_PROVIDER_{NAME}_CONTENT_TYPE` | ❌ | Content-Type，默认 `application/json`；可为 `multipart/form-data`（备用） |

### 请求风格与 `image` 字段格式

所有 provider 共用 `POST /images/generations` + `application/json`，仅在 `image` 字段的格式上通过 `REQUEST_STYLE` 区分：

| 风格 | `image` 位置 | `image` 类型 | 适配 provider |
|------|-------------|-------------|-------------|
| `refs_array`（默认） | payload 顶层 | `["data:...", "data:..."]` 数组 | 4sapi, apiyi 等标准中转站 |
| `single_image` | payload 顶层 | `"data:..."` 单字符串 | 只接受单图的中转站 |
| `extra_body` | `payload["extra_body"]` 内 | `"data:..."` 单字符串（`refs[0]`） | xinghu 等要求嵌套结构的中转站 |

#### extra_body 风格详解

当 `REQUEST_STYLE=extra_body` 时，发出的 JSON payload 结构为：

```json
{
  "model": "gpt-image-2",
  "prompt": "...",
  "size": "1824x1000",
  "extra_body": {
    "image": "data:image/jpeg;base64,...",
    "watermark": true
  }
}
```

关键区别：
- `image` 是单字符串（`refs[0]` — 客户原车图），不是数组。色卡图会进入 refs 和 prompt 解析流程；对星狐 `extra_body` 请求，必须至少确保客户原车图进入 `extra_body.image`，防止退化为文生图。
- `watermark` 也在 `extra_body` 内，不在顶层。
- 标准 OpenAI `/images/generations` 不支持 `image` 参数。`extra_body` 风格是为那些扩展了该端点、接受参考图的中转站（如 xinghu）设计的。对其他标准中转站不要用此风格。

### 已知问题

#### xinghu_primary 偶发瞬断

xinghu 的 API 偶发 "Remote end closed connection without response" 错误（约 ~10% 的请求），重试即可恢复。在 provider chain 中，第一次失败会自动回退到下一顺位（4sapi → apiyi），对终端用户无影响。

处理方式：**不要降级 xinghu 的优先级**。链式回退已经处理了瞬断。如果必须只用 xinghu，重试 1-2 次即可。

### 完整示例（4-provider chain）

```bash
# chain 顺序 = 优先级顺序。xinghu 偶发瞬断，会自动回退到下一顺位。
WRAP_PROVIDER_CHAIN=xinghu_primary,4sapi_primary,apiyi_primary,relay_backup

# --- xinghu_primary（首位，图生图，`image` 走 `extra_body`）---
WRAP_PROVIDER_XINGHU_PRIMARY_BASE_URL=https://xinghuapi.com/v1
WRAP_PROVIDER_XINGHU_PRIMARY_API_KEY=sk-......
WRAP_PROVIDER_XINGHU_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_XINGHU_PRIMARY_AUTH_SCHEME=bearer
WRAP_PROVIDER_XINGHU_PRIMARY_REQUEST_STYLE=extra_body
WRAP_PROVIDER_XINGHU_PRIMARY_WATERMARK=true
WRAP_PROVIDER_XINGHU_PRIMARY_RESPONSE_FORMAT=url

# --- 4sapi_primary（次选，宽高必须被16整除）---
WRAP_PROVIDER_4SAPI_PRIMARY_BASE_URL=https://4sapi.com/v1
WRAP_PROVIDER_4SAPI_PRIMARY_API_KEY=sk-......
WRAP_PROVIDER_4SAPI_PRIMARY_MODEL=gpt-image-2
WRAP_PROVIDER_4SAPI_PRIMARY_AUTH_SCHEME=bearer

# --- apiyi_primary（备选，无尺寸约束，输出尺寸可能微调）---
WRAP_PROVIDER_APIYI_PRIMARY_BASE_URL=https://api.apiyi.com/v1
WRAP_PROVIDER_APIYI_PRIMARY_API_KEY=sp-......
WRAP_PROVIDER_APIYI_PRIMARY_MODEL=gpt-image-2-all
WRAP_PROVIDER_APIYI_PRIMARY_AUTH_SCHEME=bearer

# --- relay_backup（最终回退，无 API Key 时跳过）---
WRAP_PROVIDER_RELAY_BACKUP_BASE_URL=https://backup.example.com/v1
WRAP_PROVIDER_RELAY_BACKUP_API_KEY=sk-......
WRAP_PROVIDER_RELAY_BACKUP_MODEL=gpt-image-2
WRAP_PROVIDER_RELAY_BACKUP_AUTH_SCHEME=bearer
```

### 变量加载优先级

`merged_env()` 按以下顺序合并（后覆盖前）：

1. `{skillDir}/.env`
2. `{skillDir}/.env.local` — **推荐存放 API Key 的位置**
3. `{profileDir}/.env`
4. `{profileDir}/.env.local`
5. 进程 `os.environ`
6. `{skillDir}/.local.json`

### 回退机制

如果 `WRAP_PROVIDER_CHAIN` 未设置或 chain 为空：

- 读单个 `IMAGE_RELAY_BASE_URL` + `IMAGE_RELAY_API_KEY`（兼容传统配置）
- 仍可通过 `IMAGE_PROVIDER` 指定模型名

## 比例处理（aspect ratio matching）

`dimensions.py` 中 `aspect_ratio_matches()` 强制要求生成图与实车图宽高比差值 ≤ 0.01，超出则抛出 `RuntimeError` 并阻止发送给客户。这是生图时最常见的失败原因之一。

### 排查步骤

1. 先检查实车图尺寸：`identify <path>` 或 `python3 -c "from PIL import Image; print(Image.open('<path>').size)"`
2. 计算目标比例：`width / height`
3. 若第一次 `--size auto` 或默认 chain 失败，手动计算匹配尺寸：
   - 找标准尺寸（宽高均能被 16 整除——部分 provider 有此限制）
   - 使 `|request_width/request_height - target_width/target_height| ≤ 0.01`
4. 常用匹配组合示例（以 270×148 ≈ 1.824:1 为例）：
   - `1824×1000`（1.8240，差 0.0003 ✅）→ 1824 能被 16 整除，1000 不能被 16 整除
   - 若 provider 要求宽高均可被 16 整除，尝试 `1808×992`（1.8226，差 0.0017 ✅，1808÷16=113，992÷16=62）
5. 用 `--size WxH` 显式传入匹配尺寸重试。
6. 如果有多 provider chain，失败后会依次尝试下一个 provider，不同 provider 对尺寸约束不同。

### 已知 provider 尺寸约束（参见 references/aspect-ratio-handling.md）

- **4sapi_primary**（gpt-image-2）：宽高必须均可被 16 整除
- **apiyi_primary**（gpt-image-2-all）：无此限制，输出尺寸可能与请求尺寸略有偏差（如请求 1824×1000 返回 1693×929 — 比例仍匹配）
- **xinghu_primary**（gpt-image-2，watermark=true，response format=url，`image` 走 `extra_body`）：首选图生图 provider，可能返回固定比例（如 4:3）导致匹配失败

## 参考文件

- 详细的 provider 尺寸约束、异常复现记录和计算方法见 `references/aspect-ratio-handling.md`。
- 各 provider 的 API 合同（端点、Content-Type、参数格式差异）见 `references/provider-api-contracts.md`。
- 生图 prompt 模板见 `references/prompts.md`。

## Hermes 注意事项

- 销售侧只需要收集实车图和色号/色名，不需要手写 prompt。
- 优先走 `--asset-id`，这样结果可追溯到资产库版本。
- 若用户对效果不满意，记录色号、生成图、反馈原因，再优化资产库中的 `finish` 或 `prompt.description`。
- 生图模型不是精确像素级编辑器，复杂遮挡、反光、局部贴膜边界仍建议人工复核。
