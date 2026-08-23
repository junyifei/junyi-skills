#!/usr/bin/env python3
"""Structural scenarios for the default-skeleton and bounded-adjustment contract."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_manifest as manifest_tool  # noqa: E402
import scan_vault  # noqa: E402


PASS = 0
FAIL = 0


SCENARIOS = {
    "超级个体默认骨架": {
        "structure": {
            "01｜事业与项目": ["当前项目"],
            "02｜个人与生活": ["个人资料"],
            "03｜知识与资产": ["学习输入", "可复用资产"],
            "99｜收件箱": [],
        },
        "notes": [
            ("01｜事业与项目/当前项目/客户需求.md", "当前项目的真实需求"),
            ("03｜知识与资产/学习输入/课程笔记.md", "尚未验证的学习输入"),
            ("03｜知识与资产/可复用资产/访谈模板.md", "跨项目复用模板"),
        ],
    },
    "创业者父母拆分家庭": {
        "structure": {
            "01｜事业与项目": ["当前项目"],
            "02｜个人成长": [],
            "03｜家庭生活": ["孩子成长"],
            "04｜知识与资产": ["学习输入", "可复用资产"],
            "99｜收件箱": [],
        },
        "notes": [
            ("01｜事业与项目/当前项目/交付方案.md", "项目交付方案"),
            ("03｜家庭生活/孩子成长/成长记录.md", "家庭长期责任与隐私材料"),
            ("04｜知识与资产/可复用资产/家庭活动清单.md", "跨场景复用清单"),
        ],
    },
    "内容主业独立表达": {
        "structure": {
            "01｜事业与项目": ["产品"],
            "02｜个人与生活": [],
            "03｜知识与资产": ["学习输入", "可复用资产"],
            "04｜内容与表达": ["素材", "已发布", "反馈"],
            "99｜收件箱": [],
        },
        "notes": [
            ("04｜内容与表达/素材/真实故事.md", "高频独立内容素材"),
            ("04｜内容与表达/反馈/发布反馈.md", "内容效果反馈"),
            ("01｜事业与项目/产品/产品决定.md", "产品经营决定"),
        ],
    },
    "老板增加关系协作": {
        "structure": {
            "01｜事业经营与项目": ["项目"],
            "02｜个人与生活": [],
            "03｜知识与资产": ["SOP", "案例"],
            "04｜关系与协作": ["客户", "伙伴", "团队"],
            "99｜收件箱": [],
        },
        "notes": [
            ("01｜事业经营与项目/项目/项目决定.md", "项目决定"),
            ("04｜关系与协作/伙伴/合作记录.md", "跨项目合作上下文"),
            ("03｜知识与资产/SOP/交付检查.md", "重复交付检查"),
        ],
    },
}


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"PASS {name}")
    else:
        FAIL += 1
        print(f"FAIL {name}: {detail}")


def write_plan(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def run_new_vault_scenario(name: str, config: dict, base: Path) -> None:
    root = base / name
    entries: list[dict] = []
    for domain, classes in config["structure"].items():
        entries.append({"type": "directory", "path": domain})
        for class_name in classes:
            entries.append({"type": "directory", "path": f"{domain}/{class_name}"})
    plan = base / f"{name}-build.json"
    write_plan(plan, entries)
    prepared = manifest_tool.prepare(plan, root, "error")
    check(f"{name}: dry-run does not mutate", not root.exists())
    manifest_tool.apply(prepared, root)

    note_entries = [
        {"type": "file", "path": path, "content": f"# {title}\n"}
        for path, title in config["notes"]
    ]
    note_plan = base / f"{name}-notes.json"
    write_plan(note_plan, note_entries)
    manifest_tool.apply(manifest_tool.prepare(note_plan, root, "error"), root)

    report = scan_vault.scan(root)
    domains = report["structure"]["domains"]
    check(f"{name}: bounded top-level folders", 3 <= len(domains) <= 6, str(domains))
    check(
        f"{name}: three representative items filed",
        all((root / path).is_file() for path, _ in config["notes"]),
    )
    check(
        f"{name}: no forced Junyi seven-domain copy",
        "00｜整体战略与经营" not in domains and "06｜AI协作与执行系统" not in domains,
        str(domains),
    )
    forbidden = ["USER.md", "CLAUDE.md", "AGENTS.md", "00｜工作台入口.md", "00｜当前主线.md"]
    check(
        f"{name}: classification skill creates no workbench system files",
        all(not (root / item).exists() for item in forbidden),
        str([item for item in forbidden if (root / item).exists()]),
    )


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def run_outdated_vault_scenario(base: Path) -> None:
    root = base / "已有但分类过时"
    paths = [
        "旧业务/已停止产品/会议/旧记录.md",
        "工作/项目A/当前项目.md",
        "知识库/客户反馈.md",
        "内容/客户反馈.md",
        "其他/不知道放哪.md",
        "散落项目决定.md",
    ]
    for relative in paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {relative}\n", encoding="utf-8")
    before = snapshot(root)
    report = scan_vault.scan(root)
    after = snapshot(root)
    signals = report["signals"]
    check("已有但分类过时: scan is read-only", before == after)
    check("已有但分类过时: detects root scatter", "散落项目决定.md" in signals["root_files"])
    check("已有但分类过时: detects deep hierarchy", bool(signals["deep_files"]))
    check("已有但分类过时: detects generic bucket", "其他" in signals["generic_directories"])
    check("已有但分类过时: no reorganization before confirmation", before == snapshot(root))


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        for name, config in SCENARIOS.items():
            run_new_vault_scenario(name, config, base)
        run_outdated_vault_scenario(base)
    print(f"RESULT {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
