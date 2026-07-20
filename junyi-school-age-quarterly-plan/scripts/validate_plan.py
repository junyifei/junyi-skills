#!/usr/bin/env python3
"""Validate a public 72-144 month quarterly growth plan."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HEADINGS = (
    "## 使用说明与边界", "## 家庭画像速览", "## 五维度画像提炼", "## 本季度聚焦方向",
    "### 决策透明：为什么选择这些方向", "### 主攻方向", "### 维持方向", "## 行动方案",
    "### 第 0 步：与孩子确认", "### 每周行动清单", "### 至少做到", "## 家长话术",
    "## 避坑提醒", "## 观察与复盘", "### 绿灯：继续保持的信号",
    "### 黄灯：需要微调的信号", "### 红灯：停止或求助信号", "## 每月复盘三问", "## 下季度展望",
)
BOUNDARY = "本计划不替代医疗、心理、发育筛查或教育专业评估"
TITLE = re.compile(r"(?m)^#\s+\S.+\s+\d{4}\s+Q[1-4]\s+学龄儿童(?:个性化发展计划|季度成长计划)\s*$")
ACTION = re.compile(r"(?m)^\|\s*A([1-4])\s*\|")
EVIDENCE = re.compile(r"\b[EQ]\d+\b")
ACADEMIC_DIRECTION = re.compile(r"(?m)^####\s*主攻[：:].*(?:语文|中文|阅读|写作|英语|英文|数学|科学|学科|学习)")
RISKS = (
    re.compile(r"(?:诊断|确诊)为"),
    re.compile(r"(?<!不)(?<!不是)(?<!并非)(?:就是|属于|可判定为)(?:自闭症|孤独症|多动症|ADHD|抑郁症|焦虑症|发育迟缓|感统失调)", re.I),
    re.compile(r"(?:孩子|他|她).{0,8}(?:一定|必然|肯定|绝对).{0,8}(?:会|能|可以)?(?:学会|掌握|达到|成为|超过|追上|考上|录取|上岸|获奖)"),
    re.compile(r"(?:孩子|他|她).{0,6}(?:就是|属于|是(?:一个)?).{0,4}(?:视觉型|听觉型|动觉型|右脑型|左脑型)(?:学习者|类型)?"),
    re.compile(r"(?:VARK|多元智能|左右脑).{0,12}(?:类型|定型|分数|学习者)"),
    re.compile(r"(?<!不)(?<!无法)(?:保证|确保|保准|一定|肯定|绝对).{0,20}(?:成绩|排名|名次|录取|考上|上岸|获奖|(?:进|进入).{0,6}(?:重点|名校))"),
    re.compile(r"/" r"Users/[^\s)]+"),
    re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"),
)
AGENCY = re.compile(r"共同设计|共同选定|共同制定|共同选择")
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
        errors.append("标题必须是：# {匿名代号} {YYYY} Q{N} 学龄儿童个性化发展计划")
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

    main_count = len(re.findall(r"(?m)^####\s*主攻[：:]", text))
    maintain_count = len(re.findall(r"(?m)^####\s*维持[：:]", text))
    if not 1 <= main_count <= 2:
        errors.append("主攻方向必须为 1—2 个")
    if not 1 <= maintain_count <= 2:
        errors.append("维持方向必须为 1—2 个")
    ids = ACTION.findall(section(text, "### 每周行动清单"))
    if not ids:
        errors.append("每周行动清单至少需要一项 A1—A4 行动")
    elif len(ids) > 4 or len(ids) != len(set(ids)):
        errors.append("每周行动必须为不重复的 A1—A4，且最多四项")
    for field in ("孩子直接反馈", "为什么现在", "为什么其他方向", "启动前提"):
        if field not in text:
            errors.append(f"缺少季度执行字段：{field}")
    if not EVIDENCE.search(text):
        errors.append("全文缺少证据编号（E## / Q##）")

    academic = bool(ACADEMIC_DIRECTION.search(text))
    academic_section = "## 学科主攻完整学习方案" in text
    if academic and not academic_section:
        errors.append("学科主攻必须包含完整学习方案")
    if academic_section and not academic:
        warnings.append("出现学科专项但未识别到学科主攻，请人工确认是否必要")
    if academic_section:
        for field in ("当前水平", "置信度", "核验", "一次学习", "分阶段", "选择标准", "评估"):
            if field not in section(text, "## 学科主攻完整学习方案"):
                errors.append(f"学科主攻完整学习方案缺少：{field}")

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
    if AGENCY.search(text):
        warnings.append("检测到共同设计断言：必须人工核对孩子是否实际参与选择")
    if re.search(r"(?:说明|证明).{0,24}(?:能力|人格|天赋|特质|类型)", text):
        warnings.append("检测到可能升格单次证据")
    if re.search(r"\{\{|\[(?:TODO|待填|请替换)", text, re.I):
        errors.append("仍有占位符")
    count = len(re.findall(r"[\u4e00-\u9fff]", text))
    if count < 2800 or count > 15000:
        warnings.append(f"当前约 {count} 个中文字符；基础计划通常约 5000—8000 字，学科专项版可更长")
    return sorted(set(errors)), sorted(set(warnings))


def sample() -> str:
    parts = ["# CHILD-C 2026 Q3 学龄儿童个性化发展计划"]
    for heading in HEADINGS:
        parts.extend([heading, "正文 E01 Q01"])
        if heading == "### 决策透明：为什么选择这些方向":
            parts.append("孩子直接反馈：想自己选顺序。为什么现在：开学窗口。为什么其他方向暂不加码：自然维持即可。")
        elif heading == "### 主攻方向":
            parts.append("#### 主攻：早晨流程")
        elif heading == "### 维持方向":
            parts.append("#### 维持：阅读兴趣")
        elif heading == "### 每周行动清单":
            parts.extend(["| 编号 | 方向 | 具体场景与第一步 | 频率 | 时长 | 负责人 | 启动前提 | 孩子可怎样调整 |",
                          "|---|---|---|---|---|---|---|---|", "| A1 | 流程 | 先选两步 | 3次/周 | 5分钟 | 家庭 | 已确认 | 改顺序 |"])
        elif heading == "## 家长话术":
            parts.extend(["| 场景 | 可以说 | 避免说 |", "|---|---|---|", "| 开始 | 你想先选哪一个 | 快点 |",
                          "| 卡住 | 我们拆一步 | 这都不会 |", "| 拒绝 | 说说哪里不合适 | 必须做 |", "| 复盘 | 哪一步有用 | 都是你的错 |", "| 调整 | 你想怎么改 | 按我说的 |"])
        elif heading == "## 每月复盘三问":
            parts.extend(["1. 孩子体验怎样？", "2. 哪个行动有效？", "3. 双方负担怎样？"])
    parts.insert(2, BOUNDARY)
    return "\n\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        good = sample()
        bad_actions = good.replace("| A1 |", "| A5 |")
        bad_internal = good + "\n\n## 内部注释\n给 Agent"
        academic = good.replace("#### 主攻：早晨流程", "#### 主攻：英语阅读")
        ok = not validate(good)[0] and all(validate(item)[0] for item in (bad_actions, bad_internal, academic))
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
