#!/bin/bash
# 一键推送到 GitHub LhqgSalesAgent 仓库
# 使用方式: bash push.sh <你的GitHub Token>

TOKEN="$1"
if [ -z "$TOKEN" ]; then
  echo "用法: bash push.sh <GitHub Personal Access Token>"
  exit 1
fi

cd /tmp/ymyy-dist
git remote set-url origin "https://coyafky:${TOKEN}@github.com/coyafky/LhqgSalesAgent.git"
git push -u origin main
