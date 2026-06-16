import subprocess
import json
import sys

title = "lark-cli 功能验证测试文档"
markdown = """# lark-cli 功能验证

## 测试概要

通过本次测试验证 lark-cli 的云文档创建功能正常。

- 测试时间：""" + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M') + """
- 测试工具：lark-cli v1.0.48
- 认证方式：bot-only
- 创建方式：docs +create

## 测试结论

> lark-cli 云文档创建功能运行正常 ✅
"""

cmd = [
    "lark-cli", "docs", "+create",
    "--title", title,
    "--markdown", markdown,
    "--api-version", "v1",
    "--as", "bot",
    "--format", "pretty"
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("EXIT_CODE:", result.returncode)
sys.exit(result.returncode)
