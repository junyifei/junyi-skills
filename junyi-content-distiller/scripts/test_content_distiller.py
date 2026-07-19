#!/usr/bin/env python3
"""Regression tests for split, merge, and validation helpers."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import merge_chunks as merge  # noqa: E402
import split_recording_md as split  # noqa: E402
import validate_distillation as validate  # noqa: E402


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


def material_item(number: int, title: str, evidence: str, quote: str) -> str:
    return f"""#### {number}. {title}
**可用于**：文章
**证据位置**：{evidence}

说明。

📎 **原话**：
> A：「{quote}」"""


def test_split_hard_limit() -> None:
    text = "说话人 1 00:00:01\n" + ("很长的一行" * 500) + "\n说话人 2 00:02:00\n结束。\n"
    chunks = split.split_lines(text.splitlines(keepends=True), 600)
    check("split creates multiple chunks", len(chunks) > 1, str(len(chunks)))
    check("every chunk respects hard limit", all(len(chunk) <= 600 for chunk in chunks), str([len(c) for c in chunks]))
    normal = "".join(
        f"说话人 {index % 2 + 1} 00:{index:02d}:00\n这是第 {index} 段正常长度的表达。\n"
        for index in range(20)
    )
    normal_chunks = split.split_lines(normal.splitlines(keepends=True), 500)
    check(
        "speaker label stays with following utterance when it fits",
        all(not re.search(r"说话人\s+\d+\s+\d{2}:\d{2}:\d{2}\s*$", chunk) for chunk in normal_chunks),
        repr(normal_chunks),
    )


def test_split_manifest_is_resumable() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source.md"
        source.write_text("A 00:00:01\n第一段\nB 00:00:10\n第二段\n", encoding="utf-8")
        chunks = split.split_lines(source.read_text(encoding="utf-8").splitlines(keepends=True), 500)
        manifest = split.build_manifest(source, root / "chunks", chunks, 500)
        check("manifest starts pending", all(item["status"] == "pending" for item in manifest["chunks"]))
        check("manifest has one entry per chunk", manifest["chunk_count"] == len(chunks))
        isolated = split.build_manifest(source, root / "isolated", ["a", "b", "c"], 500)
        check("three chunks require isolation", isolated["isolation"]["required"] is True)
        check("isolated manifest starts unassigned", isolated["isolation"]["mode"] == "unassigned")
        check(
            "isolated chunks start without worker assignment",
            all(item["worker_mode"] == "unassigned" for item in isolated["chunks"]),
        )


def test_merge_fixed_order_and_deduplication() -> None:
    chunk_a = f"""# Chunk 1
## 💡 观点
{material_item(1, "慢一点反而更快", "00:10:00", "真正的快，是不返工。")}

## 今日核心事件
1. 🔴 **确认新方向**——停止返工。（证据：00:10:00）

## 📋 工作待办安排
| 类型 | 事项 | 责任人 | 时间线索 | 状态 | 证据位置 |
|---|---|---|---|---|---|
| 待办 | 完成首页 | A | 周五 | 已确定 | 00:20:00 |
"""
    chunk_b = f"""# Chunk 2
## 情绪地图
- 下午：紧张→放松｜证据：00:30:00–00:40:00

## 🎬 故事
{material_item(9, "第一次公开演示", "00:30:00–00:40:00", "设备坏了，但我还是讲完了。")}

## 💡 观点
{material_item(7, "慢一点反而更快", "00:10:00", "真正的快，是不返工。")}
"""
    result = merge.merge_texts([chunk_a, chunk_b], "内容蒸馏 · 测试", "测试材料")
    headings = [name for name, _ in validate.heading_blocks(result)]
    check(
        "merge uses fixed order",
        headings == ["今日核心事件", "情绪地图", "🎬 故事", "💡 观点", "📋 工作待办安排"],
        str(headings),
    )
    check("duplicate item removed", result.count("慢一点反而更快") == 1, str(result.count("慢一点反而更快")))
    check("items renumber per section", "#### 1. 第一次公开演示" in result and "#### 1. 慢一点反而更快" in result)
    check("merged daily output validates", not validate.validate_text(result, daily=True), str(validate.validate_text(result, daily=True)))


def test_validator_rejects_missing_evidence() -> None:
    invalid = """# 内容蒸馏
## 💡 观点
#### 1. 没有证据的观点
说明。
"""
    errors = validate.validate_text(invalid)
    check("validator detects missing evidence", any("missing evidence" in error for error in errors), str(errors))
    check("validator detects missing quote", any("missing original quote" in error for error in errors), str(errors))


def test_short_sample_without_timestamp() -> None:
    output = f"""# 内容蒸馏 · 短日记
## 🎭 场景
{material_item(1, "雨里等车的十分钟", "短日记.md，第 3 段；原文未提供时间戳", "我站在屋檐下，突然觉得这十分钟也不用赶。")}
"""
    check("short sample without timestamps validates", not validate.validate_text(output), str(validate.validate_text(output)))


def test_validator_rejects_wrong_order_and_speaker_guess() -> None:
    invalid = f"""# 内容蒸馏
## 💡 观点
{material_item(1, "观点", "00:01:00", "一句话")}
## 🎬 故事
{material_item(1, "故事", "00:02:00", "说话人 1 讲了故事")}
"""
    errors = validate.validate_text(invalid)
    check("validator detects wrong order", any("fixed order" in error for error in errors), str(errors))
    check("validator detects speaker labels", any("speaker-number" in error for error in errors), str(errors))


def test_manifest_validation() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "raw.md"
        chunk = root / "chunk_001.md"
        distilled = root / "chunk_001.distilled.md"
        source.write_text("raw", encoding="utf-8")
        chunk.write_text("chunk", encoding="utf-8")
        distilled.write_text("distilled", encoding="utf-8")
        manifest = {
            "source": str(source),
            "chunk_count": 1,
            "chunks": [
                {
                    "chunk": 1,
                    "path": str(chunk),
                    "distilled_path": str(distilled),
                    "status": "distilled",
                    "skip_reason": "",
                }
            ],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        check("complete manifest validates", not validate.validate_manifest(manifest_path), str(validate.validate_manifest(manifest_path)))
        manifest["chunks"][0]["status"] = "pending"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        errors = validate.validate_manifest(manifest_path)
        check("pending manifest fails", any("still pending" in error for error in errors), str(errors))


def test_isolation_contract() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "raw.md"
        source.write_text("raw", encoding="utf-8")
        chunks = []
        for number in range(1, 4):
            chunk = root / f"chunk_{number:03d}.md"
            distilled = root / f"chunk_{number:03d}.distilled.md"
            chunk.write_text("chunk", encoding="utf-8")
            distilled.write_text("distilled", encoding="utf-8")
            chunks.append(
                {
                    "chunk": number,
                    "path": str(chunk),
                    "distilled_path": str(distilled),
                    "status": "distilled",
                    "skip_reason": "",
                    "worker_mode": "unassigned",
                    "worker_run": "",
                }
            )
        manifest = {
            "source": str(source),
            "chunk_count": 3,
            "isolation": {
                "required": True,
                "threshold": 3,
                "mode": "unassigned",
                "orchestrator_read_raw_chunks": False,
            },
            "chunks": chunks,
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        errors = validate.validate_manifest(manifest_path)
        check(
            "three completed chunks fail without isolated workers",
            any("isolation mode" in error for error in errors)
            and any("worker mode" in error for error in errors)
            and any("worker/run" in error for error in errors),
            str(errors),
        )
        try:
            merge.validate_manifest_for_merge(manifest)
            merge_rejected = False
        except ValueError:
            merge_rejected = True
        check("merge refuses unisolated three-chunk manifest", merge_rejected)

        manifest["isolation"]["mode"] = "isolated-worker"
        for entry in manifest["chunks"]:
            entry["worker_mode"] = "isolated-worker"
            entry["worker_run"] = f"worker-{entry['chunk']:03d}"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        check(
            "isolated three-chunk manifest validates",
            not validate.validate_manifest(manifest_path),
            str(validate.validate_manifest(manifest_path)),
        )
        try:
            merge.validate_manifest_for_merge(manifest)
            merge_accepted = True
        except ValueError:
            merge_accepted = False
        check("merge accepts isolated three-chunk manifest", merge_accepted)


def test_merge_updates_manifest() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest_path = root / "manifest.json"
        output = root / "final.md"
        manifest = {
            "chunks": [
                {"chunk": 1, "status": "distilled", "skip_reason": ""},
                {"chunk": 2, "status": "skipped", "skip_reason": "duplicate source"},
            ]
        }
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        merge.update_manifest(manifest_path, output)
        updated = json.loads(manifest_path.read_text(encoding="utf-8"))
        check("merge marks distilled chunks merged", updated["chunks"][0]["status"] == "merged")
        check("merge preserves reasoned skips", updated["chunks"][1]["status"] == "skipped")
        check("merge records final path", updated["final_path"] == str(output.resolve()))


def test_validator_rejects_malformed_work_row() -> None:
    invalid = """# 内容蒸馏
## 📋 工作待办安排
| 类型 | 事项 | 责任人 | 时间线索 | 状态 | 证据位置 |
|---|---|---|---|---|---|
| 待办 | 少了几列 | A |
"""
    errors = validate.validate_text(invalid)
    check("validator detects malformed work row", any("6 columns" in error for error in errors), str(errors))


def test_long_sample_end_to_end() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "全天录音.md"
        source_text = "".join(
            f"说话人 {index % 2 + 1} {index // 60:02d}:{index % 60:02d}:00\n"
            f"这是第 {index} 段记录。我们讨论了一个真实决定，也保留足够上下文。" + ("细节" * 40) + "\n"
            for index in range(240)
        )
        source.write_text(source_text, encoding="utf-8")
        out_dir = root / "chunks"
        out_dir.mkdir()
        chunks = split.split_lines(source_text.splitlines(keepends=True), 8000)
        manifest = split.build_manifest(source, out_dir, chunks, 8000)
        if manifest["isolation"]["required"]:
            manifest["isolation"]["mode"] = "isolated-worker"
        for entry, chunk_text in zip(manifest["chunks"], chunks):
            chunk_path = Path(entry["path"])
            chunk_path.write_text(chunk_text, encoding="utf-8")
            number = entry["chunk"]
            distilled = f"""# Chunk {number:03d} 蒸馏
## 🎬 故事
{material_item(1, f"第 {number} 段的变化", f"chunk_{number:03d}.md，第 1–3 段", "先遇到阻碍，后来我们找到办法。")}
"""
            if number == 1:
                distilled += """
## 今日核心事件
1. 🔴 **确认处理方向**——决定先分块再合并。（证据：chunk_001.md，第 1–3 段）
## 情绪地图
- 上午：紧张→稳定｜证据：chunk_001.md，第 1–3 段
## 📋 工作待办安排
| 类型 | 事项 | 责任人 | 时间线索 | 状态 | 证据位置 |
|---|---|---|---|---|---|
| 决定 | 先分块再合并 | A | 当天 | 已拍板 | chunk_001.md，第 1–3 段 |
"""
            Path(entry["distilled_path"]).write_text(distilled, encoding="utf-8")
            entry["status"] = "distilled"
            if manifest["isolation"]["required"]:
                entry["worker_mode"] = "isolated-worker"
                entry["worker_run"] = f"worker-{number:03d}"

        manifest_path = out_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        texts = [Path(entry["distilled_path"]).read_text(encoding="utf-8") for entry in manifest["chunks"]]
        final_text = merge.merge_texts(texts, "内容蒸馏 · 长录音测试", source.name)
        final_path = root / "final.md"
        final_path.write_text(final_text, encoding="utf-8")
        merge.update_manifest(manifest_path, final_path)
        errors = validate.validate_text(final_text, daily=True) + validate.validate_manifest(manifest_path)
        check("long sample creates multiple bounded chunks", len(chunks) >= 3, str(len(chunks)))
        check("long sample end-to-end validates", not errors, str(errors))


def main() -> int:
    test_split_hard_limit()
    test_split_manifest_is_resumable()
    test_merge_fixed_order_and_deduplication()
    test_validator_rejects_missing_evidence()
    test_short_sample_without_timestamp()
    test_validator_rejects_wrong_order_and_speaker_guess()
    test_manifest_validation()
    test_isolation_contract()
    test_merge_updates_manifest()
    test_validator_rejects_malformed_work_row()
    test_long_sample_end_to_end()
    print(f"RESULT {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
