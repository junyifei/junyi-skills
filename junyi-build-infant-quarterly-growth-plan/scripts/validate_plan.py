#!/usr/bin/env python3
"""Validate a public 0-35 month quarterly growth plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADING_GROUPS = (
    ("## 使用说明与边界",),
    ("## 家庭画像速览", "## 家庭与孩子近况速览"),
    ("## 五维度画像提炼",),
    ("## 本季度发展观察重点",),
    ("## 环境提供方案", "## 环境提供方案（代替行动清单）", "## 环境提供方案(代替行动清单)"),
    ("## 本计划观察指标", "## 里程碑观察指标", "## 观察与复盘"),
    ("## 家长话术",),
    ("## 避坑提醒", "## 个性化避坑提醒"),
    ("## 每月复盘三问",),
    ("## 下季度展望",),
)
BOUNDARY = "本计划不替代医疗、心理、发育筛查或教育专业评估"
TITLE = re.compile(r"(?m)^#\s+\S.+\s+\d{4}\s+Q[1-4]\s+婴幼儿(?:个性化发展计划|季度成长计划)\s*$")
EVIDENCE_REF = re.compile(r"\b[EQ]\d+\b")
OBSERVATION = re.compile(r"(?m)^###\s+(?:观察线\s*\d+|\d+[.、])(?:[：:]|\s).+")
ENVIRONMENT = re.compile(r"(?m)^###\s+环境(?:方案)?\s*(?:\d+|[一二三四五])(?:[：:]|\s).+")
RISKS = (
    re.compile(r"(?:诊断|确诊)为"),
    re.compile(r"(?<!不)(?<!不是)(?<!并非)(?:就是|属于|可判定为)(?:自闭症|孤独症|多动症|ADHD|抑郁症|焦虑症|发育迟缓|感统失调)", re.I),
    re.compile(r"(?:孩子|他|她).{0,8}(?:一定|必然|肯定|绝对).{0,8}(?:会|能|可以)?(?:学会|掌握|达到|成为|超过|追上)"),
    re.compile(r"(?:孩子|发育|发展|能力).{0,8}(?:很正常|完全正常|属于正常|发育正常|没有问题|一点(?:问题|毛病)都没有)"),
    re.compile(r"(?:孩子|他|她).{0,6}(?:就是|属于|是(?:一个)?).{0,4}(?:视觉型|听觉型|动觉型|右脑型|左脑型)(?:学习者|类型)?"),
    re.compile(r"(?:VARK|多元智能|左右脑).{0,12}(?:类型|定型|分数|学习者)"),
    re.compile(r"(?:达到|追上|赶上).{0,10}(?:同龄|月龄|里程碑)"),
    re.compile(r"/" r"Users/[^\s)]+"),
    re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"),
)
OVERCLAIM = re.compile(r"(?:说明|证明).{0,24}(?:能力|发育|人格|天赋|特质|类型)")
TRAINING = re.compile(r"(?<!不)(?<!避免)(?:安排|进行|开展|要求|坚持|每天|每周).{0,12}(?:密集)?训练")
FORBIDDEN_TRACK = re.compile(r"(?m)^#{2,4}\s*(?:主攻方向|维持方向)|^####\s*(?:主攻|维持)[：:]")
INTERNAL_NOTES = re.compile(r"(?m)^#{1,4}\s*(?:【?内部注释】?|给\s*Agent|Agent\s*工作记录)", re.I)


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    end = re.search(rf"(?m)^#{{1,{level}}}\s+", text[match.end():])
    return text[match.end():match.end() + end.start()] if end else text[match.end():]


def find_heading(text: str, options: tuple[str, ...]) -> tuple[str, re.Match[str] | None]:
    matches = []
    for heading in options:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
        if match:
            matches.append((match.start(), heading, match))
    if not matches:
        return options[0], None
    _, heading, match = min(matches, key=lambda item: item[0])
    return heading, match


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not TITLE.search(text):
        errors.append("标题必须是：# {匿名代号} {YYYY} Q{N} 婴幼儿个性化发展计划")
    positions: list[int] = []
    for options in HEADING_GROUPS:
        heading, match = find_heading(text, options)
        if not match:
            errors.append(f"缺少章节：{options[0]}")
        else:
            positions.append(match.start())
    if len(positions) == len(HEADING_GROUPS) and positions != sorted(positions):
        errors.append("章节顺序错误")
    if BOUNDARY not in text:
        errors.append("缺少专业边界声明")
    if FORBIDDEN_TRACK.search(text):
        errors.append("0—35 月龄计划不得设置主攻/维持双轨")

    observations = OBSERVATION.findall(section(text, "## 本季度发展观察重点"))
    if not 3 <= len(observations) <= 5:
        errors.append("必须设置 3—5 条发展观察线")
    env_heading, _ = find_heading(text, HEADING_GROUPS[4])
    environments = ENVIRONMENT.findall(section(text, env_heading))
    if not 3 <= len(environments) <= 5:
        errors.append("必须设置 3—5 个环境提供方案")
    if not EVIDENCE_REF.search(text):
        errors.append("全文缺少年度或季度证据编号（E## / Q##）")

    review = section(text, "## 每月复盘三问")
    if len(re.findall(r"(?m)^\s*(?:1[.、]|2[.、]|3[.、])\s*", review)) < 3:
        errors.append("每月复盘三问必须包含三个编号问题")
    speech = section(text, "## 家长话术")
    speech_rows = len(re.findall(r"(?m)^\|[^|]+\|[^|]+\|[^|]+\|\s*$", speech))
    if speech_rows < 7:  # header + separator + at least five scenarios
        warnings.append("家长话术建议覆盖至少 5 个高频场景")
    if INTERNAL_NOTES.search(text):
        errors.append("对外家长报告不得包含内部注释或 Agent 工作记录")
    for risk in RISKS:
        if risk.search(text):
            errors.append(f"命中风险表达：{risk.pattern}")
    if TRAINING.search(text):
        warnings.append("检测到训练式表达：请确认改变的是成人、环境和流程")
    if OVERCLAIM.search(text):
        warnings.append("检测到可能用‘说明/证明’升格单次证据")
    if re.search(r"\{\{|\[(?:TODO|待填|请替换)", text, re.I):
        errors.append("仍有占位符")
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if chinese_chars < 2200 or chinese_chars > 12000:
        warnings.append(f"当前约 {chinese_chars} 个中文字符；基础计划通常约 4000—7000 字，完整优先")
    return sorted(set(errors)), sorted(set(warnings))


def sample() -> str:
    parts = ["# CHILD-A 2026 Q3 婴幼儿个性化发展计划", "## 使用说明与边界", BOUNDARY,
             "## 家庭画像速览", "家庭画像 E01 Q01", "## 五维度画像提炼", "五个维度 Q02",
             "## 本季度发展观察重点"]
    for index in range(1, 4):
        parts.extend([f"### 观察线 {index}：共同参与", "观察什么；已有证据 Q01；本季度观察问题？"])
    parts.append("## 环境提供方案")
    for index in range(1, 4):
        parts.extend([f"### 环境 {index}：生活游戏", "为什么；怎么做；最低版本；与观察线连接。"])
    parts.extend(["## 本计划观察指标", "绿灯继续，黄灯微调，红灯停止或求助。",
                  "## 家长话术", "| 场景 | 可以说 | 避免说 |", "|---|---|---|",
                  "| 转换 | 我们一起看下一步 | 快点 |", "| 游戏 | 你想怎么继续 | 这样才对 |",
                  "| 拒绝 | 你可以停一下 | 必须做 |", "| 分离 | 我会按确认的安排回来 | 别哭 |",
                  "| 收尾 | 保存好下次继续 | 马上收 |", "## 避坑提醒", "风险—证据—替代做法。",
                  "## 每月复盘三问", "1. 孩子体验怎样？", "2. 观察到什么变化？", "3. 家庭负担怎样？",
                  "## 下季度展望", "依据季度末新资料再决定。"])
    return "\n\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        good = sample()
        bad_track = good.replace("## 本季度发展观察重点", "## 本季度发展观察重点\n\n#### 主攻：语言")
        bad_count = good.replace("### 观察线 3：共同参与", "### 其他：共同参与")
        bad_internal = good + "\n\n## 内部注释\n给 Agent"
        ok = not validate(good)[0] and all(validate(item)[0] for item in (bad_track, bad_count, bad_internal))
        print("SELF-TEST PASS" if ok else f"SELF-TEST FAIL: {validate(good)[0]}")
        return 0 if ok else 1
    if args.plan is None:
        parser.error("plan is required unless --self-test is used")
    try:
        text = args.plan.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors, warnings = validate(text)
    print("PASS" if not errors else "FAIL")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
