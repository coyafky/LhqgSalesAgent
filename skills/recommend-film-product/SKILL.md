---
name: recommend-film-product
description: Use when internal sales asks which car film, window film package, paint protection film, or color-change direction fits a customer's needs.
---

# Recommend Film Product

## Overview

Use this skill to help 有膜有漾 sales staff recommend 隐形车衣、汽车窗膜、车身改色膜, or aftercare guidance based on a customer's vehicle, budget, and buying motive.

## Triggers

Use this skill when the user asks:

- 客户适合贴什么膜
- 怎么推荐套餐
- 预算有限怎么选
- 新车怕剐蹭推荐什么
- 想隔热/隐私/防晒/防爆怎么选

## Required Inputs

Ask or infer these before giving a firm recommendation:

- 车型或车辆级别
- 预算范围
- 主要诉求：漆面保护、隔热、防爆、隐私、外观、性价比
- 用车环境：露天停放、高速多、家用通勤、商务接待、南方暴晒等
- 是否新车、是否已有划痕、是否刚交付

If several inputs are missing, give a provisional recommendation and list the top 2-3 questions sales should confirm.

## 车型知识参考

When the customer's vehicle model is confirmed, consult `references/ne-vehicle-models-guide.md` for:
- 车型定位（SUV/轿车/轿跑/MPV等）和常见车身颜色
- 该车型的常见改装需求（车衣、改色、电动踏板、轮毂、底盘护板等）
- 一句话销售点评（帮门店做推荐的角度）

This helps tailor the recommendation to the specific vehicle rather than giving a generic answer.

The full 50-vehicle knowledge base is at `/Users/fkycoya/蓝火改装/有膜有漾-销售知识库/热门新能源车型50个.md` for deeper reference.

## Workflow

1. Identify the customer's primary motive.
   - 怕剐蹭、石子、鸟粪、酸雨、水垢：优先考虑隐形车衣。
   - 怕晒、车内热、紫外线、隐私：优先考虑汽车窗膜。
   - 想换外观、个性化、保护原漆颜色：考虑改色膜。
2. Match the product tier.
   - 预算稳健或入门保护：推荐基础款，并强调核心保护价值。
   - 中高预算或新车重视质保：推荐更高质保期、更高厚度或更高性能等级产品。
   - 重视隔热和安全防爆：优先推荐总太阳能阻隔率和质保期更高的窗膜套餐。
3. Explain why it fits.
   - 用客户语言表达，不要只堆参数。
   - 每次最多推荐 1 个主推方案 + 1 个升级/备选方案。
4. Add a guardrail.
   - 价格、活动、库存、施工排期以门店最新确认为准。
   - 质保必须按知识库条目和来源页回答。
5. Give the next action.
   - 建议到店看样膜、确认车型、看施工案例、核对套餐、预约施工。

## Response Template

```markdown
建议优先推荐：{产品/套餐}

推荐理由：客户主要关注 {诉求}，这款在 {关键能力} 上更匹配。{用一句客户听得懂的话说明价值}

可以这样跟客户说：
“{80-150 字可直接发送话术}”

下一步：建议先确认 {车型/预算/施工门店/是否要看样膜}，价格和排期以门店最新确认为准。
```

## Guardrails

- Do not invent price, discounts, inventory, or construction duration.
- Do not promise effects beyond the service manual and verified knowledge base.
- If asked for a precise spec, cite the relevant `source_page`.
