#!/usr/bin/env python3
"""Validate a public 36-71 month quarterly growth plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADINGS = (
    "## 使用说明与边界", "## 家庭画像速览", "## 五维度画像提炼", "## 本季度聚焦方向",
    "### 决策透明：为什么选择这些方向", "### 聚焦方向", "### 自然维持方向",
    "## 游戏化学习与生活建议", "## 家长话术", "## 避坑提醒", "## 观察与复盘",
    "### 绿灯：继续保持的信号", "### 黄灯：需要微调的信号", "### 红灯：停止或求助信号",
    "## 每月复盘三问", "## 下季度展望",
)
BOUNDARY = "本计划不替代医疗、心理、发育筛查或教育专业评估"
TITLE = re.compile(r"(?m)^#\s+\S.+\s+\d{4}\s+Q[1-4]\s+学前儿童(?:个性化发展计划|季度成长计划)\s*$")
EVIDENCE_REF = re.compile(r"\b[EQ]\d+\b")
RISKS = (
    re.compile(r"(?:诊断|确诊)为"),
    re.compile(r"(?<!不)(?<!不是)(?<!并非)(?:就是|属于|可判定为)(?:自闭症|孤独症|多动症|ADHD|抑郁症|焦虑症|发育迟缓|感统失调)", re.I),
    re.compile(r"(?:孩子|他|她).{0,8}(?:一定|必然|肯定|绝对).{0,8}(?:会|能|可以)?(?:学会|掌握|达到|成为|超过|追上)"),
    re.compile(r"(?:识字|词汇|算术).{0,8}(?:达到|达标|完成)\s*\d+"),
    re.compile(r"(?:孩子|他|她).{0,6}(?:就是|属于|是(?:一个)?).{0,4}(?:视觉型|听觉型|动觉型|右脑型|左脑型)(?:学习者|类型)?"),
    re.compile(r"/" r"Users/[^\s)]+"),
    re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"),
)
INTERNAL_NOTES = re.compile(r"(?m)^#{1,4}\s*(?:【?内部注释】?|给\s*Agent|Agent\s*工作记录)", re.I)


def section(text: str, heading: str) -> str:
    match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not match:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    end = re.search(rf"(?m)^#{{1,{level}}}\s+", text[match.end():])
    return text[match.end():match.end() + end.start()] if end else text[match.end():]


def validate(text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not TITLE.search(text):
        errors.append("标题必须是：# {匿名代号} {YYYY} Q{N} 学前儿童个性化发展计划")
    positions = []
    for heading in HEADINGS:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
        if not match:
            errors.append(f"缺少章节：{heading}")
        else:
            positions.append(match.start())
    if len(positions) == len(HEADINGS) and positions != sorted(positions):
        errors.append("章节顺序错误")
    if BOUNDARY not in text:
        errors.append("缺少专业边界声明")

    focus_count = len(re.findall(r"(?m)^####\s*聚焦[：:]", text))
    maintain_count = len(re.findall(r"(?m)^####\s*维持[：:]", text))
    if not 1 <= focus_count <= 2:
        errors.append("聚焦方向必须为 1—2 个")
    if not 1 <= maintain_count <= 2:
        errors.append("自然维持方向必须为 1—2 个")
    suggestions = len(re.findall(r"(?m)^####\s*游戏建议[：:]", text))
    if suggestions < focus_count * 3 or suggestions > focus_count * 5:
        errors.append("每个聚焦方向必须提供 3—5 个游戏或生活建议")
    for required in ("孩子直接表达", "为什么现在", "为什么其他方向"):
        if required not in text:
            errors.append(f"缺少季度决策字段：{required}")
    if not EVIDENCE_REF.search(text):
        errors.append("全文缺少年度或季度证据编号（E## / Q##）")
    review = section(text, "## 每月复盘三问")
    if len(re.findall(r"(?m)^\s*(?:1[.、]|2[.、]|3[.、])\s*", review)) < 3:
        errors.append("每月复盘三问必须包含三个编号问题")
    speech = section(text, "## 家长话术")
    if len(re.findall(r"(?m)^\|[^|]+\|[^|]+\|[^|]+\|\s*$", speech)) < 7:
        warnings.append("家长话术建议覆盖至少 5 个高频场景")
    if INTERNAL_NOTES.search(text):
        errors.append("对外家长报告不得包含内部注释或 Agent 工作记录")
    for risk in RISKS:
        if risk.search(text):
            errors.append(f"命中风险表达：{risk.pattern}")
    if re.search(r"\{\{|\[(?:TODO|待填|请替换)", text, re.I):
        errors.append("仍有占位符")
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if chinese_chars < 2200 or chinese_chars > 12000:
        warnings.append(f"当前约 {chinese_chars} 个中文字符；基础计划通常约 4000—7000 字，完整优先")
    return sorted(set(errors)), sorted(set(warnings))


def sample() -> str:
    parts = ["# CHILD-B 2026 Q3 学前儿童个性化发展计划"]
    for heading in HEADINGS:
        parts.extend([heading, "正文 E01 Q01"])
        if heading == "### 决策透明：为什么选择这些方向":
            parts.append("孩子直接表达：想继续搭建。为什么现在：兴趣正在延续。为什么其他方向暂不加码：负担有限。")
        elif heading == "### 聚焦方向":
            parts.append("#### 聚焦：共同搭建")
        elif heading == "### 自然维持方向":
            parts.append("#### 维持：户外游戏")
        elif heading == "## 游戏化学习与生活建议":
            parts.extend(["### 方向：共同搭建", "#### 游戏建议：续建", "最低版本：五分钟。",
                          "#### 游戏建议：角色讲述", "最低版本：一句话。", "#### 游戏建议：共同收尾", "最低版本：保存作品。"])
        elif heading == "## 家长话术":
            parts.extend(["| 场景 | 可以说 | 避免说 |", "|---|---|---|", "| 开始 | 你想先选哪一个 | 快点 |",
                          "| 卡住 | 我陪你试一步 | 这都不会 |", "| 拒绝 | 可以先停 | 必须做 |", "| 收尾 | 保存下次继续 | 马上收 |", "| 分享 | 你想怎么说 | 你应该说 |"])
        elif heading == "## 每月复盘三问":
            parts.extend(["1. 孩子体验怎样？", "2. 哪个建议有效？", "3. 家庭负担怎样？"])
    parts.insert(2, BOUNDARY)
    return "\n\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        good = sample()
        bad_count = good.replace("#### 游戏建议：共同收尾", "#### 其他：共同收尾")
        bad_voice = good.replace("孩子直接表达", "成人推测")
        bad_internal = good + "\n\n## 内部注释\n给 Agent"
        ok = not validate(good)[0] and all(validate(item)[0] for item in (bad_count, bad_voice, bad_internal))
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
