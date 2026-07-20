#!/usr/bin/env python3
"""Validate the infant intake handoff."""

from __future__ import annotations
import argparse, json, sys
from datetime import date
from pathlib import Path

TRACK, LOW, HIGH = "infant", 0, 36

def months(birth: date, as_of: date) -> int:
    return (as_of.year-birth.year)*12 + as_of.month-birth.month - (as_of.day < birth.day)

def validate(data):
    errors=[]
    if data.get("schema_version") != "junyi-child-growth-intake/v1": errors.append("schema_version 不匹配")
    if data.get("plan_track") != TRACK: errors.append(f"只接受 plan_track={TRACK}")
    try:
        birth=date.fromisoformat(data["child"]["birth_date"]); as_of=date.fromisoformat(data["plan_as_of"]); age=months(birth,as_of)
        if data["child"].get("age_months") != age: errors.append(f"age_months 应为 {age}")
        if not LOW <= age < HIGH: errors.append(f"月龄 {age} 不属于 0—35 月龄")
    except (KeyError, TypeError, ValueError): errors.append("缺少有效计划日期、出生日期或 child")
    for field in ("family_goals","strengths","observations","attempts"):
        if not isinstance(data.get(field),list) or not data[field]: errors.append(f"{field} 不能为空")
    if len(data.get("observations",[])) < 6: errors.append("至少需要六条观察")
    return sorted(set(errors))

def self_test():
    good={"schema_version":"junyi-child-growth-intake/v1","plan_track":"infant","plan_as_of":"2026-07-17","child":{"birth_date":"2024-07-18","age_months":23},"family_goals":["目标"],"strengths":["优势"],"observations":[{}]*6,"attempts":["尝试"]}
    if validate(good): return 1
    good["plan_track"]="preschool"
    return 0 if validate(good) else 1

def main():
    p=argparse.ArgumentParser(); p.add_argument("input",nargs="?",type=Path); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    if a.self_test:
        result=self_test(); print("SELF-TEST PASS" if result==0 else "SELF-TEST FAIL"); return result
    if not a.input: p.error("input required")
    try: data=json.loads(a.input.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors=validate(data); print("PASS" if not errors else "FAIL"); [print(f"ERROR: {e}") for e in errors]; return 0 if not errors else 1
if __name__ == "__main__": raise SystemExit(main())
