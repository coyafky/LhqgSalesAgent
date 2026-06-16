# 有膜有漾 Sales Agent — Hermes Profile Distribution

> 面向门店销售、招商人员和客服的 Hermes Agent Profile，集成 CRM 全链路、产品知识库、销售话术与车膜改色预览生成。

## 安装

### 前置要求

- [Hermes Agent](https://hermes-agent.nousresearch.com) >= 0.12.0
- Git

### 安装命令

```bash
hermes profile install github.com/coyafky/LhqgSalesAgent --alias
```

安装完成后，配置你的 API 密钥：

```bash
# 找到 profile 的 .env 路径
hermes config env-path

# 复制模板并填入密钥
cp .env.EXAMPLE .env
# 编辑 .env，填入 DEEPSEEK_API_KEY、FEISHU_APP_ID、FEISHU_APP_SECRET 等
```

### 快速验证

```bash
hermes chat --profile LhqgSalesAgent -q "你好，自我介绍"
```

## 更新

当仓库有更新时，运行：

```bash
hermes profile update LhqgSalesAgent
```

Hermes 会自动合并变更，同时保留你的 `.env`、会话记录、记忆等本地数据。

## 功能概览

| 功能 | 说明 |
|------|------|
| **CRM 全链路** | 线索录入 → 跟进 → 报价 → 建档 → 工单 → 售后 → 数据分析 |
| **定时 Hook** | 沉睡线索预警 / 回访提醒（自动推送） |
| **产品知识库** | 太阳膜 / 车衣 / 改色膜 / 电动踏板 / 轮毂 / 小米改装 |
| **销售话术** | Mom Test / SPIN / 异议处理 / 战术同理心 / 影响力话术 |
| **改色预览** | 传车型图 + 色号，AI 生成上车效果图 |
| **升单策略** | 结合 CRM 数据，针对性生成增项话术 |
| **新能源车型** | 50 款热门新能源车的销售机会分析 |

## 所需环境变量

| 变量 | 必需 | 说明 |
|------|:----:|------|
| `DEEPSEEK_API_KEY` | ✅ | 主模型 API 密钥 |
| `FEISHU_APP_ID` | ✅ | 飞书应用 App ID（CRM 用） |
| `FEISHU_APP_SECRET` | ✅ | 飞书应用 App Secret |
| `WRAP_PROVIDER_*` | ❌ | 改色生图 API 密钥（可选） |

## 目录结构

```
├── distribution.yaml    # 分发清单
├── SOUL.md              # Agent 系统提示词
├── profile.yaml         # Profile 配置
├── config.yaml          # Hermes 配置（无密钥）
├── .env.EXAMPLE         # 环境变量模板
├── .gitignore
├── skills/              # 内置技能
│   ├── crm/             #   CRM 全链路 7 个技能
│   ├── ark-seedream-*   #   改色预览生图
│   ├── xiaomi-*         #   小米改装知识
│   ├── electric-step-*  #   电动踏板知识
│   └── ...              #   销售话术技能
├── workspace/           # 知识库资产
├── knowledge-base/      # 检索知识库
├── cron/                # 定时任务配置
└── scripts/             # 辅助脚本
```

## 版本历史

- **0.3.0** — CRM 全链路上线（线索→售后 7 步 + 2 个定时 Hook + 升单话术）
- **0.2.1** — 改色预览、小米改装、电动踏板、轮毂知识库
- **0.1.0** — 基础销售话术技能
