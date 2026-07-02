#!/usr/bin/env python3
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = {"svg": "http://www.w3.org/2000/svg"}
BLACK = "#111111"
HIGHLIGHT = "#b45309"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_svg_rect_lines(path: Path):
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    rects = root.findall(".//svg:rect", SVG_NS)
    line_rects = []
    for rect in rects:
        fill = rect.attrib.get("fill")
        width = rect.attrib.get("width")
        height = rect.attrib.get("height")
        y = rect.attrib.get("y")
        if fill not in {BLACK, HIGHLIGHT}:
            continue
        if width not in {"160", "68"} or height != "14" or y is None:
            continue
        line_rects.append(
            {
                "y": int(float(y)),
                "width": int(width),
                "fill": fill,
            }
        )
    grouped = {}
    for item in line_rects:
        grouped.setdefault(item["y"], []).append(item)
    ordered = []
    for y in sorted(grouped.keys()):
        members = grouped[y]
        widths = sorted(member["width"] for member in members)
        fills = {member["fill"] for member in members}
        if widths == [160]:
            line_type = "阳"
        elif widths == [68, 68]:
            line_type = "阴"
        else:
            line_type = "异常"
        ordered.append(
            {
                "y": y,
                "line_type": line_type,
                "rect_count": len(members),
                "highlight": HIGHLIGHT in fills,
            }
        )
    return ordered


def line_words_from_bottom(lines):
    return ["阳" if value == 1 else "阴" for value in lines]


def line_words_from_top(lines):
    return list(reversed(line_words_from_bottom(lines)))


def expect_moving_line(payload):
    change = payload["moving_line_change"]
    return {
        "index_from_bottom": change["index_from_bottom"],
        "index_from_top": change["index_from_top"],
        "original_word": change["original_word"],
        "changed_word": change["changed_word"],
    }


def collect_issues(payload, upper_lines, lower_lines, primary_lines, changed_lines):
    issues = []
    expected_upper = payload["primary"]["upper"]["visual_top_to_bottom"].split(" / ")
    expected_lower = payload["primary"]["lower"]["visual_top_to_bottom"].split(" / ")
    expected_primary = line_words_from_top(payload["primary"]["lines"])
    expected_changed = line_words_from_top(payload["changed"]["lines"])
    moving = expect_moving_line(payload)

    if len(upper_lines) != 3:
        issues.append(f"上卦图应有3条爻线，当前检测到 {len(upper_lines)} 条。")
    if len(lower_lines) != 3:
        issues.append(f"下卦图应有3条爻线，当前检测到 {len(lower_lines)} 条。")
    if len(primary_lines) != 6:
        issues.append(f"本卦图应有6条爻线，当前检测到 {len(primary_lines)} 条。")
    if len(changed_lines) != 6:
        issues.append(f"变卦图应有6条爻线，当前检测到 {len(changed_lines)} 条。")

    actual_upper = [item["line_type"] for item in upper_lines]
    actual_lower = [item["line_type"] for item in lower_lines]
    actual_primary = [item["line_type"] for item in primary_lines]
    actual_changed = [item["line_type"] for item in changed_lines]

    if actual_upper != expected_upper:
        issues.append(f"上卦图形不对，应为 {' / '.join(expected_upper)}，实际为 {' / '.join(actual_upper) or '空'}。")
    if actual_lower != expected_lower:
        issues.append(f"下卦图形不对，应为 {' / '.join(expected_lower)}，实际为 {' / '.join(actual_lower) or '空'}。")
    if actual_primary != expected_primary:
        issues.append(f"本卦图形不对，应为 {' / '.join(expected_primary)}，实际为 {' / '.join(actual_primary) or '空'}。")
    if actual_changed != expected_changed:
        issues.append(f"变卦图形不对，应为 {' / '.join(expected_changed)}，实际为 {' / '.join(actual_changed) or '空'}。")

    primary_upper = actual_primary[:3]
    primary_lower = actual_primary[3:]
    if primary_upper != expected_upper:
        issues.append("本卦上半没有原样复用上卦图形。")
    if primary_lower != expected_lower:
        issues.append("本卦下半没有原样复用下卦图形。")

    highlighted = [idx + 1 for idx, item in enumerate(primary_lines) if item["highlight"]]
    if len(highlighted) != 1:
        issues.append(f"本卦动爻高亮数量应为1，当前检测到 {len(highlighted)} 处。")
    else:
        actual_index_from_top = highlighted[0]
        if actual_index_from_top != moving["index_from_top"]:
            issues.append(
                f"动爻高亮位置不对。应为自下而上第{moving['index_from_bottom']}爻，也就是自上而下第{moving['index_from_top']}条；当前高亮的是自上而下第{actual_index_from_top}条。"
            )
        actual_original = actual_primary[actual_index_from_top - 1]
        actual_changed_word = actual_changed[actual_index_from_top - 1] if len(actual_changed) == 6 else "未知"
        if actual_original != moving["original_word"]:
            issues.append(
                f"动爻变化前阴阳不对。第{moving['index_from_bottom']}爻原本应为{moving['original_word']}，当前检测为{actual_original}。"
            )
        if actual_changed_word != moving["changed_word"]:
            issues.append(
                f"动爻变化后阴阳不对。第{moving['index_from_bottom']}爻变化后应为{moving['changed_word']}，当前检测为{actual_changed_word}。"
            )

    return issues


def build_report(payload, issues, upper_lines, lower_lines, primary_lines, changed_lines):
    return {
        "check_result": "通过" if not issues else "不通过",
        "question": payload["question"],
        "digits": payload["digits"],
        "expected": {
            "upper_top_to_bottom": payload["primary"]["upper"]["visual_top_to_bottom"],
            "lower_top_to_bottom": payload["primary"]["lower"]["visual_top_to_bottom"],
            "primary_top_to_bottom": " / ".join(line_words_from_top(payload["primary"]["lines"])),
            "changed_top_to_bottom": " / ".join(line_words_from_top(payload["changed"]["lines"])),
            "moving_line": payload["moving_line"],
            "moving_line_from_top": payload["moving_line_change"]["index_from_top"],
            "moving_line_change": payload["moving_line_change"]["instruction"],
            "primary_name": payload["primary"]["name"],
            "changed_name": payload["changed"]["name"],
        },
        "detected": {
            "upper_top_to_bottom": " / ".join(item["line_type"] for item in upper_lines),
            "lower_top_to_bottom": " / ".join(item["line_type"] for item in lower_lines),
            "primary_top_to_bottom": " / ".join(item["line_type"] for item in primary_lines),
            "changed_top_to_bottom": " / ".join(item["line_type"] for item in changed_lines),
            "primary_highlight_from_top": [idx + 1 for idx, item in enumerate(primary_lines) if item["highlight"]],
        },
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Check Meihua Yishu deterministic diagram artifacts.")
    parser.add_argument("--out-dir", required=True, help="Directory containing result.json and SVG artifacts.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    payload = load_json(out_dir / "result.json")
    upper_lines = parse_svg_rect_lines(out_dir / "upper_trigram.svg")
    lower_lines = parse_svg_rect_lines(out_dir / "lower_trigram.svg")
    primary_lines = parse_svg_rect_lines(out_dir / "primary_hexagram.svg")
    changed_lines = parse_svg_rect_lines(out_dir / "changed_hexagram.svg")
    issues = collect_issues(payload, upper_lines, lower_lines, primary_lines, changed_lines)
    report = build_report(payload, issues, upper_lines, lower_lines, primary_lines, changed_lines)
    report_path = out_dir / "qa_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
