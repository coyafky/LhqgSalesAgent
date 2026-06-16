# 小米产品款式知识库

本目录由 `小米产品款式.xls` 解析生成，用于给 Hermes Sales Agent 检索小米 SU7 / YU7 相关产品款式与图片。

## 文件结构

```text
xiaomi/
├── README.md
├── products.json
├── image-manifest.json
├── products.md
├── SU7.md
├── YU7.md
├── preview-contact-sheet.png
└── Image/
    ├── SU7/
    └── YU7/
```

## 数据说明

- 产品数量：18
- 图片数量：18
- 车型：SU7, YU7
- 图片目录：`Image/`
- 结构化产品索引：`products.json`
- 图片清单：`image-manifest.json`
- 人工预览图：`preview-contact-sheet.png`

## 关联规则

图片从老式 Excel `.xls` 的 BIFF `MSODRAWINGGROUP` / `MSODRAWING` / `CONTINUE` 记录中重组提取。图片按 Workbook 内 PNG 出现顺序，与 Excel 中非空产品行顺序一一匹配。当前产品数和图片数均为 18，数量一致。

## 使用建议

- 给 Agent 检索时优先读取 `products.json`。
- 给销售或人工查看时使用 `products.md`、`SU7.md`、`YU7.md`。
- 对外展示图片时使用 `Image/<车型>/<文件名>.png` 中的相对路径。
