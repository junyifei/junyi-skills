#!/usr/bin/env python3
"""Validate the school-age intake handoff."""

from __future__ import annotations
import argparse, json, sys
from datetime import date
from pathlib import Path

TRACK, LOW, HIGH = "school-age", 72, 145

def months(birth: date, as_of: date) -> int:
    return (as_of.year-birth.year)*12 + as_of.month-birth.month - (as_of.day < birth.day)

def validate(data):
    errors=[]
    if data.get("schema_version") != "junyi-child-growth-intake/v1": errors.append("schema_version 不匹配")
    if data.get("plan_track") != TRACK: errors.append(f"只接受 plan_track={TRACK}")
    try:
        birth=date.fromisoformat(data["child"]["birth_date"]); as_of=date.fromisoformat(data["plan_as_of"]); age=months(birth,as_of)
        if data["child"].get("age_months") != age: errors.append(f"age_months 应为 {age}")
        if not LOW <= age < HIGH: errors.append(f"月龄 {age} 不属于 72—144 月龄")
    except (KeyError, TypeError, ValueError): errors.append("缺少有效计划日期、出生日期或 child")
    for field in ("family_goals","child_goals","strengths","observations","attempts"):
        if not isinstance(data.get(field),list) or not data[field]: errors.append(f"{field} 不能为空")
    if len(data.get("observations",[])) < 6: errors.append("至少需要六条观察")
    sources={str(item.get("source","")).strip() for item in data.get("observations",[]) if isinstance(item,dict)}
    if not any("孩子" in source for source in sources): errors.append("至少需要一种孩子视角证据")
    if not any(any(label in source for label in ("家长","教师","老师","照护")) for source in sources): errors.append("至少需要一种成人视角证据")
    return sorted(set(errors))

def self_test():
    obs=[{"source":"孩子"}]+[{"source":"家长"}]*5
    good={"schema_version":"junyi-child-growth-intake/v1","plan_track":"school-age","plan_as_of":"2026-07-17","child":{"birth_date":"2018-07-18","age_months":95},"family_goals":["目标"],"child_goals":["孩子目标"],"strengths":["优势"],"observations":obs,"attempts":["尝试"]}
    if validate(good): return 1
    good["plan_track"]="preschool"
    return 0 if validate(good) else 1

def main():
    p=argparse.ArgumentParser(); p.add_argument("input",nargs="?",type=Path); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    if a.self_test: result=self_test(); print("SELF-TEST PASS" if result==0 else "SELF-TEST FAIL"); return result
    if not a.input: p.error("input required")
    try: data=json.loads(a.input.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors=validate(data); print("PASS" if not errors else "FAIL"); [print(f"ERROR: {e}") for e in errors]; return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
