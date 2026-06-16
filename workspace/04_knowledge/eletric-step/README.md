# 蓝辉轻改电动踏板知识库

本目录用于 Hermes Sales Agent 检索和讲解电动踏板产品，路径保留用户指定拼写：`eletric-step`。

## 当前内容

- 产品族：电动踏板
- 模块分类：单灯款 / 带灯款、双灯款、不带灯款
- 适配车型记录：21 条
- 覆盖品牌：仰望, 小米, 小鹏, 岚图, 方程豹, 智己, 极氪, 比亚迪, 深蓝, 理想, 腾势, 蔚来, 问界, 阿维塔, 零跑
- 车型类型：新能源 SUV、MPV、越野 SUV
- 通用参数：承重 300KG、支持防水、质保 1 年

## 文件结构

```text
eletric-step/
├── README.md
├── products.json
├── image-manifest.json
├── style-modules.md
├── fitment-table.md
├── sales-knowledge.md
├── sales-qa.md                  # 按客户决策链条组织的销售 QA
├── source-boundary.md
├── data-quality-issues.md
├── Image/
└── raw/
```

## 图片状态

Excel 只提供图片文件名，没有嵌入图片文件。请把以下 3 张图片放入 `Image/` 后，知识库引用会自动对应：

- `mmexport1780990252734.jpg`
- `mmexport1780990258176.jpg`
- `mmexport1780990445714.jpg`

## Agent 使用建议

- 查车型是否适配：读取 `products.json.fitments`。
- 讲三种款式区别：读取 `style-modules.md`。
- 给销售培训：读取 `sales-knowledge.md` 和 `sales-qa.md`；其中 `sales-qa.md` 可用于判断客户处在认知、适配、款式选择、风险评估、价格成交或预约阶段。
- 对外承诺前：读取 `source-boundary.md`。
