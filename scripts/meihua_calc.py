#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path


TRIGRAMS = {
    1: {"name": "乾", "element": "金", "lines": [1, 1, 1]},
    2: {"name": "兑", "element": "金", "lines": [1, 1, 0]},
    3: {"name": "离", "element": "火", "lines": [1, 0, 1]},
    4: {"name": "震", "element": "木", "lines": [1, 0, 0]},
    5: {"name": "巽", "element": "木", "lines": [0, 1, 1]},
    6: {"name": "坎", "element": "水", "lines": [0, 1, 0]},
    7: {"name": "艮", "element": "土", "lines": [0, 0, 1]},
    8: {"name": "坤", "element": "土", "lines": [0, 0, 0]},
}

HEXAGRAM_NAMES = {
    ("乾", "乾"): "乾为天",
    ("坤", "坤"): "坤为地",
    ("坎", "震"): "水雷屯",
    ("艮", "坎"): "山水蒙",
    ("坎", "乾"): "水天需",
    ("乾", "坎"): "天水讼",
    ("坤", "坎"): "地水师",
    ("坎", "坤"): "水地比",
    ("巽", "乾"): "风天小畜",
    ("乾", "兑"): "天泽履",
    ("坤", "乾"): "地天泰",
    ("乾", "坤"): "天地否",
    ("乾", "离"): "天火同人",
    ("离", "乾"): "火天大有",
    ("坤", "艮"): "地山谦",
    ("震", "坤"): "雷地豫",
    ("兑", "震"): "泽雷随",
    ("艮", "巽"): "山风蛊",
    ("坤", "兑"): "地泽临",
    ("巽", "坤"): "风地观",
    ("离", "震"): "火雷噬嗑",
    ("艮", "离"): "山火贲",
    ("艮", "坤"): "山地剥",
    ("坤", "震"): "地雷复",
    ("乾", "震"): "天雷无妄",
    ("艮", "乾"): "山天大畜",
    ("艮", "震"): "山雷颐",
    ("兑", "巽"): "泽风大过",
    ("坎", "坎"): "坎为水",
    ("离", "离"): "离为火",
    ("兑", "艮"): "泽山咸",
    ("震", "巽"): "雷风恒",
    ("乾", "艮"): "天山遁",
    ("震", "乾"): "雷天大壮",
    ("离", "坤"): "火地晋",
    ("坤", "离"): "地火明夷",
    ("巽", "离"): "风火家人",
    ("离", "兑"): "火泽睽",
    ("坎", "艮"): "水山蹇",
    ("震", "坎"): "雷水解",
    ("艮", "兑"): "山泽损",
    ("巽", "震"): "风雷益",
    ("兑", "乾"): "泽天夬",
    ("乾", "巽"): "天风姤",
    ("兑", "坤"): "泽地萃",
    ("坤", "巽"): "地风升",
    ("兑", "坎"): "泽水困",
    ("坎", "巽"): "水风井",
    ("兑", "离"): "泽火革",
    ("离", "巽"): "火风鼎",
    ("震", "震"): "震为雷",
    ("艮", "艮"): "艮为山",
    ("巽", "艮"): "风山渐",
    ("震", "兑"): "雷泽归妹",
    ("震", "离"): "雷火丰",
    ("离", "艮"): "火山旅",
    ("巽", "巽"): "巽为风",
    ("兑", "兑"): "兑为泽",
    ("巽", "坎"): "风水涣",
    ("坎", "兑"): "水泽节",
    ("巽", "兑"): "风泽中孚",
    ("震", "艮"): "雷山小过",
    ("坎", "离"): "水火既济",
    ("离", "坎"): "火水未济",
}

GENERATES = {
    "金": "水",
    "水": "木",
    "木": "火",
    "火": "土",
    "土": "金",
}

CONTROLS = {
    "金": "木",
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
}


def mod_pick(value: int, base: int) -> int:
    remainder = value % base
    return remainder if remainder != 0 else base


def parse_digits(digits, packed):
    if digits and len(digits) == 2:
        return int(digits[0]), int(digits[1])
    if packed:
        text = packed.strip()
        if len(text) != 2 or not text.isdigit():
            raise ValueError("--packed 目前只支持两位数字，例如 78。")
        return int(text[0]), int(text[1])
    raise ValueError("请提供 --digits 7 8 或 --packed 78。")


def lines_to_hexagram(upper_lines, lower_lines):
    return lower_lines + upper_lines


def flip_line(lines, moving_line):
    changed = list(lines)
    idx = moving_line - 1
    changed[idx] = 1 - changed[idx]
    return changed


def find_trigram_by_lines(lines):
    for number, info in TRIGRAMS.items():
        if info["lines"] == lines:
            return number, info
    raise ValueError(f"未找到对应三爻: {lines}")


def relation_of(body_element, use_element):
    if body_element == use_element:
        return "体用比和"
    if GENERATES[body_element] == use_element:
        return "体生用"
    if GENERATES[use_element] == body_element:
        return "用生体"
    if CONTROLS[body_element] == use_element:
        return "体克用"
    if CONTROLS[use_element] == body_element:
        return "用克体"
    return "关系待补充"


def verdict_for_relation(relation):
    mapping = {
        "体用比和": "吉。体用同气，整体较顺。",
        "体生用": "小吉。事情可成，但自己会更费神费力。",
        "用生体": "吉。外部条件对自己有助力，推进较顺。",
        "体克用": "吉。能掌控事情，但过程可能有压力。",
        "用克体": "凶。事情压制自己，宜谨慎。",
    }
    return mapping.get(relation, "中性。当前规则未覆盖完整断法。")


def top_to_bottom_lines(lines):
    return list(reversed(lines))


def line_word(value):
    return "阳" if value == 1 else "阴"


def trigram_visual_signature(lines):
    return " / ".join(line_word(v) for v in top_to_bottom_lines(lines))


def moving_line_change(lines, moving_line):
    original = lines[moving_line - 1]
    changed = 1 - original
    return {
        "index_from_bottom": moving_line,
        "index_from_top": 7 - moving_line,
        "original_value": original,
        "changed_value": changed,
        "original_word": line_word(original),
        "changed_word": line_word(changed),
        "instruction": f"第{moving_line}爻按自下而上计数，原为{line_word(original)}，变化后为{line_word(changed)}。",
    }


def render_line(y, is_yang, highlight=False, x=40):
    color = "#b45309" if highlight else "#111111"
    stroke = f'fill="{color}"'
    if is_yang:
        return f'<rect x="{x}" y="{y}" width="160" height="14" rx="3" {stroke} />'
    left = f'<rect x="{x}" y="{y}" width="68" height="14" rx="3" {stroke} />'
    right = f'<rect x="{x + 92}" y="{y}" width="68" height="14" rx="3" {stroke} />'
    return left + right


def svg_text(text):
    return html.escape(str(text), quote=False)


def render_hexagram_group(x, y, lines, title, moving_line=None, subtitle=None):
    parts = [
        f'<text x="{x + 90}" y="{y}" text-anchor="middle" font-size="18" fill="#7c4a1d">{svg_text(title)}</text>'
    ]
    if len(lines) == 3:
        y_positions = [y + 130, y + 85, y + 40]
        subtitle_y = y + 175
    else:
        y_positions = [y + 190, y + 155, y + 120, y + 85, y + 50, y + 15]
        subtitle_y = y + 225
    for idx, line in enumerate(lines, start=1):
        parts.append(
            render_line(
                y_positions[idx - 1],
                line == 1,
                highlight=moving_line == idx,
                x=x + 10,
            )
        )
    if subtitle:
        parts.append(
            f'<text x="{x + 90}" y="{subtitle_y}" text-anchor="middle" font-size="12" fill="#6b7280">{svg_text(subtitle)}</text>'
        )
    return "".join(parts)


def render_panel(x, y, w, h, title, step_label):
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="28" fill="rgba(255,253,248,0.92)" stroke="#dcc7a1" stroke-width="1.5"/>',
            f'<circle cx="{x + 38}" cy="{y + 38}" r="20" fill="#8a5a2b"/>',
            f'<text x="{x + 38}" y="{y + 45}" text-anchor="middle" font-size="18" fill="#fff8ef">{svg_text(step_label)}</text>',
            f'<text x="{x + 72}" y="{y + 46}" font-size="26" fill="#6f431c">{svg_text(title)}</text>',
        ]
    )


def render_chip(x, y, w, text, fill="#f7efe0", stroke="#e2cfaa", color="#4b5563", size=18):
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="17" fill="{fill}" stroke="{stroke}"/>',
            f'<text x="{x + 16}" y="{y + 23}" font-size="{size}" fill="{color}">{svg_text(text)}</text>',
        ]
    )


def render_element_badge(x, y, element):
    palette = {
        "金": ("#f4ead2", "#b78b2e", "#6c5314"),
        "木": ("#e3f0e6", "#4f8a5b", "#1e4d2b"),
        "水": ("#e2eef8", "#4b7ca8", "#1f4f73"),
        "火": ("#f8e4de", "#c55a3d", "#7b2f1d"),
        "土": ("#efe3d1", "#9a7342", "#5f4521"),
    }
    fill, stroke, text_color = palette[element]
    return "".join(
        [
            f'<rect x="{x}" y="{y}" width="52" height="28" rx="14" fill="{fill}" stroke="{stroke}"/>',
            f'<text x="{x + 26}" y="{y + 20}" text-anchor="middle" font-size="16" fill="{text_color}">{element}</text>',
        ]
    )


def render_relation_diagram(x, y, body_name, body_element, use_name, use_element, relation, verdict):
    parts = [
        f'<rect x="{x}" y="{y}" width="340" height="214" rx="22" fill="#f8f4ec" stroke="#e3d5ba"/>',
        f'<text x="{x + 24}" y="{y + 32}" font-size="20" fill="#6f431c">体用判断</text>',
        f'<circle cx="{x + 88}" cy="{y + 104}" r="42" fill="#fffaf1" stroke="#d5bea0" stroke-width="2"/>',
        f'<text x="{x + 88}" y="{y + 100}" text-anchor="middle" font-size="18" fill="#111827">体</text>',
        f'<text x="{x + 88}" y="{y + 124}" text-anchor="middle" font-size="16" fill="#6b7280">{svg_text(body_name)}</text>',
        f'<circle cx="{x + 252}" cy="{y + 104}" r="42" fill="#fffaf1" stroke="#d5bea0" stroke-width="2"/>',
        f'<text x="{x + 252}" y="{y + 100}" text-anchor="middle" font-size="18" fill="#111827">用</text>',
        f'<text x="{x + 252}" y="{y + 124}" text-anchor="middle" font-size="16" fill="#6b7280">{svg_text(use_name)}</text>',
        f'<line x1="{x + 132}" y1="{y + 104}" x2="{x + 208}" y2="{y + 104}" stroke="#8a5a2b" stroke-width="2.5" marker-end="url(#arrow-brown)"/>',
        f'<text x="{x + 170}" y="{y + 90}" text-anchor="middle" font-size="16" fill="#8a5a2b">{svg_text(relation)}</text>',
        render_element_badge(x + 62, y + 146, body_element),
        render_element_badge(x + 226, y + 146, use_element),
        f'<text x="{x + 24}" y="{y + 192}" font-size="16" fill="#4b5563">{svg_text(verdict)}</text>',
    ]
    return "".join(parts)


def render_five_element_chart(x, y):
    nodes = {
        "金": (x + 160, y + 26),
        "水": (x + 288, y + 116),
        "木": (x + 238, y + 256),
        "火": (x + 82, y + 256),
        "土": (x + 32, y + 116),
    }
    generates = [("金", "水"), ("水", "木"), ("木", "火"), ("火", "土"), ("土", "金")]
    controls = [("金", "木"), ("木", "土"), ("土", "水"), ("水", "火"), ("火", "金")]
    palette = {
        "金": ("#f4ead2", "#b78b2e", "#6c5314"),
        "木": ("#e3f0e6", "#4f8a5b", "#1e4d2b"),
        "水": ("#e2eef8", "#4b7ca8", "#1f4f73"),
        "火": ("#f8e4de", "#c55a3d", "#7b2f1d"),
        "土": ("#efe3d1", "#9a7342", "#5f4521"),
    }
    parts = [
        f'<rect x="{x}" y="{y}" width="320" height="286" rx="22" fill="#f8f4ec" stroke="#e3d5ba"/>',
        f'<text x="{x + 24}" y="{y + 34}" font-size="20" fill="#6f431c">五行生克图</text>',
    ]
    for start, end in generates:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#4f8a5b" stroke-width="2.5" marker-end="url(#arrow-green)"/>'
        )
    for start, end in controls:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#c55a3d" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#arrow-red)"/>'
        )
    for element, (cx, cy) in nodes.items():
        fill, stroke, text_color = palette[element]
        parts.extend(
            [
                f'<circle cx="{cx}" cy="{cy}" r="28" fill="{fill}" stroke="{stroke}" stroke-width="2"/>',
                f'<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-size="22" fill="{text_color}">{element}</text>',
            ]
        )
    parts.extend(
        [
            render_chip(x + 22, y + 238, 118, "绿色实线 = 相生", fill="#e7f4ea", stroke="#b8d9c0", color="#2d6b3f", size=16),
            render_chip(x + 154, y + 238, 128, "红色虚线 = 相克", fill="#f9e7e3", stroke="#e6b8ae", color="#8b3c2d", size=16),
        ]
    )
    return "".join(parts)


def render_hexagram_svg(path, title, lines, moving_line=None, subtitle=None):
    y_positions = [210, 175, 140, 105, 70, 35]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="260" viewBox="0 0 240 260">',
        '<rect width="240" height="260" rx="18" fill="#fcfbf7" stroke="#d6c7a3"/>',
        f'<text x="120" y="24" text-anchor="middle" font-size="18" fill="#7c4a1d">{title}</text>',
    ]
    if subtitle:
        parts.append(
            f'<text x="120" y="244" text-anchor="middle" font-size="12" fill="#6b7280">{subtitle}</text>'
        )
    for idx, line in enumerate(lines, start=1):
        highlight = moving_line == idx
        parts.append(render_line(y_positions[idx - 1], line == 1, highlight=highlight))
    parts.append("</svg>")
    path.write_text("".join(parts), encoding="utf-8")


def render_step_report_svg(path, payload):
    question = svg_text(payload["question"])
    first, second = payload["digits"]
    upper_number = payload["upper_number"]
    lower_number = payload["lower_number"]
    moving_line = payload["moving_line"]
    body = payload["body"]
    use = payload["use"]
    primary = payload["primary"]
    changed = payload["changed"]

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1520" viewBox="0 0 1200 1520">',
        '<defs>',
        '<linearGradient id="bg-wash" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fbf6ec"/><stop offset="100%" stop-color="#efe4d1"/></linearGradient>',
        '<linearGradient id="hero-band" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#8a5a2b"/><stop offset="100%" stop-color="#c48a52"/></linearGradient>',
        '<marker id="arrow-brown" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#8a5a2b"/></marker>',
        '<marker id="arrow-green" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#4f8a5b"/></marker>',
        '<marker id="arrow-red" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#c55a3d"/></marker>',
        '</defs>',
        '<rect width="1200" height="1520" fill="url(#bg-wash)"/>',
        '<circle cx="1030" cy="118" r="140" fill="#f1e1c9" opacity="0.55"/>',
        '<circle cx="140" cy="1420" r="180" fill="#ead7bb" opacity="0.45"/>',
        '<rect x="40" y="34" width="1120" height="84" rx="28" fill="url(#hero-band)"/>',
        '<text x="72" y="84" font-size="36" fill="#fff8ef">梅花易数四步推演图</text>',
        '<text x="72" y="106" font-size="15" fill="#f7e9d8">每次占一次，就完整复习一次：问题、计算、变卦、解析。</text>',
        render_chip(910, 56, 216, "演示样例：明天会不会下雨？", fill="#f4ead8", stroke="#e8d3b1", color="#6f431c", size=15),
        render_panel(40, 140, 1120, 220, "明确问题，给数字", "1"),
        render_panel(40, 390, 1120, 400, "做计算，算本卦", "2"),
        render_panel(40, 820, 1120, 310, "做计算，算变卦", "3"),
        render_panel(40, 1160, 1120, 320, "做解析", "4"),
        f'<text x="80" y="202" font-size="18" fill="#4b5563">问题越具体，后面的判断越稳定；当前插件默认使用两位数字起卦。</text>',
        render_chip(80, 228, 430, f"问题：{payload['question']}", fill="#fff8ef", stroke="#e8d5b7", color="#111827", size=22),
        render_chip(80, 276, 172, f"数字：{first} / {second}", fill="#f4ead8", stroke="#dcc39d", color="#7c4a1d", size=22),
        render_chip(560, 228, 230, f"第一位 = {first}", size=20),
        render_chip(560, 272, 230, f"第二位 = {second}", size=20),
        render_chip(816, 228, 290, "上卦 = 第一位 ÷ 8 取余", fill="#f8f4ec"),
        render_chip(816, 272, 290, "下卦 = 第二位 ÷ 8 取余", fill="#f8f4ec"),
        '<text x="80" y="452" font-size="18" fill="#4b5563">本卦 = 上卦 + 下卦。余数是 0 时，按 8 处理。</text>',
        render_chip(80, 474, 340, f"上卦：{first} ÷ 8，余 {upper_number} -> {primary['upper']['name']}", fill="#fff8ef", stroke="#e8d5b7", size=18),
        render_chip(80, 520, 340, f"下卦：{second} ÷ 8，余 {lower_number} -> {primary['lower']['name']}", fill="#fff8ef", stroke="#e8d5b7", size=18),
        render_chip(80, 566, 340, f"组合成本卦：{primary['name']}", fill="#f4ead8", stroke="#dcc39d", color="#7c4a1d", size=20),
        render_hexagram_group(92, 618, primary["upper"]["lines"], f"上卦 {primary['upper']['name']}", subtitle=f"{primary['upper']['element']} / 数字 {upper_number}"),
        '<line x1="292" y1="704" x2="340" y2="704" stroke="#c48a52" stroke-width="2.5" marker-end="url(#arrow-brown)"/>',
        render_hexagram_group(350, 618, primary["lower"]["lines"], f"下卦 {primary['lower']['name']}", subtitle=f"{primary['lower']['element']} / 数字 {lower_number}"),
        '<line x1="550" y1="704" x2="600" y2="704" stroke="#c48a52" stroke-width="2.5" marker-end="url(#arrow-brown)"/>',
        render_hexagram_group(620, 588, primary["lines"], f"本卦 {primary['name']}", subtitle="上卦在上，下卦在下"),
        '<rect x="880" y="456" width="238" height="286" rx="22" fill="#f8f4ec" stroke="#e3d5ba"/>',
        '<text x="906" y="490" font-size="20" fill="#6f431c">先天八卦与五行</text>',
        '<text x="906" y="528" font-size="16" fill="#4b5563">1 乾 = 金   2 兑 = 金</text>',
        '<text x="906" y="558" font-size="16" fill="#4b5563">3 离 = 火   4 震 = 木</text>',
        '<text x="906" y="588" font-size="16" fill="#4b5563">5 巽 = 木   6 坎 = 水</text>',
        '<text x="906" y="618" font-size="16" fill="#4b5563">7 艮 = 土   8 坤 = 土</text>',
        '<line x1="906" y1="638" x2="1092" y2="638" stroke="#ddc9a8"/>',
        '<text x="906" y="674" font-size="17" fill="#4b5563">本例对应：</text>',
        f'<text x="906" y="706" font-size="17" fill="#4b5563">{first} -> {primary["upper"]["name"]} -> {primary["upper"]["element"]}</text>',
        f'<text x="906" y="736" font-size="17" fill="#4b5563">{second} -> {primary["lower"]["name"]} -> {primary["lower"]["element"]}</text>',
        '<text x="80" y="882" font-size="18" fill="#4b5563">变卦 = 两数相加 ÷ 6 取余。余数是 0 时，按 6 处理。</text>',
        render_chip(80, 904, 286, f"动爻：{first} + {second} = {first + second}", fill="#fff8ef", stroke="#e8d5b7", size=18),
        render_chip(80, 950, 286, f"{first + second} ÷ 6，余 {moving_line}", fill="#fff8ef", stroke="#e8d5b7", size=18),
        render_chip(80, 996, 286, f"所以动第 {moving_line} 爻", fill="#f4ead8", stroke="#dcc39d", color="#7c4a1d", size=20),
        render_hexagram_group(360, 896, primary["lines"], f"本卦 {primary['name']}", moving_line=moving_line, subtitle=f"高亮的是第 {moving_line} 爻"),
        '<line x1="590" y1="990" x2="640" y2="990" stroke="#c48a52" stroke-width="2.5" marker-end="url(#arrow-brown)"/>',
        render_hexagram_group(662, 896, changed["lines"], f"变卦 {changed['name']}", subtitle="动爻阴阳互变之后"),
        '<rect x="930" y="894" width="180" height="168" rx="22" fill="#f8f4ec" stroke="#e3d5ba"/>',
        '<text x="956" y="928" font-size="20" fill="#6f431c">变化说明</text>',
        f'<text x="956" y="968" font-size="18" fill="#4b5563">本卦：{primary["name"]}</text>',
        f'<text x="956" y="1002" font-size="18" fill="#4b5563">第 {moving_line} 爻发生变化</text>',
        f'<text x="956" y="1036" font-size="18" fill="#4b5563">得到：{changed["name"]}</text>',
        '<text x="80" y="1222" font-size="18" fill="#4b5563">解析时同时看三件事：八卦数字对应、八卦五行对应、体用之间的生克关系。</text>',
        '<rect x="80" y="1254" width="320" height="190" rx="22" fill="#f8f4ec" stroke="#e3d5ba"/>',
        '<text x="106" y="1288" font-size="20" fill="#6f431c">八卦与五行对应</text>',
        '<text x="106" y="1324" font-size="17" fill="#4b5563">乾=金  兑=金  离=火  震=木</text>',
        '<text x="106" y="1356" font-size="17" fill="#4b5563">巽=木  坎=水  艮=土  坤=土</text>',
        f'<text x="106" y="1400" font-size="18" fill="#4b5563">体：{body["name"]} -> {body["element"]}</text>',
        f'<text x="106" y="1432" font-size="18" fill="#4b5563">用：{use["name"]} -> {use["element"]}</text>',
        render_five_element_chart(430, 1238),
        render_relation_diagram(792, 1238, body["name"], body["element"], use["name"], use["element"], payload["relation"], payload["verdict"]),
        '</svg>',
    ]
    path.write_text("".join(parts), encoding="utf-8")


def render_overview_svg(path, payload):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420">',
        '<rect width="960" height="420" fill="#f8f5ef"/>',
        '<text x="40" y="44" font-size="28" fill="#7c4a1d">梅花易数推演过程</text>',
        f'<text x="40" y="80" font-size="16" fill="#374151">问题：{payload["question"]}</text>',
        f'<text x="40" y="106" font-size="16" fill="#374151">数字：{payload["digits"][0]} / {payload["digits"][1]}</text>',
        f'<text x="40" y="132" font-size="16" fill="#374151">本卦：{payload["primary"]["name"]}</text>',
        f'<text x="40" y="158" font-size="16" fill="#374151">变卦：{payload["changed"]["name"]}</text>',
        f'<text x="40" y="184" font-size="16" fill="#374151">动爻：第 {payload["moving_line"]} 爻</text>',
        f'<text x="40" y="210" font-size="16" fill="#374151">体：{payload["body"]["name"]}（{payload["body"]["element"]}）</text>',
        f'<text x="40" y="236" font-size="16" fill="#374151">用：{payload["use"]["name"]}（{payload["use"]["element"]}）</text>',
        f'<text x="40" y="262" font-size="16" fill="#374151">关系：{payload["relation"]}</text>',
        f'<text x="40" y="288" font-size="16" fill="#374151">判断：{payload["verdict"]}</text>',
        '<rect x="360" y="40" width="220" height="300" rx="18" fill="#fffdf8" stroke="#d6c7a3"/>',
        '<rect x="620" y="40" width="220" height="300" rx="18" fill="#fffdf8" stroke="#d6c7a3"/>',
        '<text x="470" y="72" text-anchor="middle" font-size="22" fill="#7c4a1d">本卦</text>',
        '<text x="730" y="72" text-anchor="middle" font-size="22" fill="#7c4a1d">变卦</text>',
    ]
    y_positions = [290, 250, 210, 170, 130, 90]
    for idx, line in enumerate(payload["primary"]["lines"], start=1):
        parts.append(
            render_line(
                y_positions[idx - 1],
                line == 1,
                highlight=payload["moving_line"] == idx,
                x=390,
            )
        )
    for idx, line in enumerate(payload["changed"]["lines"], start=1):
        parts.append(render_line(y_positions[idx - 1], line == 1, x=650))
    parts.append("</svg>")
    path.write_text("".join(parts), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Meihua Yishu calculator and SVG renderer.")
    parser.add_argument("--question", required=True, help="Question to divine.")
    parser.add_argument("--digits", nargs=2, help="Two digits, e.g. 7 8")
    parser.add_argument("--packed", help="Packed two-digit number, e.g. 78")
    parser.add_argument("--out-dir", required=True, help="Output directory")
    args = parser.parse_args()

    first, second = parse_digits(args.digits, args.packed)
    upper_number = mod_pick(first, 8)
    lower_number = mod_pick(second, 8)
    moving_line = mod_pick(first + second, 6)

    upper = TRIGRAMS[upper_number]
    lower = TRIGRAMS[lower_number]
    primary_lines = lines_to_hexagram(upper["lines"], lower["lines"])
    changed_lines = flip_line(primary_lines, moving_line)
    line_change = moving_line_change(primary_lines, moving_line)
    changed_lower_number, changed_lower = find_trigram_by_lines(changed_lines[:3])
    changed_upper_number, changed_upper = find_trigram_by_lines(changed_lines[3:])

    # 不变为体，变化为用：1-3 爻动看下卦，4-6 爻动看上卦。
    if moving_line <= 3:
        body = upper
        use = lower
    else:
        body = lower
        use = upper
    relation = relation_of(body["element"], use["element"])
    verdict = verdict_for_relation(relation)

    primary_name = HEXAGRAM_NAMES[(upper["name"], lower["name"])]
    changed_name = HEXAGRAM_NAMES[(changed_upper["name"], changed_lower["name"])]

    payload = {
        "question": args.question,
        "digits": [first, second],
        "upper_number": upper_number,
        "lower_number": lower_number,
        "moving_line": moving_line,
        "moving_line_change": line_change,
        "body": body,
        "use": use,
        "relation": relation,
        "verdict": verdict,
        "primary": {
            "name": primary_name,
            "upper": {
                "number": upper_number,
                **upper,
                "visual_top_to_bottom": trigram_visual_signature(upper["lines"]),
            },
            "lower": {
                "number": lower_number,
                **lower,
                "visual_top_to_bottom": trigram_visual_signature(lower["lines"]),
            },
            "lines": primary_lines,
            "composition_rule": "本卦上半必须等于上卦图形，本卦下半必须等于下卦图形",
            "assembly_lock": {
                "upper_source": f"上卦 {upper['name']}",
                "upper_visual_top_to_bottom": trigram_visual_signature(upper["lines"]),
                "lower_source": f"下卦 {lower['name']}",
                "lower_visual_top_to_bottom": trigram_visual_signature(lower["lines"]),
                "instruction": "画本卦时，不允许重画、不允许改线，必须把上卦原样放到上半，把下卦原样放到下半。",
            },
        },
        "changed": {
            "name": changed_name,
            "upper": {
                "number": changed_upper_number,
                **changed_upper,
                "visual_top_to_bottom": trigram_visual_signature(changed_upper["lines"]),
            },
            "lower": {
                "number": changed_lower_number,
                **changed_lower,
                "visual_top_to_bottom": trigram_visual_signature(changed_lower["lines"]),
            },
            "lines": changed_lines,
        },
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    render_hexagram_svg(
        out_dir / "upper_trigram.svg",
        f"上卦 {upper['name']}",
        upper["lines"],
        subtitle=f"{upper['element']} / 数字 {upper_number}",
    )
    render_hexagram_svg(
        out_dir / "lower_trigram.svg",
        f"下卦 {lower['name']}",
        lower["lines"],
        subtitle=f"{lower['element']} / 数字 {lower_number}",
    )
    render_hexagram_svg(
        out_dir / "primary_hexagram.svg",
        f"本卦 {primary_name}",
        primary_lines,
        moving_line=moving_line,
        subtitle=f"动爻：第 {moving_line} 爻",
    )
    render_hexagram_svg(
        out_dir / "changed_hexagram.svg",
        f"变卦 {changed_name}",
        changed_lines,
        subtitle=f"体用：{relation}",
    )
    render_overview_svg(out_dir / "process_overview.svg", payload)
    render_step_report_svg(out_dir / "step_by_step_report.svg", payload)


if __name__ == "__main__":
    main()
