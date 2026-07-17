#!/usr/bin/env python3
"""Validate a WeChat Channels title-package JSON file."""

import argparse
import json
import re
import sys
from pathlib import Path


EMOJI = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF"
    "️✨❤"
    "]"
)
FORBIDDEN = (
    "不转不是中国人",
    "必须转发",
    "赶紧点赞",
    "求关注",
    "保证赚钱",
    "轻松躺赚",
    "彻底改变你的人生",
    "所有人都",
)
CLAIM_STRENGTHS = {
    "可核验事实",
    "有边界的个人判断",
    "变化主张",
    "普遍因果",
}


def compact_length(text):
    return len(re.sub(r"\s", "", str(text)))


def normalized(text):
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]", "", str(text)).lower()


def load_json(path):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", help="JSON file path, or - for stdin")
    parser.add_argument("--source", help="Optional source text for exact quote checks")
    args = parser.parse_args()

    data = load_json(args.json_path)
    source = Path(args.source).read_text(encoding="utf-8") if args.source else None
    errors = []
    warnings = []

    if data.get("platform") != "video":
        errors.append("platform 必须是 video")
    if not str(data.get("intended_recipient", "")).strip():
        errors.append("缺少 intended_recipient")

    evidence = data.get("evidence", [])
    evidence_ids = {item.get("id") for item in evidence if item.get("id")}
    if not evidence_ids:
        errors.append("至少需要一条带 id 的 evidence")

    if source:
        source_norm = normalized(source)
        for item in evidence:
            if item.get("type") == "原话" and normalized(item.get("text", "")) not in source_norm:
                errors.append(f"原话 {item.get('id', '?')} 无法在 source 中找到")

    options = data.get("options", [])
    if len(options) < 3:
        errors.append("options 至少需要 3 套")

    option_ids = set()
    angles = []
    for index, option in enumerate(options, 1):
        prefix = f"方案{index}"
        option_id = option.get("id")
        if not option_id:
            errors.append(f"{prefix} 缺少 id")
        elif option_id in option_ids:
            errors.append(f"{prefix} id 重复：{option_id}")
        option_ids.add(option_id)

        angle = str(option.get("angle", "")).strip()
        if not angle:
            errors.append(f"{prefix} 缺少 angle")
        angles.append(angle)

        title = str(option.get("title", "")).strip()
        title_length = compact_length(title)
        if not title:
            errors.append(f"{prefix} 缺少 title")
        if title_length > 30:
            errors.append(f"{prefix} 标题 {title_length} 字 > 30：{title}")
        if option.get("title_chars") is not None and option.get("title_chars") != title_length:
            errors.append(f"{prefix} title_chars 应为 {title_length}")
        if EMOJI.search(title):
            errors.append(f"{prefix} 标题含 emoji：{title}")
        for phrase in FORBIDDEN:
            if phrase in title:
                errors.append(f"{prefix} 标题含禁用表达：{phrase}")

        cover = option.get("cover", [])
        if not isinstance(cover, list) or not 1 <= len(cover) <= 3:
            errors.append(f"{prefix} cover 必须是 1–3 行列表")
            cover = cover if isinstance(cover, list) else []
        for line_index, line in enumerate(cover, 1):
            length = compact_length(line)
            if length > 10:
                errors.append(f"{prefix} 封面第{line_index}行 {length} 字 > 10：{line}")
            if EMOJI.search(str(line)):
                errors.append(f"{prefix} 封面第{line_index}行含 emoji：{line}")

        three_seconds = str(option.get("three_second_line", "")).strip()
        if not three_seconds:
            errors.append(f"{prefix} 缺少 three_second_line")
        if compact_length(three_seconds) > 45:
            warnings.append(f"{prefix} three_second_line 可能过长，不利于口播")

        if not str(option.get("relationship_target", "")).strip():
            errors.append(f"{prefix} 缺少 relationship_target")
        if not str(option.get("discussion_question", "")).strip():
            errors.append(f"{prefix} 缺少 discussion_question")

        claim_strength = option.get("claim_strength")
        if claim_strength not in CLAIM_STRENGTHS:
            errors.append(f"{prefix} claim_strength 不在允许值中")
        if claim_strength == "普遍因果":
            warnings.append(f"{prefix} 使用普遍因果，必须人工核验广泛证据")

        source_ids = option.get("source_ids", [])
        if not source_ids:
            errors.append(f"{prefix} 缺少 source_ids")
        unknown_ids = set(source_ids) - evidence_ids
        if unknown_ids:
            errors.append(f"{prefix} 引用了不存在的 evidence：{sorted(unknown_ids)}")

        score = option.get("score")
        if not isinstance(score, (int, float)) or not 0 <= score <= 100:
            errors.append(f"{prefix} score 必须是 0–100")

        title_norm = normalized(title)
        cover_norm = normalized("".join(str(line) for line in cover))
        if len(cover_norm) >= 4 and (cover_norm in title_norm or title_norm in cover_norm):
            warnings.append(f"{prefix} 封面与标题可能重复")

    nonempty_angles = [angle for angle in angles if angle]
    if len(set(nonempty_angles)) != len(nonempty_angles):
        warnings.append("存在重复 angle，请确认不是同一钩子换说法")

    recommended_id = data.get("recommended_id")
    if recommended_id not in option_ids:
        errors.append("recommended_id 必须指向现有方案")
    if not str(data.get("test_hypothesis", "")).strip():
        errors.append("缺少 test_hypothesis")

    if errors:
        print(f"FAIL: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        return 1

    print(f"PASS: {len(options)} video option(s)")
    for warning in warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
