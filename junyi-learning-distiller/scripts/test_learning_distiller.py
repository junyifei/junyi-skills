#!/usr/bin/env python3
"""Regression tests for learning-source splitting and output validation."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import split_learning_source as split  # noqa: E402
import validate_learning_note as validate  # noqa: E402


PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"PASS {name}")
    else:
        FAIL += 1
        print(f"FAIL {name}: {detail}")


def valid_note() -> str:
    return """# 学习蒸馏｜测试材料
> 来源：测试讲座
> 覆盖范围：完整
> 个人应用背景：未提供
> 外部核验：未进行

## L1｜关键结论
来源主张，小实验比一次性制度化更适合验证新方法。

## L2｜主张与证据地图
### C01｜先小范围测试
**类型**：【来源主张】
**证据位置**：00:12:00–00:14:00
**来源依据**：讲者比较了两种实施方式。
**支持状态**：来源内有支持
**限制**：只有一个案例。

## L3｜用自己的话讲明白
先用一次可逆尝试观察结果，而不是先把方法写成永久规定。例子是先在一个项目试行；反例是对安全底线也只做随意试验。

## L4｜可迁移方法
### M01｜最小试行
**目标**：低成本验证方法。
**前置条件**：行动可逆且风险可控。
**步骤**：1. 选场景；2. 设信号；3. 复盘。
**适用场景**：流程改进。
**不适用场景**：高风险、不可逆决定。
**常见失败方式**：没有预先设观察信号。
**证据位置**：00:12:00–00:18:00

## L5｜与我已有认知的关系
个人应用背景未提供，可能关联到需要试行新流程的场景，待用户判断。

## L6｜应用与小实验
### E01｜一次流程试行
**要验证的假设**：新流程能减少返工。
**真实场景**：待用户选择。
**最小动作**：只在一个任务中试一次。
**观察信号**：返工次数减少。
**停止/调整条件**：错误率上升即停止。
**复盘时间**：完成一次任务后。

## L7｜存疑与待跟进
案例数量不足，待寻找反例。

## L8｜一句话本质
把新认知先变成有边界的小实验，再决定是否长期采用。
"""


def test_valid_note() -> None:
    errors = validate.validate_text(valid_note())
    check("complete eight-layer note validates", not errors, str(errors))


def test_missing_evidence_and_boundary() -> None:
    invalid = valid_note().replace("**证据位置**：00:12:00–00:14:00\n", "", 1)
    invalid = invalid.replace("**不适用场景**：高风险、不可逆决定。\n", "")
    errors = validate.validate_text(invalid)
    check("missing L2 evidence fails", any("L2 item missing evidence" in error for error in errors), str(errors))
    check("missing method boundary fails", any("不适用场景" in error for error in errors), str(errors))


def test_layer_order() -> None:
    invalid = valid_note().replace("## L1｜关键结论", "## TEMP", 1).replace("## L2｜主张与证据地图", "## L1｜关键结论", 1).replace("## TEMP", "## L2｜主张与证据地图", 1)
    errors = validate.validate_text(invalid)
    check("wrong layer order fails", any("out of order" in error for error in errors), str(errors))


def test_long_split_and_manifest() -> None:
    source_text = "\n".join(f"## 第 {index} 节\n" + ("论证内容。" * 300) for index in range(30))
    chunks = split.split_text(source_text, 4000)
    check("long source splits into multiple chunks", len(chunks) > 5, str(len(chunks)))
    check("learning chunks obey hard limit", all(len(chunk) <= 4000 for chunk in chunks), str(max(map(len, chunks))))

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "course.md"
        source.write_text(source_text, encoding="utf-8")
        chunk_dir = root / "chunks"
        ledger_dir = root / "ledgers"
        chunk_dir.mkdir()
        ledger_dir.mkdir()
        manifest = split.build_manifest(source, chunk_dir, chunks, 4000)
        for entry, chunk in zip(manifest["chunks"], chunks):
            Path(entry["path"]).write_text(chunk, encoding="utf-8")
            Path(entry["ledger_path"]).write_text("# ledger\n", encoding="utf-8")
            entry["status"] = "ledgered"
        manifest_path = chunk_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        errors = validate.validate_manifest(manifest_path)
        check("complete long-source manifest validates", not errors, str(errors))


def main() -> int:
    test_valid_note()
    test_missing_evidence_and_boundary()
    test_layer_order()
    test_long_split_and_manifest()
    print(f"RESULT {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
