#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pick_font():
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def make_font(font_path, size):
    return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()


def draw_round_box(draw, box, fill, outline, radius=24, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_yao(draw, x, y, kind, fill, width=190, height=18):
    if kind == "阳":
        draw.rounded_rectangle([x, y, x + width, y + height], radius=5, fill=fill)
        return
    seg = 78
    gap = width - seg * 2
    draw.rounded_rectangle([x, y, x + seg, y + height], radius=5, fill=fill)
    draw.rounded_rectangle([x + seg + gap, y, x + width, y + height], radius=5, fill=fill)


def draw_trigram(draw, x, y, words, line_fill, font_main, font_small, label=None, element=None, number=None):
    gap = 26
    for idx, word in enumerate(words):
        draw_yao(draw, x, y + idx * (18 + gap), word, line_fill)
    if label:
        draw.text((x, y + 3 * (18 + gap) + 4), label, font=font_main, fill=(35, 31, 28))
    if element:
        draw.text((x, y + 3 * (18 + gap) + 44), element, font=font_small, fill=(35, 31, 28))
    if number is not None:
        draw.rounded_rectangle([x - 76, y + 34, x - 18, y + 90], radius=12, outline=(190, 158, 112), width=3, fill=(252, 248, 238))
        draw.text((x - 56, y + 42), str(number), font=make_font(pick_font(), 36), fill=(116, 72, 32))


def draw_hexagram(draw, x, y, words, line_fill, font_main, label=None, highlight_top_index=None, highlight_fill=(196, 77, 55)):
    gap = 22
    for idx, word in enumerate(words, start=1):
        fill = highlight_fill if highlight_top_index == idx else line_fill
        draw_yao(draw, x, y + (idx - 1) * (18 + gap), word, fill)
    if label:
        draw.text((x, y + 6 * (18 + gap) + 8), label, font=font_main, fill=(35, 31, 28))


def render_card(out_dir: Path):
    result = load_json(out_dir / "result.json")
    qa = load_json(out_dir / "qa_report.json")

    width, height = 1600, 2400
    img = Image.new("RGB", (width, height), (247, 241, 231))
    draw = ImageDraw.Draw(img)

    font_path = pick_font()
    f_title = make_font(font_path, 72)
    f_sub = make_font(font_path, 32)
    f_h = make_font(font_path, 42)
    f_m = make_font(font_path, 30)
    f_s = make_font(font_path, 24)
    f_xs = make_font(font_path, 20)
    f_big = make_font(font_path, 54)
    f_result = make_font(font_path, 56)

    brown = (116, 72, 32)
    dark = (35, 31, 28)
    line_black = (10, 10, 10)
    highlight = (196, 77, 55)
    blue = (74, 112, 164)
    green = (71, 126, 78)
    red = (175, 77, 62)

    margin = 40
    draw_round_box(draw, [18, 18, width - 18, height - 18], (249, 244, 236), (163, 128, 83), radius=28, width=4)
    draw.text((width // 2 - 360, 48), "梅花易数四步推演图", font=f_title, fill=brown)
    draw.text((width // 2 - 285, 136), f"案例：{result['question']}  数字 {result['digits'][0]}{result['digits'][1]}", font=f_sub, fill=dark)

    def section(y, num, title, section_height):
        draw_round_box(draw, [margin, y, width - margin, y + section_height], (255, 251, 245), (209, 184, 146))
        draw.rounded_rectangle([margin + 16, y + 16, margin + 600, y + 74], radius=18, fill=(151, 111, 66))
        draw.text((margin + 40, y + 23), f"第 {num} 步：{title}", font=f_h, fill=(255, 248, 238))

    section(210, 1, "明确问题，给数字", 230)
    section(470, 2, "做计算，算本卦", 700)
    section(1200, 3, "做计算，算变卦", 470)
    section(1700, 4, "做解析", 560)

    draw.text((90, 320), f"问题：{result['question']}", font=make_font(font_path, 40), fill=dark)
    draw.text((90, 380), f"数字：{result['digits'][0]}{result['digits'][1]}", font=f_big, fill=(170, 62, 36))
    draw.text((90, 440), "先专注问题，再取两位数起卦。", font=f_s, fill=(80, 73, 66))

    upper = result["primary"]["upper"]["visual_top_to_bottom"].split(" / ")
    lower = result["primary"]["lower"]["visual_top_to_bottom"].split(" / ")
    primary = qa["expected"]["primary_top_to_bottom"].split(" / ")
    changed = qa["expected"]["changed_top_to_bottom"].split(" / ")

    s2y = 470
    draw.text((90, s2y + 110), f"上卦：{result['digits'][0]} ÷ 8，余 {result['upper_number']}，为{result['primary']['upper']['name']}，为{result['primary']['upper']['element']}", font=f_m, fill=dark)
    draw.text((90, s2y + 360), f"下卦：{result['digits'][1]} ÷ 8，余 {result['lower_number']}，为{result['primary']['lower']['name']}，为{result['primary']['lower']['element']}", font=f_m, fill=dark)
    draw_trigram(draw, 270, s2y + 140, upper, line_black, f_m, f_s, label=result["primary"]["upper"]["name"], element=result["primary"]["upper"]["element"], number=result["digits"][0])
    draw_trigram(draw, 270, s2y + 390, lower, line_black, f_m, f_s, label=result["primary"]["lower"]["name"], element=result["primary"]["lower"]["element"], number=result["digits"][1])
    for arrow_y in [s2y + 250, s2y + 500]:
        draw.line([520, arrow_y, 620, arrow_y], fill=blue, width=5)
        draw.polygon([(620, arrow_y), (598, arrow_y - 12), (598, arrow_y + 12)], fill=blue)
    draw.text((700, s2y + 110), f"本卦：{result['primary']['name']}", font=f_m, fill=dark)
    draw_hexagram(draw, 760, s2y + 160, primary, line_black, f_m)
    draw.text((1060, s2y + 220), "上卦", font=f_s, fill=blue)
    draw.text((1060, s2y + 260), f"{result['primary']['upper']['name']}（{result['primary']['upper']['element']}）", font=f_s, fill=blue)
    draw.text((1060, s2y + 470), "下卦", font=f_s, fill=red)
    draw.text((1060, s2y + 510), f"{result['primary']['lower']['name']}（{result['primary']['lower']['element']}）", font=f_s, fill=red)
    draw.text((90, s2y + 620), f"本卦构成：本卦上半为上卦（{result['primary']['upper']['name']}），下半为下卦（{result['primary']['lower']['name']}）。", font=f_m, fill=dark)
    draw_round_box(draw, [1130, s2y + 90, 1540, s2y + 610], (250, 246, 239), (209, 184, 146))
    draw.text((1160, s2y + 120), "先天八卦数字与五行", font=f_m, fill=brown)
    rows = ["1 乾 = 金", "2 兑 = 金", "3 离 = 火", "4 震 = 木", "5 巽 = 木", "6 坎 = 水", "7 艮 = 土", "8 坤 = 土"]
    for idx, row in enumerate(rows):
        draw.text((1170, s2y + 180 + idx * 44), row, font=f_s, fill=dark)
    draw.text((1160, s2y + 550), f"本例：{result['digits'][0]} → {result['primary']['upper']['name']} → {result['primary']['upper']['element']}，{result['digits'][1]} → {result['primary']['lower']['name']} → {result['primary']['lower']['element']}", font=f_xs, fill=dark)

    s3y = 1200
    draw.text((90, s3y + 110), f"1. {result['digits'][0]} + {result['digits'][1]} = {sum(result['digits'])}", font=make_font(font_path, 40), fill=dark)
    draw.text((90, s3y + 180), f"2. {sum(result['digits'])} ÷ 6，余 {result['moving_line']}", font=make_font(font_path, 40), fill=dark)
    draw.text((90, s3y + 250), f"3. 第{result['moving_line']}爻动", font=make_font(font_path, 40), fill=dark)
    draw.text((90, s3y + 320), f"说明：自下而上第{result['moving_line']}爻 = 自上而下第{qa['expected']['moving_line_from_top']}条", font=f_m, fill=(120, 52, 38))
    draw.text((430, s3y + 100), f"本卦：{result['primary']['name']}", font=f_m, fill=dark)
    draw_hexagram(draw, 470, s3y + 150, primary, line_black, f_m, highlight_top_index=qa["expected"]["moving_line_from_top"])
    highlight_y = s3y + 150 + (qa["expected"]["moving_line_from_top"] - 1) * (18 + 22)
    draw.rounded_rectangle([455, highlight_y - 8, 676, highlight_y + 26], radius=8, outline=highlight, width=4)
    draw.ellipse([690, highlight_y - 2, 730, highlight_y + 38], outline=highlight, width=4)
    draw.text((700, highlight_y + 2), str(result["moving_line"]), font=f_xs, fill=highlight)
    draw.line([790, s3y + 260, 900, s3y + 260], fill=dark, width=6)
    draw.polygon([(900, s3y + 260), (874, s3y + 246), (874, s3y + 274)], fill=dark)
    draw.text((970, s3y + 100), f"变卦：{result['changed']['name']}", font=f_m, fill=dark)
    draw_hexagram(draw, 1010, s3y + 150, changed, line_black, f_m)
    draw.text((910, s3y + 440), qa["expected"]["moving_line_change"] + f" 得到变卦：{result['changed']['name']}。", font=f_s, fill=dark)

    s4y = 1700
    draw_round_box(draw, [70, s4y + 100, 360, s4y + 430], (252, 248, 241), (209, 184, 146))
    draw.text((100, s4y + 130), "八卦与五行对应", font=f_m, fill=brown)
    mappings = ["乾：金    兑：金", "离：火    震：木", "巽：木    坎：水", "艮：土    坤：土"]
    for idx, row in enumerate(mappings):
        draw.text((100, s4y + 200 + idx * 60), row, font=f_s, fill=dark)

    center_x, center_y, radius = 740, s4y + 260, 150
    points = {
        "金": (center_x, center_y - radius),
        "水": (center_x + 142, center_y - 44),
        "木": (center_x + 88, center_y + 120),
        "火": (center_x - 88, center_y + 120),
        "土": (center_x - 142, center_y - 44),
    }
    palette = {"金": (226, 193, 98), "水": (78, 114, 157), "木": (90, 142, 90), "火": (188, 84, 56), "土": (150, 111, 69)}
    draw.text((610, s4y + 110), "五行生克图", font=f_m, fill=brown)
    generate_pairs = [("金", "水"), ("水", "木"), ("木", "火"), ("火", "土"), ("土", "金")]
    control_pairs = [("金", "木"), ("木", "土"), ("土", "水"), ("水", "火"), ("火", "金")]
    for start, end in generate_pairs:
        draw.line([points[start], points[end]], fill=green, width=4)
    for start, end in control_pairs:
        draw.line([points[start], points[end]], fill=red, width=3)
    for key, (x, y) in points.items():
        draw.ellipse([x - 34, y - 34, x + 34, y + 34], fill=palette[key], outline=(255, 255, 255), width=2)
        box = draw.textbbox((0, 0), key, font=make_font(font_path, 34))
        draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2 - 4), key, font=make_font(font_path, 34), fill=(255, 250, 244))
    draw.text((580, s4y + 470), "绿色实线 = 相生    红色线 = 相克", font=f_xs, fill=dark)

    draw_round_box(draw, [1140, s4y + 100, 1520, s4y + 430], (252, 248, 241), (209, 184, 146))
    draw.text((1210, s4y + 130), "体用关系", font=f_m, fill=brown)
    draw.rounded_rectangle([1180, s4y + 200, 1480, s4y + 260], radius=14, fill=(246, 228, 220))
    draw.rounded_rectangle([1180, s4y + 290, 1480, s4y + 350], radius=14, fill=(246, 236, 220))
    draw.text((1240, s4y + 214), f"体 = {result['body']['name']}（{result['body']['element']}）", font=f_m, fill=dark)
    draw.text((1240, s4y + 304), f"用 = {result['use']['name']}（{result['use']['element']}）", font=f_m, fill=dark)
    draw.text((1235, s4y + 390), f"关系：{result['relation']}", font=make_font(font_path, 40), fill=(140, 58, 43))

    draw_round_box(draw, [60, s4y + 470, 1540, s4y + 540], (251, 246, 238), (209, 184, 146))
    draw.text((110, s4y + 488), "结论：偏不下雨", font=f_result, fill=(145, 48, 33))
    draw.text((700, s4y + 500), "体为火，用为土，火生土，为体生用之象，故偏不下雨。", font=f_s, fill=dark)

    out_path = out_dir / "deterministic_teaching_card.png"
    img.save(out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Render deterministic Meihua teaching card PNG.")
    parser.add_argument("--out-dir", required=True, help="Directory containing result.json and qa_report.json")
    args = parser.parse_args()
    out_path = render_card(Path(args.out_dir))
    print(out_path)


if __name__ == "__main__":
    main()
