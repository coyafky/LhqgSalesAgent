# 米沃供应商产品知识库

本目录由供应商图册 `2025.12.06-米沃图册.pdf` 解析生成，用于有膜有漾 Sales Agent 学习和检索小米 SU7 / YU7 改装件资料。

## 目录结构

```text
miwo/
├── README.md
├── products.json
├── product-catalog.md
├── su7-product-cards.md
├── yu7-product-cards.md
├── supplier-profile.md
├── sales-knowledge.md
├── sales-qa.md
├── source-boundary.md
├── data-quality-issues.md
└── raw/
    ├── pdf-info.json
    ├── text/
    ├── pages/
    └── images/
```

## 已解析内容

- PDF 页数：47 页
- 产品数量：30 个
- 覆盖车型：SU7、YU7
- 页面截图：`raw/pages/`
- 嵌入图片：`raw/images/`
- 结构化产品数据：`products.json`

## 给 Agent 的使用建议

- 查产品参数时优先读取 `products.json`。
- 给销售看图时使用 `product-catalog.md` 或单车型知识卡。
- 生成对客话术时必须参考 `source-boundary.md`，不要编造价格、库存、交期、质保和备案结论。
- 遇到 `data-quality-issues.md` 中列出的疑点，必须提示销售先确认。
