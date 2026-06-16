#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


PROFILE_ROOT = Path(__file__).resolve().parents[3]
XIAOMI_ROOT = PROFILE_ROOT / "workspace" / "04_knowledge" / "xiaomi"
XIAOMI_PRODUCTS = XIAOMI_ROOT / "products.json"
MIWO_PRODUCTS = XIAOMI_ROOT / "miwo" / "products.json"


EXTERIOR_TERMS = {
    "前包围", "后包围", "前杠", "后杠", "侧裙", "机盖", "尾翼", "电动尾翼",
    "后视镜", "后视镜壳", "大灯饰板", "风道口", "扰流板", "鸭尾"
}
INTERIOR_TERMS = {
    "方向盘", "中控", "中控面板", "中控台", "出风口", "门饰条", "迎宾踏板",
    "座椅背板", "仪表台", "刹车油门踏板"
}
COVER_TERMS = {"座椅", "顶棚", "ABC", "门板", "扶手箱", "包覆"}

PRODUCT_ALIASES = {
    "前包围": ["前包围", "前杠"],
    "后包围": ["后包围", "后杠"],
    "后视镜": ["后视镜", "后视镜壳"],
    "后视镜壳": ["后视镜", "后视镜壳"],
    "尾翼": ["尾翼", "扰流板", "鸭尾"],
    "后扰流板": ["扰流板", "尾翼"],
    "中控面板": ["中控面板", "中控", "仪表台"],
    "出风口": ["出风口", "风道口"],
    "迎宾踏板": ["迎宾踏板"],
    "刹车油门踏板": ["刹车油门踏板", "刹车", "油门"],
    "方向盘": ["方向盘"],
    "侧裙": ["侧裙"],
    "机盖": ["机盖"],
    "座椅背板": ["座椅背板", "座椅后饰板"],
    "门饰条": ["门饰条", "门板", "四门饰板"],
    "大灯饰板": ["大灯饰板", "前大灯饰板"],
}


def load_json(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f).get("products", [])


def normalize(text):
    return re.sub(r"\s+", "", text.upper())


def infer_model(query):
    q = normalize(query)
    if "YU7" in q:
        return "YU7"
    if "SU7" in q:
        return "SU7"
    return None


def infer_category(name):
    if any(term in name for term in EXTERIOR_TERMS):
        return "外观姿态"
    if any(term in name for term in INTERIOR_TERMS):
        return "内饰质感"
    if any(term in name for term in COVER_TERMS):
        return "包覆升级"
    return "产品款式"


def product_score(product, query, model):
    q = query.upper()
    name = product["product_name"]
    score = 0
    if model and product["vehicle_model"] == model:
        score += 4
    for term in EXTERIOR_TERMS | INTERIOR_TERMS | COVER_TERMS:
        if term and term in query and term in name:
            score += 8
    if name in query:
        score += 10
    if product["vehicle_model"] in q:
        score += 2
    return score


def focus_terms_for_query(query):
    terms = []
    for term in sorted(EXTERIOR_TERMS | INTERIOR_TERMS | COVER_TERMS, key=len, reverse=True):
        if term and term in query:
            terms.append(term)
    return terms


def product_matches_focus(product, focus_terms):
    if not focus_terms:
        return True
    name = product["product_name"]
    for term in focus_terms:
        aliases = PRODUCT_ALIASES.get(term, [term])
        if any(alias in name for alias in aliases):
            return True
    return False


def find_miwo_specs(miwo_products, model, product_name):
    terms = PRODUCT_ALIASES.get(product_name, [product_name])
    matches = []
    for item in miwo_products:
        if item.get("model") != model:
            continue
        haystack = "".join(str(item.get(k, "")) for k in ["name", "position", "series", "category"])
        if any(t in haystack for t in terms):
            matches.append(item)
    return matches[:2]


def image_md(product):
    image_path = Path(product["image"]["absolute_path"])
    return f"MEDIA:{image_path}"


def build_overview(products, miwo_products, model=None):
    selected = [p for p in products if not model or p["vehicle_model"] == model]
    title_model = model if model else "小米 SU7 / YU7"
    grouped = {"外观姿态": [], "内饰质感": [], "包覆升级": [], "产品款式": []}
    for p in selected:
        grouped[infer_category(p["product_name"])].append(p)

    lines = [
        f"# {title_model} 改装产品图文学习",
        "",
        "可以先按 3 条线理解：",
        "",
        "1. 外观姿态：前包围、侧裙、机盖、尾翼、后视镜等，让客户第一眼看到变化。",
        "2. 内饰质感：方向盘、中控、出风口、门饰条、迎宾踏板等，提升日常可见和可触摸的位置。",
        "3. 包覆升级：座椅、顶棚、ABC 柱、门板、中控仪表台等，属于更深度的内饰定制；当前主要来自米沃 SU7 图册。",
        "",
        "## 快速产品地图",
        "",
    ]
    for category in ["外观姿态", "内饰质感", "包覆升级", "产品款式"]:
        names = [f"{p['vehicle_model']} {p['product_name']}" for p in grouped[category]]
        if names:
            lines.append(f"- {category}：" + "、".join(names))
    lines += ["", "## 代表图片", ""]

    representative = []
    for category in ["外观姿态", "内饰质感"]:
        representative.extend(grouped[category][:3])
    if not representative:
        representative = selected[:6]
    for p in representative[:6]:
        lines += [f"### {p['display_name']}", image_md(p), ""]

    lines += [
        "## 销售怎么讲",
        "",
        "> 小米改装先不要一上来讲一堆 SKU，先问客户想改变外观姿态、内饰质感，还是只做局部点缀。确认车型后，再给他看对应图片和部位。",
        "",
        "## 下一步确认",
        "",
        "- 车型：SU7 还是 YU7，年款是否匹配。",
        "- 方向：外观、内饰、包覆，还是局部小件。",
        "- 门店确认：价格、库存、安装工时、质保、是否需要备案。",
        "",
        "## 边界",
        "",
        "- 资料来自内部款式表和供应商图册，不要说成小米官方原厂件。",
        "- 不要编造价格、库存、施工周期、质保或备案结论。",
    ]
    return "\n".join(lines)


def build_specific(products, miwo_products, query, model=None):
    focus_terms = focus_terms_for_query(query)
    scored = []
    for p in products:
        if not product_matches_focus(p, focus_terms):
            continue
        score = product_score(p, query, model)
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: (-x[0], x[1]["vehicle_model"], x[1]["order_in_model"]))
    matches = [p for _, p in scored[:6]]
    if not matches:
        return build_overview(products, miwo_products, model)

    lines = ["# 小米改装产品图文讲解", ""]
    for p in matches:
        category = infer_category(p["product_name"])
        specs = find_miwo_specs(miwo_products, p["vehicle_model"], p["product_name"])
        lines += [
            f"## {p['display_name']}",
            "",
            image_md(p),
            "",
            "### 产品理解",
            "",
            f"- 车型：{p['vehicle_model']}",
            f"- 类别：{category}",
            f"- 部位：{p['product_name']}",
        ]
        if specs:
            s = specs[0]
            lines += [
                "- 供应商图册参数：",
                f"  - 名称：{s.get('name', '未提供')}",
                f"  - 编码：{s.get('code') or '资料未提供'}",
                f"  - 材质：{s.get('material') or '资料未提供'}",
                f"  - 重量：{s.get('weight') or '资料未提供'}",
                f"  - 来源：米沃图册 PDF p.{s.get('pdf_page')}",
            ]
            if s.get("notes"):
                lines.append("  - 待确认：" + "；".join(s["notes"]))
        else:
            lines.append("- 供应商图册参数：当前未匹配到，先按图片款式讲解，参数需门店确认。")

        if category == "外观姿态":
            talk = "这类产品主要改变车身外观姿态，适合客户想让车更运动、更个性化。"
        elif category == "内饰质感":
            talk = "这类产品更偏向座舱质感升级，客户每天开车都会看到或摸到。"
        elif category == "包覆升级":
            talk = "这类产品偏深度内饰定制，需要确认材质、颜色和施工范围。"
        else:
            talk = "这个产品适合做局部升级，建议结合客户想改的位置继续确认。"
        lines += [
            "",
            "### 可以这样跟客户说",
            "",
            f"> {talk} 如果您喜欢这个风格，我先帮您确认适配、价格、库存、安装方式和质保。",
            "",
        ]

    lines += [
        "## 边界",
        "",
        "- 不要说成小米官方原厂件。",
        "- 价格、库存、安装工时、质保和备案需要门店确认。",
    ]
    return "\n".join(lines)


def main():
    query = " ".join(sys.argv[1:]).strip() or "我想了解小米的改装"
    products = load_json(XIAOMI_PRODUCTS)
    miwo_products = load_json(MIWO_PRODUCTS)
    if not products:
        raise SystemExit(f"Missing products file: {XIAOMI_PRODUCTS}")
    model = infer_model(query)
    broad_terms = ["了解", "介绍", "有哪些", "全部", "总览", "学习", "改装"]
    specific_terms = EXTERIOR_TERMS | INTERIOR_TERMS | COVER_TERMS
    is_specific = any(t in query for t in specific_terms)
    if not is_specific and any(t in query for t in broad_terms):
        print(build_overview(products, miwo_products, model))
    else:
        print(build_specific(products, miwo_products, query, model))


if __name__ == "__main__":
    main()
