---
name: crm-sleeping-lead-hook
description: 定时 hook — 每天自动检查线索跟进状态，发现超过N天未跟进的沉睡线索，推送提醒给销售和店长
requires:
  - lark-base
base:
  base_url: https://wcnqctja2tue.feishu.cn/base/Q6VQbuLTOaPP5VspfKXc7ZbTnA8
  base_token: Q6VQbuLTOaPP5VspfKXc7ZbTnA8
  identity: --as bot
---

# CRM沉睡线索预警Hook

## 概述

这是一个**定时执行的数据检查 hook**，不是销售主动调用的 skill。每天自动运行一次，查询 CRM 中超过指定天数未跟进的线索，生成预警报告并推送到指定渠道。

## 共享引用

执行前按需读取：

- `../references/base.md` — Base token、身份、时区、隐私边界。
- `../references/schema.md` — 线索、跟进记录、销售人员字段。
- `../references/idempotency.md` — `lead record_id + alert level + date` 防重复规则。
- `../references/people-products.md` — 销售提醒对象解析。

**触发方式：** 通过 `cronjob` 设置每日定时任务
**目标：** 减少线索浪费，提升跟进时效

## 预警规则

| 规则 | 检查条件 | 预警级别 | 提醒对象 |
|------|---------|:--------:|---------|
| 轻度沉睡 | 线索状态=已分配，且超过 **7 天**无跟进记录 | 🟡 黄色 | 销售本人 |
| 中度沉睡 | 线索状态=已分配，且超过 **14 天**无跟进记录 | 🟠 橙色 | 销售本人 + 店长 |
| 深度沉睡 | 线索状态=已分配，且超过 **30 天**无跟进记录 | 🔴 红色 | 店长（建议重新分配或标记无效） |
| 报价跟进慢 | 报价状态=已发客户/跟进中，且超过 **7 天**无新跟进 | 🟡 黄色 | 销售本人 |

## 执行流程

### 第一步：查询沉睡线索

查询线索管理表，筛选条件：
- 线索状态 = "已分配"
- 创建时间 > 30天前（避免刚创建的线索）
- 无关联跟进记录，或最后跟进日期 > N 天前

```bash
# 查询所有已分配线索及最后跟进日期
lark-cli base +data-query --base-token Q6VQbuLTOaPP5VspfKXc7ZbTnA8 --dsl '{
  "datasource": {"type":"table","table":{"tableId":"tblHsrpSsTmJnB0c"}},
  "dimensions":[{"field_name":"客户姓名","alias":"customer"}],
  "measures":[{"field_name":"创建时间","aggregation":"max","alias":"created_at"}],
  "filters":{"type":1,"conjunction":"and","conditions":[
    {"field_name":"线索状态","operator":"is","value":["已分配"]}
  ]},
  "shaper":{"format":"flat"}
}'
```

> 注：由于 data-query 无法跨表 join，实际检查逻辑需要通过脚本组合多表查询。

### 第二步：查询跟进记录

查询跟进记录表中该客户最近一次跟进日期。

### 第三步：计算沉睡天数

对比当前日期与最后跟进日期，计算差值。

### 第四步：生成预警报告

```markdown
⏰ 沉睡线索预警报告
📅 日期：2026-06-15

🔴 深度沉睡（>30天无跟进）— 需店长介入
┌────────────────────────────────────────────┐
│ 客户     销售      天数     意向            │
│ 王**    刘志培     35天     隐形车衣        │
│ 李**    吕佳豪     32天     电动踏板        │
└────────────────────────────────────────────┘

🟠 中度沉睡（>14天无跟进）
┌────────────────────────────────────────────┐
│ 客户     销售      天数     意向            │
│ 陈**    张秋苑     18天     窗膜            │
└────────────────────────────────────────────┘

🟡 轻度沉睡（>7天无跟进）
┌────────────────────────────────────────────┐
│ 客户     销售      天数     意向            │
│ 赵**    刘志培     9天      改色膜          │
│ 钱**    吕佳豪     8天      轻改装          │
└────────────────────────────────────────────┘

💡 建议动作：
- 深度沉睡 → 店长联系客户确认意向，或标记无效
- 中度沉睡 → 销售今天内安排跟进
- 轻度沉睡 → 销售本周内安排跟进
```

## 定时配置

建议使用 cronjob 设置每日执行：

```bash
# 每天早上 9:30 执行检查
cronjob action=create \
  schedule="30 9 * * *" \
  name="沉睡线索预警检查" \
  prompt="执行CRM沉睡线索预警检查，查询超过7/14/30天未跟进的已分配线索，生成预警报告并推送" \
  skills="crm-analytics,crm-lead-entry" \
  deliver="origin"
```

## 脚本检查方案

由于飞书 data-query 不支持跨表 join，实际线索→跟进记录的关联检查建议通过脚本实现：

```python
# 伪代码逻辑
from datetime import datetime, timedelta

def check_sleeping_leads():
    # 1. 获取所有已分配线索（含客户姓名、销售负责人、创建时间）
    leads = get_records("线索管理", filter={"线索状态": "已分配"})

    for lead in leads:
        # 2. 获取该线索的最近跟进记录
        followups = get_records("跟进记录", filter={"线索": lead["record_id"]})

        # 3. 计算沉睡天数
        if not followups:
            # 无跟进记录 → 从创建时间算起
            days = (datetime.now() - lead["创建时间"]).days
        else:
            # 有跟进记录 → 从最后跟进日期算起
            last_followup = max(f["跟进日期"] for f in followups)
            days = (datetime.now() - last_followup).days

        # 4. 判断预警级别
        if days >= 30:
            level = "🔴 深度沉睡"
        elif days >= 14:
            level = "🟠 中度沉睡"
        elif days >= 7:
            level = "🟡 轻度沉睡"
        else:
            continue  # 正常跟进，跳过

        alerts.append({"客户": lead["客户姓名"],
                       "销售": lead["销售负责人"],
                       "天数": days,
                       "意向": lead["意向产品类型"],
                       "级别": level})

    # 5. 按级别分组输出报告
    return format_report(alerts)
```

## 推送方式

| 预警级别 | 推送对象 | 推送渠道 |
|---------|---------|---------|
| 🔴 深度沉睡 | 店长 | 飞书消息 |
| 🟠 中度沉睡 | 店长 + 销售 | 飞书消息 |
| 🟡 轻度沉睡 | 销售 | 飞书消息 |

推送前按 `../references/idempotency.md` 检查当天同一线索、同一预警级别是否已提醒，避免重复打扰销售。

## 安装步骤

1. 确认 cronjob 能力已启用
2. 创建定时任务：
   ```
   cronjob action=create schedule="30 9 * * *" name="沉睡线索预警" prompt="执行CRM沉睡线索预警检查，生成预警报告" skills="crm-analytics" deliver="origin"
   ```
3. 验证：首次执行后查看推送结果
4. 可根据门店营业时间调整执行频率（建议工作日执行）

## 关联 Skill

- `crm-analytics` — 数据查询能力
- `crm-lead-entry` — 线索状态更新
