#!/usr/bin/env python3
"""Create a Feishu doc and grant full_access to the user."""
import subprocess
import json
import sys
from datetime import datetime

now = datetime.now().strftime('%Y-%m-%d %H:%M')
USER_OPEN_ID = "ou_f31f78d6475545bfeffee0e226809708"

# ── Step 1: Create document ──
print("=" * 60)
print("步骤1: 创建云文档「测试文档-2」")
print("=" * 60)

markdown = f"""# 测试文档-2

## 说明

本文档由 lark-cli 自动创建，并已授权给用户。

- 创建时间：{now}
- 创建工具：lark-cli v1.0.48
- 创建身份：bot

## 授权信息

- 被授权人：ou_f31f78d6475545bfeffee0e226809708
- 权限等级：full_access（可管理权限）
- 授权方式：drive permission.members create
"""

cmd_create = [
    "lark-cli", "docs", "+create",
    "--title", "测试文档-2",
    "--markdown", markdown,
    "--api-version", "v1",
    "--as", "bot",
    "--format", "json"
]

result = subprocess.run(cmd_create, capture_output=True, text=True, timeout=15)

if result.returncode != 0:
    print("❌ 创建文档失败")
    print("STDERR:", result.stderr)
    sys.exit(1)

data = json.loads(result.stdout)
if not data.get("ok"):
    print("❌ 创建文档失败:", data)
    sys.exit(1)

doc_id = data["data"]["doc_id"]
doc_url = data["data"]["doc_url"]
print(f"✅ 文档创建成功")
print(f"   doc_id: {doc_id}")
print(f"   doc_url: {doc_url}")

# ── Step 2: Grant permission ──
print()
print("=" * 60)
print("步骤2: 授权 full_access 给用户")
print("=" * 60)

# URL params: token, type, need_notification
params = json.dumps({
    "token": doc_id,
    "type": "docx",
    "need_notification": True
})

# Request body: member info
data_body = json.dumps({
    "member_id": USER_OPEN_ID,
    "member_type": "openid",
    "perm": "full_access",
    "type": "user"
})

cmd_perm = [
    "lark-cli", "drive", "permission.members", "create",
    "--params", params,
    "--data", data_body,
    "--as", "bot",
    "--yes",
    "--format", "pretty"
]

result = subprocess.run(cmd_perm, capture_output=True, text=True, timeout=15)

if result.returncode != 0:
    print("❌ 授权失败")
    print("STDERR:", result.stderr)
    print("STDOUT:", result.stdout)
    sys.exit(1)

perm_data = json.loads(result.stdout)
if perm_data.get("ok"):
    print(f"✅ 授权成功！full_access 已授予用户")
    print(f"   权限: {perm_data.get('data', {}).get('member', {}).get('perm', 'full_access')}")
else:
    print("⚠️ 授权可能未完全成功:", perm_data)

print()
print("=" * 60)
print("全部完成！")
print(f"📄 文档链接: {doc_url}")
print("=" * 60)
