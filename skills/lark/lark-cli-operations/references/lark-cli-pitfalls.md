# lark-cli 常见错误与避坑

## 认证与身份

### `lark-cli doctor` 显示 `not bound`
```
config.json not found / hermes context detected but lark-cli is not bound to it
```
**修复：** `lark-cli config bind --source hermes --identity bot-only`
（需用户确认）

### `--as user` 报身份缺失
```
User identity: missing (no user logged in)
```
**原因：** 本 profile 只配置了 bot-only 身份。
**修复：** 改用 `--as bot`。如需 user 身份，需先 `lark-cli auth login`。

---

## 文档操作

### `docs +create --api-version v2` 报 `--content is required`
```
--content is required
```
**原因：** v2 API 弃用了 `--markdown`，改用 `--content` 传 XML 格式内容（标题写在 `<title>` 标签内）。
**修复：** 使用 XML 格式：`--content '<title>标题</title><p>内容</p>'`。
如仍需 Markdown，只能用 v1 API：`--api-version v1 --markdown "内容"`（v1 已废弃）。

### `docs +create` 用 v2 但传了 `--title`
**原因：** v2 API 的标题从 `--content` 的 `<title>` 标签中解析，不再用单独的 `--title` 参数。
**修复：** 把标题写在 XML 内容的 `<title>` 标签中：`--content '<title>文档标题</title>...'`

### `docs +create --as bot` 成功但打不开文档
文档已创建，但 bot 身份无法自动授权给用户。
**原因：** user 身份未登录，`permission_grant` 被跳过。
**修复：** 用户在飞书 UI 手动添加权限，或后续用 `drive permission.members create` 授权。

---

## 权限操作

### `drive permission.members create` 被拒绝
```
confirmation_required: drive.permission.members.create requires confirmation
```
**修复：** 加上 `--yes` 标志：`lark-cli drive permission.members create ... --yes`

---

## Base 操作

### `lark-cli api` 不支持 `--format json`
```
unknown flag: --format
```
**原因：** `lark-cli api` 命令没有 `--format` 标志。
**修复：** 不加 `--format`，输出默认为 JSON。

---

## lark-im 消息发送

### `+messages-send --image` 传绝对路径被拒绝
```
/Users/xxx/image.png is not a valid relative path
```
**原因：** `--image` 只接受工作目录相对路径、URL 或已有 `image_key`。
**修复：** `cd` 到图片目录后用 `--image ./product.png`，或先用 `lark-cli im images create --data '{"image_type":"message"}' --file ./product.png` 上传获取 `image_key`。

---

## 通用

### shell 转义导致命令失败
当 `--markdown` 或 `--title` 中包含 `$()`、引号、反引号时，直接在 shell 中传参容易报错。
**推荐做法：** 用 Python `subprocess.run([...])` 传参，避免 shell 解释。
