# 飞书多维表格接入说明

## 当前接入结果

- ✅ **Base URL：** `https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- ✅ **Base token：** `Q6VQbuLTOaPP5VspfKXc7ZbTnA8`
- ✅ **Base 名称：** 有膜有漾 CRM
- ✅ **目标表：** 线索管理（`tblHsrpSsTmJnB0c`）
- ✅ **销售人员表：** 销售人员表（`tblhP4v00FNjYQnm`）
- ✅ **身份：** `--as bot`（有膜有漾销售助理）

## 表结构总览

| 表名 | 表 ID | 用途 |
|------|-------|------|
| 线索管理 | `tblHsrpSsTmJnB0c` | 新增线索、查看线索列表 |
| 报价表 | `tblzGNVSFPSXgb9K` | 报价记录 |
| 工单表 | `tblntyv0q6aS6Y3v` | 施工工单 |
| 售后表 | `tbliYr7rZow5cBIq` | 售后处理 |
| 客户车辆档案表 | `tblV6qrgb7Xef1N7` | 已成交客户车辆档案 |
| 跟进记录 | `tblx0u6u4N1Vv2vY` | 每次沟通记录 |
| 产品项目表 | `tblbfqLLrnxyOMIt` | 产品/项目信息 |
| 销售人员表 | `tblhP4v00FNjYQnm` | 销售员工信息 |

## 常用命令

### 1. 查看表列表

```bash
lark-cli base +table-list --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --as bot
```

### 2. 查看字段列表

```bash
lark-cli base +field-list --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --table-id tblHsrpSsTmJnB0c --as bot
```

### 3. 新增线索记录

```bash
lark-cli base +record-upsert \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblHsrpSsTmJnB0c \
  --json '{"客户姓名":"王先生","电话":"17620770627","来源渠道":"抖音","销售负责人":[{"id":"rec6gBu3IVdtim"}],"车辆品牌":"问界","车型":"SUV","意向产品类型":["轻改装"],"线索状态":"已分配","线索描述":"问界M9，咨询电动踏板"}' \
  --as bot
```

### 4. 搜索记录

```bash
lark-cli base +record-search \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblHsrpSsTmJnB0c \
  --keyword "王" \
  --search-field fldC6n9VPy \
  --as bot
```

### 5. 查看单条记录

```bash
lark-cli base +record-get \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblHsrpSsTmJnB0c \
  --record-id <record_id> \
  --as bot
```

### 6. 查看销售人员表（获取负责人 ID）

```bash
lark-cli base +record-list \
  --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 \
  --table-id tblhP4v00FNjYQnm \
  --as bot
```

## 写入注意事项

1. **销售负责人是关联字段** — 使用 `[{"id": "recXXX"}]` 格式传入销售人员表的 record_id，不直接写姓名。
2. **意向产品类型是多选** — 使用数组格式 `["轻改装"]`。
3. **线索状态** — 新建并指定负责人时设为「已分配」。
4. **车型是单选** — 仅支持「SUV」「轿车」「MPV」三个选项。
5. **写前必查重** — 搜索客户姓名+车型，或手机号，避免重复创建相同客户。
6. **写前必确认** — 任何写入操作前必须向用户展示确认摘要，待用户回复「确认写入」后才执行。
