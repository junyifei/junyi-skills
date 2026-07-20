#!/usr/bin/env python3
"""Validate the public 36-71 month quarterly plan input bundle."""
from __future__ import annotations
import argparse, calendar, json, re, sys
from datetime import date
from pathlib import Path

INTAKE_SCHEMA="junyi-child-growth-intake/v1"; UPDATE_SCHEMA="junyi-child-quarterly-update/v1"
ANNUAL_TITLE="# 3—6 岁全年成长规划"; PRIOR_ANNUAL_TITLE="# 0—3 岁全年成长规划"; ANNUAL_BOUNDARY="本规划不替代医疗、心理、发育筛查或教育专业评估"
HEADINGS=("## 1. 季度变化与执行复盘","## 2. 证据与来源","## 3. 资料完整性与未知","## 4. 月龄路由与交接结果")
EVENT_BLOCK_RE=re.compile(r"(?ms)^### Q\d+\s*$\n(.*?)(?=^### Q\d+\s*$|^##\s+|\Z)")
FIELD_RE_TEMPLATE=r"^- {label}：\s*(.+?)\s*$"; EMPTY_FACTS={"","（空）","(空)","空","unknown","none","n/a","na","待补充","未提供","无具体事件"}
SENSITIVE=(re.compile(r"/" r"Users/[^\s)]+"),re.compile(r"(?i)\b(?:app_secret|access_token|refresh_token|api_key)\b\s*[:=]"))

def frontmatter(text):
    lines=text.splitlines()
    if not lines or lines[0].strip()!="---": raise ValueError("quarterly update 缺少 YAML frontmatter")
    try: end=lines.index("---",1)
    except ValueError as exc: raise ValueError("quarterly update frontmatter 未闭合") from exc
    data={}
    for line in lines[1:end]:
        if not line.strip(): continue
        if ":" not in line or line.startswith((" ","\t")): raise ValueError(f"无效 frontmatter 行：{line}")
        key,value=line.split(":",1); data[key.strip()]=value.strip().strip("\"'")
    return data,"\n".join(lines[end+1:])

def as_date(value):
    try: return date.fromisoformat(value)
    except (TypeError,ValueError): return None

def months(birth,as_of):
    value=(as_of.year-birth.year)*12+as_of.month-birth.month
    return value-(as_of.day<min(birth.day,calendar.monthrange(as_of.year,as_of.month)[1]))

def event_blocks(body):return [m.group(1) for m in EVENT_BLOCK_RE.finditer(body)]
def field_value(block,label):
    match=re.search(FIELD_RE_TEMPLATE.format(label=re.escape(label)),block,re.MULTILINE)
    if not match:return None
    value=match.group(1).strip();return value if value.lower() not in EMPTY_FACTS else None

def validate(intake,update_text,annual_text):
    errors=[]; warnings=[]
    if not isinstance(intake,dict): return ["intake 根节点必须是 JSON 对象"],warnings
    if intake.get("schema_version")!=INTAKE_SCHEMA: errors.append(f"intake.schema_version 必须是 {INTAKE_SCHEMA}")
    try: update,body=frontmatter(update_text)
    except ValueError as exc: return [str(exc)],warnings
    if update.get("schema_version")!=UPDATE_SCHEMA: errors.append(f"update.schema_version 必须是 {UPDATE_SCHEMA}")
    if update.get("status")!="ready": errors.append("季度资料必须为 status: ready")
    if update.get("plan_track")!="preschool": errors.append("本 Skill 只接受 plan_track: preschool")
    if update.get("child_voice_status") not in {"direct-simple","direct-reflection"}: errors.append("36—71 月龄必须有孩子直接表达")
    for heading in HEADINGS:
        if heading not in body: errors.append(f"quarterly update 缺少章节：{heading}")
    child=intake.get("child") if isinstance(intake.get("child"),dict) else {}
    if update.get("child_id")!=child.get("id"): errors.append("update.child_id 必须与 intake.child.id 一致")
    birth=as_date(child.get("birth_date")); start=as_date(update.get("quarter_start"))
    try: declared=int(update.get("age_months","")); evidence=int(update.get("evidence_count","")); contexts=int(update.get("context_count",""))
    except ValueError: declared=evidence=contexts=-1; errors.append("age_months、evidence_count 和 context_count 必须是整数")
    if birth is None or start is None: errors.append("出生日期和 quarter_start 必须是有效日期")
    else:
        actual=months(birth,start)
        if actual!=declared: errors.append(f"季度开始月龄应为 {actual}，不是 {declared}")
        if not 36<=actual<=71: errors.append(f"季度开始月龄 {actual} 不属于 36—71 月龄")
    if evidence<3: errors.append("正式季度计划至少需要 3 个本季度具体事件")
    if contexts<2: errors.append("正式季度计划至少需要 2 个生活情境")
    blocks=event_blocks(body);body_contexts={value for block in blocks if (value:=field_value(block,"场景"))}
    if len(blocks)!=evidence:errors.append(f"正文 Qxx 数量为 {len(blocks)}，与 evidence_count={evidence} 不一致")
    if len(body_contexts)!=contexts:errors.append(f"正文生活情境数量为 {len(body_contexts)}，与 context_count={contexts} 不一致")
    for index,block in enumerate(blocks,1):
        if not field_value(block,"事实或原话"):errors.append(f"Q{index} 缺少非空事实或原话")
        if not field_value(block,"来源"):errors.append(f"Q{index} 缺少已知来源")
    current_annual=ANNUAL_TITLE in annual_text
    prior_transition=(update.get("track_transition")=="true" and intake.get("plan_track")=="infant" and PRIOR_ANNUAL_TITLE in annual_text)
    if not current_annual and not prior_transition:errors.append("annual plan 必须是当前 3—6 岁全年规划；轨道过渡时可使用上一轨道的 0—3 岁全年规划")
    if prior_transition:warnings.append("使用上一年龄轨道全年规划作为历史底座；本季度按 preschool 方法生成")
    if ANNUAL_BOUNDARY not in annual_text: errors.append("annual plan 缺少专业边界声明")
    if any(p.search(update_text) for p in SENSITIVE): errors.append("quarterly update 包含私有路径或疑似凭证")
    if intake.get("plan_track")!="preschool":
        if update.get("track_transition")!="true":errors.append("全年 intake 来自旧轨道时，update.track_transition 必须为 true")
        else:warnings.append("全年 intake 来自旧年龄轨道；已按轨道过渡作为历史底座使用")
    return sorted(set(errors)),sorted(set(warnings))

def sample():
    intake={"schema_version":INTAKE_SCHEMA,"plan_track":"preschool","child":{"id":"CHILD-B","birth_date":"2022-02-15"}}
    update="""---
schema_version: junyi-child-quarterly-update/v1
status: ready
plan_track: preschool
quarter_start: 2026-07-01
quarter_end: 2026-09-30
as_of: 2026-06-20
child_id: CHILD-B
age_months: 52
annual_plan_as_of: 2026-02-20
previous_plan_status: first-cycle
child_voice_status: direct-simple
track_transition: false
evidence_count: 3
context_count: 3
---
## 1. 季度变化与执行复盘
## 2. 证据与来源
### Q1
- 场景：家庭游戏
- 事实或原话：孩子表达想继续完成搭建
- 来源：孩子和家长
### Q2
- 场景：幼儿园
- 事实或原话：孩子向教师提出需要预告
- 来源：孩子和教师
### Q3
- 场景：社区活动
- 事实或原话：孩子在有限选择后完成收尾
- 来源：家长
## 3. 资料完整性与未知
## 4. 月龄路由与交接结果
"""
    return intake,update,f"{ANNUAL_TITLE}\n\n{ANNUAL_BOUNDARY}"

def main():
    p=argparse.ArgumentParser(); p.add_argument("--intake",type=Path); p.add_argument("--update",type=Path); p.add_argument("--annual-plan",type=Path); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    if a.self_test:
        i,u,n=sample(); ok=not validate(i,u,n)[0] and bool(validate(i,u.replace("status: ready","status: needs-observation"),n)[0]); print("SELF-TEST PASS" if ok else "SELF-TEST FAIL"); return 0 if ok else 1
    if not all((a.intake,a.update,a.annual_plan)): p.error("--intake, --update and --annual-plan are required")
    try: intake=json.loads(a.intake.read_text(encoding="utf-8")); update=a.update.read_text(encoding="utf-8"); annual=a.annual_plan.read_text(encoding="utf-8")
    except (OSError,json.JSONDecodeError) as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors,warnings=validate(intake,update,annual); print("PASS" if not errors else "FAIL"); [print(f"WARNING: {x}") for x in warnings]; [print(f"ERROR: {x}") for x in errors]; return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
