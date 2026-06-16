# 文档创建/更新/授权操作参考

## 创建文档（docx）

### v1 API（推荐 — 参数简洁，Markdown 原生支持）

```bash
lark-cli docs +create \
  --title "文档标题" \
  --markdown "# 一级标题\n\n正文内容" \
  --api-version v1 \
  --as bot \
  --format pretty
```

**返回示例：**
```json
{
  "ok": true,
  "data": {
    "doc_id": "DEc8d18sOoAiiHxx0mRcWZC5n4g",
    "doc_url": "https://www.feishu.cn/docx/DEc8d18sOoAiiHxx0mRcWZC5n4g",
    "message": "文档创建成功"
  }
}
```

### v2 API

```bash
lark-cli docs +create \
  --title "文档标题" \
  --content "# 一级标题\n\n正文内容" \
  --api-version v2 \
  --as bot
```

### 注意
- `--as bot` 创建的文档：bot 是所有者，不会自动授予用户权限
- 如需用户可访问 → 手动授权或 `drive permission.members create`

---

## 更新文档

### 追加内容

```bash
lark-cli docs +update \
  --doc "<doc_id>" \
  --command append \
  --markdown "## 追加章节\n\n内容" \
  --api-version v1 \
  --as bot
```

---

## 授权文档权限

### 授权 full_access 给用户

```bash
lark-cli drive permission.members create \
  --params '{
    "token": "<doc_id>",
    "type": "docx",
    "need_notification": true
  }' \
  --data '{
    "member_id": "<user_open_id>",
    "member_type": "openid",
    "perm": "full_access",
    "type": "user"
  }' \
  --as bot \
  --yes \
  --format pretty
```

**参数说明：**
| 参数位置 | 字段 | 说明 |
|---------|------|------|
| `--params` | `token` | 文档 ID（doc_id） |
| | `type` | 文档类型：`docx` / `doc` / `sheet` / `bitable` |
| | `need_notification` | 是否发送通知给被授权人 |
| `--data` | `member_id` | 用户的 open_id |
| | `member_type` | `openid` / `userid` / `email` |
| | `perm` | `view` / `edit` / `full_access` |
| | `type` | `user` / `chat` / `department` |

**权限等级：**
| 等级 | 说明 |
|------|------|
| `view` | 可阅读 |
| `edit` | 可编辑 |
| `full_access` | 可管理（含分享和权限管理） |

**成功返回：**
```json
{
  "code": 0,
  "data": {
    "member": {
      "member_id": "ou_xxx",
      "member_type": "openid",
      "perm": "full_access",
      "perm_type": "container",
      "type": "user"
    }
  },
  "msg": "Success"
}
```

---

## 获取文档内容

```bash
lark-cli docs +fetch --doc "<doc_id>" --api-version v1 --as bot
```
