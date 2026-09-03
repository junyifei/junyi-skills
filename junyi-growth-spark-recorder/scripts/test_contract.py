#!/usr/bin/env python3
"""Deterministic package and permission-contract checks."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS {label}")


def main() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    models = (ROOT / "references" / "models.md").read_text(encoding="utf-8")

    check("name: junyi-growth-spark-recorder" in skill, "canonical-name")
    check("无法确定授权时，默认只分析" in skill, "analysis-default")
    check("不得静默使用今天" in skill, "unknown-date-block")
    check("保存事件不等于允许修改长期画像" in skill, "profile-separate-permission")
    check("每个事件只创建一份主记录" in skill, "single-event-source")
    check("不得自造或改写近义模型名" in skill, "exact-model-name")
    check("不做医学、心理、神经发育或教育诊断" in skill, "no-diagnosis")
    check("输出前事实终审" in skill, "claim-audit")

    headings = re.findall(r"^###\s+(\d+)\.\s+(.+)$", models, flags=re.MULTILINE)
    check(len(headings) == 62, "core-model-count-62")
    check(headings[0][0] == "1" and headings[-1][0] == "62", "model-number-range")

    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="strict")
        for path in ROOT.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    user_root_marker = "/" + "Users" + "/"
    account_pattern = re.compile("(?:app_" + "token|table_" + "id|ou_" + "[A-Za-z0-9]+)")
    check(user_root_marker not in public_text and "\ufffd" not in public_text, "portable-utf8")
    check(not account_pattern.search(public_text), "no-account-identifiers")

    validator = ROOT / "scripts" / "validate_config.py"
    with tempfile.TemporaryDirectory(prefix="growth-spark-contract-") as tmp:
        tmp_path = Path(tmp)
        valid = {
            "schema_version": 1,
            "archive_root": str(tmp_path / "archive"),
            "subjects": [{"id": "child-a", "display_name": "孩子A", "birth_date": ""}],
            "write_policy": {
                "event_records": True,
                "profile_updates_require_separate_confirmation": True,
            },
        }
        valid_path = tmp_path / "valid.json"
        valid_path.write_text(json.dumps(valid, ensure_ascii=False), encoding="utf-8")
        ok = subprocess.run([sys.executable, str(validator), str(valid_path)], capture_output=True, text=True)
        check(ok.returncode == 0, "valid-config-accepted")

        valid["archive_root"] = "relative"
        invalid_path = tmp_path / "invalid.json"
        invalid_path.write_text(json.dumps(valid, ensure_ascii=False), encoding="utf-8")
        bad = subprocess.run([sys.executable, str(validator), str(invalid_path)], capture_output=True, text=True)
        check(bad.returncode != 0, "unsafe-config-rejected")


if __name__ == "__main__":
    main()
