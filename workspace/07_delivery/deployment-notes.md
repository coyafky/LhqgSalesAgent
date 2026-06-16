# 部署协作说明

## Hermes 运行配置

- `profile.yaml`：profile 元信息、技能列表、知识库和生图配置。
- `config.yaml`：本机模型、工具和终端配置。
- `distribution.yaml`：profile distribution 清单。

## 不应提交的运行态数据

- `.env`
- `auth.json`
- `sessions/`
- `logs/`
- `memories/`
- `state.db*`

## Workspace 与部署的关系

`workspace/` 是项目协作层文档，可以随 profile distribution 一起版本管理；但它不应包含密钥、真实客户隐私、临时聊天记录或门店未公开政策明细。

