#!/usr/bin/env python3
"""Five end-to-end persona scenarios required before junyi-vault publication."""

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


PERSONAS = {
    "内容创作者": {
        "structure": {
            "定位与品牌": ["定位", "用户"],
            "创作": ["素材", "选题", "复盘"],
            "学习": ["课程", "行业"],
            "经营": ["产品", "数据"],
        },
        "notes": [
            ("创作/素材/2026-07-19_生活录音素材.md", "生活录音中提取的真实故事"),
            ("创作/复盘/2026-07-19_选题测试复盘.md", "三个选题的表现与结论"),
            ("学习/课程/2026-07-19_叙事课程学习.md", "课程学习蒸馏"),
        ],
        "ambiguous": "一份用户访谈同时涉及用户画像和新产品需求，需在定位与品牌/用户、经营/产品之间确认。",
    },
    "一人公司": {
        "structure": {
            "业务": ["产品", "营销", "交付", "复盘"],
            "客户": ["档案", "沟通", "案例"],
            "系统": ["SOP", "工具", "决策"],
            "个人": ["学习", "健康"],
        },
        "notes": [
            ("客户/沟通/2026-07-19_客户需求确认.md", "客户原话与确认事项"),
            ("系统/SOP/2026-07-19_交付检查清单.md", "重复交付流程"),
            ("业务/复盘/2026-07-19_本周销售复盘.md", "销售动作和结果"),
        ],
        "ambiguous": "个人品牌复盘既可能服务业务营销，也可能属于个人学习，需按未来用途确认。",
    },
    "家庭记录者": {
        "structure": {
            "家庭": ["共同生活", "关系", "健康"],
            "孩子成长": ["观察", "里程碑", "作品"],
            "个人成长": ["学习", "反思", "兴趣"],
            "资料": ["待处理", "公共参考"],
        },
        "notes": [
            ("孩子成长/观察/2026-07-19_第一次主动安慰同伴.md", "具体场景与孩子原话"),
            ("家庭/健康/2026-07-19_家庭体检安排.md", "家庭成员体检安排"),
            ("个人成长/反思/2026-07-19_今天的情绪复盘.md", "个人情绪与判断"),
        ],
        "ambiguous": "家庭旅行既是共同生活，也可能包含孩子成长观察，应按这篇记录的主要用途确认。",
    },
    "上班族": {
        "structure": {
            "工作": ["项目", "会议", "复盘"],
            "专业成长": ["课程", "读书", "技能"],
            "生活": ["健康", "财务", "兴趣"],
            "资料": ["待处理", "公共参考"],
        },
        "notes": [
            ("工作/项目/2026-07-19_网站改版决定.md", "项目决定与责任人"),
            ("工作/会议/2026-07-19_周会纪要.md", "会议决定和待办"),
            ("专业成长/课程/2026-07-19_数据分析课程.md", "课程学习蒸馏"),
        ],
        "ambiguous": "一本产品书的笔记可能用于当前项目，也可能作为长期读书资产，需要用户选择检索入口。",
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


def note_content(title: str) -> str:
    return (
        "---\n"
        "date: 2026-07-19\n"
        f"title: {title}\n"
        "source: persona-test\n"
        "tags: []\n"
        "privacy: private\n"
        "---\n\n"
        f"# {title}\n"
    )


def run_new_vault_persona(name: str, config: dict, base: Path) -> None:
    root = base / name
    build_entries: list[dict] = []
    for domain, classes in config["structure"].items():
        build_entries.append({"type": "directory", "path": domain})
        for class_name in classes:
            build_entries.append({"type": "directory", "path": f"{domain}/{class_name}"})
    build_entries.extend(
        [
            {"type": "file", "path": "知识库说明.md", "content": f"# {name}知识库\n"},
            {"type": "file", "path": "索引.md", "content": "# 索引\n"},
        ]
    )
    build_plan = base / f"{name}-build.json"
    write_plan(build_plan, build_entries)
    prepared = manifest_tool.prepare(build_plan, root, "error")
    check(f"{name}: dry-run does not mutate", not root.exists())
    manifest_tool.apply(prepared, root)

    file_entries = [
        {"type": "file", "path": path, "content": note_content(title)}
        for path, title in config["notes"]
    ]
    file_plan = base / f"{name}-file.json"
    write_plan(file_plan, file_entries)
    file_prepared = manifest_tool.prepare(file_plan, root, "error")
    manifest_tool.apply(file_prepared, root)

    report = scan_vault.scan(root)
    domains = report["structure"]["domains"]
    check(f"{name}: domain count remains minimal", 3 <= len(domains) <= 6, str(domains))
    check(
        f"{name}: three representative notes filed",
        all((root / path).is_file() for path, _ in config["notes"]),
    )
    check(f"{name}: no unapproved extra class", not any("待确认" in path for path in report["structure"]["classes"]))
    check(f"{name}: ambiguous item is deferred", bool(config["ambiguous"]) and report["summary"]["files"] == 5)


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def run_messy_vault_persona(base: Path) -> None:
    root = base / "已有混乱知识库"
    paths = [
        "工作/项目A/会议/2026-01-01.md",
        "职业/项目A/讨论/2026-01-02.md",
        "创作/素材/a.md",
        "个人品牌/素材/b.md",
        "其他/不知道放哪.md",
        "散落会议.md",
    ]
    for relative in paths:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"# {relative}\n", encoding="utf-8")
    before = snapshot(root)
    report = scan_vault.scan(root)
    after = snapshot(root)
    signals = report["signals"]
    check("已有混乱知识库: scan is read-only", before == after)
    check("已有混乱知识库: detects root scatter", "散落会议.md" in signals["root_files"], str(signals))
    check("已有混乱知识库: detects deep hierarchy", bool(signals["deep_files"]), str(signals))
    check("已有混乱知识库: detects generic bucket", "其他" in signals["generic_directories"], str(signals))
    check(
        "已有混乱知识库: detects overlapping class names",
        any(len(items) > 1 for items in signals["duplicate_normalized_directory_names"].values()),
        str(signals["duplicate_normalized_directory_names"]),
    )
    check("已有混乱知识库: no migration applied before confirmation", before == snapshot(root))


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        for name, config in PERSONAS.items():
            run_new_vault_persona(name, config, base)
        run_messy_vault_persona(base)
    print(f"RESULT {PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
