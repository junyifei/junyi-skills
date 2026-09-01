#!/usr/bin/env python3
"""Check obvious privacy, scope, status, and CTA violations in a draft."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ABSOLUTE_PATH = re.compile(
    r"(?:/" r"Users/|/home/|/private/|[A-Za-z]:\\\\" r"Users\\\\|~/(?:\.openclaw|\.codex|\.claude|\.agents))"
)
BROAD_SCOPE = re.compile(
    r"(?:绝大多数|大多数(?:人|创作者|读者|用户)?|所有(?:人|创作者|读者|用户)|"
    r"每个人都|人人都|大家都|任何人都|无一例外|普遍(?:都会|认为|存在|如此)|"
    r"必然(?:会|导致|发生)?|一定会|从来(?:都|就)|"
    r"(?:常见|共同|普遍的)(?:看法|误解|顾虑|焦虑|问题|需求|感受))"
)
AUDIENCE_PREDICTION = re.compile(
    r"(?:(?:目标)?读者|创作者|用户)[^，。；\n]{0,16}(?:会|都会)[^，。；\n]{0,16}(?:代入|认出|共鸣|理解|相信|接受|感到)"
    r"|让[^，。；\n]{0,24}(?:读者|创作者|用户)[^，。；\n]{0,16}(?:代入|认出|共鸣|理解|相信|接受)"
    r"|(?:目标)?读者[^，。；\n]{0,16}核心(?:顾虑|焦虑|问题|需求)"
)
CONDITIONAL_SCOPE = re.compile(r"(?:如果|假如|可能|有些|部分|某些|对正在|对已经|本来就|有这种|有同样)" )
STATUS_CLAIM = re.compile(
    r"(?:已发布|已经发布|已切换|已经切换|验证成功|已验证成功|迁移已完成|"
    r"(?:公开版|Skill|方法|自己的)[^，。；\n]{0,10}(?:公开了|开放了|上线了))"
)
CTA_CLAIM = re.compile(r"(?:加我微信|添加微信|私信我|评论区|扫码|报名|关注我|联系我们|欢迎加)"
)
NEGATION_OR_AUDIT = re.compile(
    r"(?:不得|不能|不应|不要|禁止|避免|不可|未|没有证据|缺乏证据|待确认|待补|风险|拦截|检查|"
    r"无范围证据|问题清单|修复前定位|状态越界|预测读者|修订|需改动|→|"
    r"不(?:写|声称|升华|使用|添加|引导|出现|回显|扩大|泛化|承诺))"
)


def iter_visible_lines(text: str):
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


def add_violation(items, kind: str, line_no: int, line: str, match: re.Match[str]):
    items.append(
        {
            "kind": kind,
            "line": line_no,
            "match": match.group(0),
            "text": line.strip(),
        }
    )


def check(text: str, scope_evidence: str, status: str, cta: str):
    violations = []
    for line_no, line in iter_visible_lines(text):
        path_match = ABSOLUTE_PATH.search(line)
        if path_match:
            add_violation(violations, "absolute-path", line_no, line, path_match)

        exempt = bool(NEGATION_OR_AUDIT.search(line))

        if scope_evidence == "none" and not exempt:
            scope_match = BROAD_SCOPE.search(line)
            if scope_match:
                add_violation(violations, "unsupported-scope", line_no, line, scope_match)
            audience_match = AUDIENCE_PREDICTION.search(line)
            if audience_match and not CONDITIONAL_SCOPE.search(line):
                add_violation(violations, "unsupported-audience-prediction", line_no, line, audience_match)

        if status == "candidate" and not exempt:
            status_match = STATUS_CLAIM.search(line)
            if status_match:
                add_violation(violations, "status-overclaim", line_no, line, status_match)

        if cta == "none" and not exempt:
            cta_match = CTA_CLAIM.search(line)
            if cta_match:
                add_violation(violations, "unauthorized-cta", line_no, line, cta_match)

    return violations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("draft", type=Path)
    parser.add_argument("--scope-evidence", choices=("none", "provided"), default="none")
    parser.add_argument("--status", choices=("candidate", "published"), default="candidate")
    parser.add_argument("--cta", choices=("none", "authorized"), default="none")
    args = parser.parse_args()

    violations = check(
        args.draft.read_text(encoding="utf-8"),
        scope_evidence=args.scope_evidence,
        status=args.status,
        cta=args.cta,
    )
    result = {"ok": not violations, "violations": violations}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
