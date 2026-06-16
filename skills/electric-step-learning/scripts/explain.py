#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


PROFILE_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_ROOT = PROFILE_ROOT / "workspace" / "04_knowledge" / "eletric-step"
PRODUCTS_FILE = KNOWLEDGE_ROOT / "products.json"


STYLE_ALIASES = {
    "single-light": ["单灯", "带灯", "一灯", "灯款"],
    "double-light": ["双灯", "双灯款", "两灯"],
    "no-light": ["不带灯", "无灯", "不要灯", "低调"],
}


BRAND_ALIASES = {
    "极氪": ["极氪", "009", "MIX"],
    "理想": ["理想", "MEGA", "I6", "I8"],
    "问界": ["问界", "M5", "M7", "M8", "M9"],
    "蔚来": ["蔚来", "ES6", "ES7", "ES8"],
    "小鹏": ["小鹏", "G6", "G9", "X9"],
    "腾势": ["腾势", "D9", "N8", "N9"],
    "比亚迪": ["比亚迪", "唐", "宋", "元", "夏"],
    "方程豹": ["方程豹", "豹5", "豹8", "豹 5", "豹 8"],
    "仰望": ["仰望", "U8"],
    "小米": ["小米", "YU7"],
    "阿维塔": ["阿维塔", "07", "11"],
    "岚图": ["岚图", "梦想家", "FREE"],
    "零跑": ["零跑", "C10", "C11", "C16"],
    "深蓝": ["深蓝", "S07", "G318"],
    "智己": ["智己", "LS6", "LS7"],
}


def load_data():
    if not PRODUCTS_FILE.exists():
        raise SystemExit(f"Missing products file: {PRODUCTS_FILE}")
    return json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))


def normalize(text):
    return re.sub(r"\s+", "", text.upper())


def infer_style_ids(query):
    q = normalize(query)
    ids = []
    for style_id, aliases in STYLE_ALIASES.items():
        if any(normalize(alias) in q for alias in aliases):
            ids.append(style_id)
    return ids


def infer_brand_terms(query):
    q = normalize(query)
    hits = []
    for brand, aliases in BRAND_ALIASES.items():
        if any(normalize(alias) in q for alias in aliases):
            hits.append(brand)
    return hits


def vehicle_score(item, query, brands, style_ids):
    q = normalize(query)
    score = 0
    haystack = normalize(
        " ".join(
            [
                item.get("vehicle_display_name", ""),
                item.get("brand", ""),
                item.get("vehicle_type", ""),
                " ".join(item.get("style_labels", [])),
            ]
        )
    )
    if any(brand == item.get("brand") for brand in brands):
        score += 1
    for token in re.findall(r"[A-Za-z]+\\d+|\\d+|[\\u4e00-\\u9fff]+", query):
        if normalize(token) and normalize(token) in haystack:
            score += 3
    if style_ids and any(style in item.get("style_module_ids", []) for style in style_ids):
        score += 2
    if q and q in haystack:
        score += 5
    return score


def format_load_capacity(value):
    if value in (None, "", "未提供"):
        return "资料未提供"
    text = str(value).upper()
    return text if "KG" in text else f"{text}KG"


def format_waterproof(value):
    if value is True:
        return "支持防水"
    if value is False:
        return "资料未提供"
    if value in (None, ""):
        return "资料未提供"
    return str(value)


def style_module_by_id(data):
    return {item["id"]: item for item in data.get("style_modules", [])}


def image_lines(item):
    lines = []
    for path in item.get("image_paths", []):
        p = Path(path)
        if p.exists():
            lines.append(f"MEDIA:{p}")
    return lines


def missing_image_names(item):
    missing = []
    for name, path in zip(item.get("image_files", []), item.get("image_paths", [])):
        if not Path(path).exists():
            missing.append(name)
    return missing


def format_fitment(item, styles):
    lines = [
        f"## {item['vehicle_display_name']}",
        "",
        f"- 品牌：{item.get('brand', '未提供')}",
        f"- 车型类型：{item.get('vehicle_type', '未提供')}",
        f"- 可选款式：{'、'.join(item.get('style_labels', []))}",
        f"- 承重：{format_load_capacity(item.get('load_capacity_kg'))}",
        f"- 防水：{format_waterproof(item.get('waterproof'))}",
        f"- 质保：{item.get('warranty', '资料未提供')}",
        "",
    ]
    media = image_lines(item)
    if media:
        lines += ["图片：", "", *media, ""]
    else:
        missing = missing_image_names(item)
        if missing:
            lines += [
                "图片状态：",
                "",
                "- 当前知识库有图片文件名，但原图尚未放入 `Image/`：" + "、".join(f"`{name}`" for name in missing),
                "",
            ]
    lines += [
        "销售建议：",
        "",
        "> 这类电动踏板主要解决 SUV/MPV 上下车便利，同时提升迎宾感。夜间用车多可以优先看带灯或双灯款；偏低调实用可以看不带灯款。",
        "",
    ]
    for style_id in item.get("style_module_ids", []):
        style = styles.get(style_id)
        if style:
            lines.append(f"- {style['name']}：{style.get('sales_positioning', '')}")
    return "\n".join(lines)


def build_style_answer(data, style_ids):
    styles = style_module_by_id(data)
    selected = [styles[sid] for sid in style_ids if sid in styles] or data.get("style_modules", [])
    lines = ["# 电动踏板款式模块", ""]
    for style in selected:
        lines += [
            f"## {style['name']}",
            "",
            f"- 原始标签：{style.get('source_label', '未提供')}",
            f"- 模块类型：{style.get('module_type', '未提供')}",
            f"- 销售定位：{style.get('sales_positioning', '未提供')}",
            "",
            "适合客户：",
        ]
        for customer in style.get("customer_fit", []):
            lines.append(f"- {customer}")
        lines += [
            "",
            "对客话术：",
            "",
            f"> {style.get('talk_track', '先确认客户车型、用车场景和预算，再推荐对应款式。')}",
            "",
        ]
    lines += boundary_lines()
    return "\n".join(lines)


def build_overview(data):
    brands = sorted({item.get("brand", "") for item in data.get("fitments", []) if item.get("brand")})
    vehicle_types = sorted({item.get("vehicle_type", "") for item in data.get("fitments", []) if item.get("vehicle_type")})
    lines = [
        "# 蓝辉轻改电动踏板销售学习",
        "",
        "电动踏板可以按 3 个款式模块理解：",
        "",
        "1. 单灯款 / 带灯款：实用基础上增加夜间识别，适合大多数家庭和商务用户。",
        "2. 双灯款：迎宾和展示感更强，适合中大型 SUV/MPV 或想要明显灯光效果的客户。",
        "3. 不带灯款：更低调，核心是上下车便利，适合预算克制或不想要灯光效果的客户。",
        "",
        "当前知识库适配范围：",
        "",
        f"- 适配记录：{len(data.get('fitments', []))} 条",
        f"- 覆盖品牌：{'、'.join(brands)}",
        f"- 车型类型：{'、'.join(vehicle_types)}",
        "- 通用参数：承重 300KG、支持防水、质保 1 年",
        "",
        "销售先问 3 个问题：",
        "",
        "1. 车型是什么，是否为 SUV/MPV/越野 SUV？",
        "2. 主要痛点是老人小孩上下车、商务接待、夜间识别，还是单纯低调实用？",
        "3. 客户更在意展示效果、预算，还是不要灯光？",
        "",
    ]
    lines += boundary_lines()
    return "\n".join(lines)


def boundary_lines():
    return [
        "## 边界",
        "",
        "- 价格、库存、施工工时、安装方案和具体质保范围以门店确认为准。",
        "- 防水当前只能说“支持防水”，不要扩展成具体 IP 等级。",
        "- 原图还未补齐前，不要承诺可直接发完整产品图册。",
    ]


def build_fitment_answer(data, query):
    brands = infer_brand_terms(query)
    style_ids = infer_style_ids(query)
    styles = style_module_by_id(data)
    scored = []
    for item in data.get("fitments", []):
        score = vehicle_score(item, query, brands, style_ids)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda pair: (-pair[0], pair[1].get("sequence", 999)))
    top_score = scored[0][0] if scored else 0
    matches = [item for score, item in scored if score >= max(1, top_score - 2)][:5]
    if not matches:
        if style_ids:
            return build_style_answer(data, style_ids)
        return build_overview(data)
    lines = ["# 电动踏板车型适配查询", ""]
    for item in matches:
        lines.append(format_fitment(item, styles))
        lines.append("")
    lines += boundary_lines()
    return "\n".join(lines)


def main():
    query = " ".join(sys.argv[1:]).strip() or "我想了解电动踏板"
    data = load_data()
    style_ids = infer_style_ids(query)
    brands = infer_brand_terms(query)
    fitment_words = ["能不能", "适配", "车型", "装", "安装", "理想", "问界", "小米", "蔚来", "小鹏", "极氪", "腾势", "比亚迪", "方程豹", "仰望", "阿维塔", "岚图", "零跑", "深蓝", "智己"]
    if brands or any(word in query for word in fitment_words):
        print(build_fitment_answer(data, query))
    elif style_ids or any(word in query for word in ["双灯", "单灯", "带灯", "不带灯", "区别", "款式"]):
        print(build_style_answer(data, style_ids))
    else:
        print(build_overview(data))


if __name__ == "__main__":
    main()
