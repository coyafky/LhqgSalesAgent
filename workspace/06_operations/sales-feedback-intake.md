# 销售反馈收集

## 反馈类型

- 客户问题答不上来。
- 话术不自然。
- 推荐不符合门店实际。
- 参数或质保疑似错误。
- 门店政策需要更新。
- 改色效果图不符合预期。

## 反馈格式

```markdown
日期：
反馈人：
客户原话：
Agent 原回答：
问题类型：
期望回答：
是否涉及门店政策：
是否需要进入知识库：
```

## 处理规则

- 知识错误：进入 `04_knowledge-rag/data-quality-backlog.md`。
- 话术问题：进入 `02_sales-assets/talk-track-library.md` 或 skill reference。
- 验收缺口：进入 `05_evaluation/acceptance-queries.md`。
- 政策问题：不得直接写入长期知识库，需单独管理有效期。

