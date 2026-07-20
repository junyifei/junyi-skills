#!/usr/bin/env python3
"""Validate a public 0-3 annual growth plan."""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

HEADINGS=("# 0—3 岁全年成长规划","## 使用说明与边界","## 宝宝与家庭情境","## 证据地图","## 优势、兴趣与关系资源","## 日常参与画像","## 当前支持重点","## 90 天家庭行动实验","## 全年路线图","## 照护者协作与家庭负担","## 复盘安排","## 需要进一步了解","## 专业支持提示")
QUARTERS=("### 第一季度","### 第二季度","### 第三季度","### 第四季度")
FIELDS=("目标","依据","成人与环境行动","频率","成功信号","停止或调整条件","记录方式")
SAFETY="本规划不替代医疗、心理、发育筛查或教育专业评估"
RISKS=(r"(?:诊断|确诊)为",r"(?<!不)(?:一定|必然)(?:会|能|可以|成为)",r"(?:VARK|多元智能|左右脑).{0,12}(?:类型|定型|分数)",r"/" r"Users/[^\s)]+",r"(?i)\b(?:app_secret|access_token|api_key)\b\s*[:=]")

AGENCY=(r"共同设计",r"共同选定",r"共同选择",r"共同作者",r"全程参与.{0,8}选择")
TYPICALITY=r"(?:不是|并非)(?:异常|问题)|属于正常|发育正常"
OVERCLAIM=r"(?:说明|证明).{0,24}(?:能力|发育|人格|天赋|特质|类型)"
SURNAMES="王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾萧田董袁潘蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔汤"
TEACHER=re.compile(rf"[{SURNAMES}]老师")

def validate(text):
    errors=[]; positions=[]; warnings=[]
    for h in HEADINGS:
        m=re.search(rf"(?m)^{re.escape(h)}\s*$",text)
        if not m: errors.append(f"缺少章节：{h}")
        else: positions.append(m.start())
    if len(positions)==len(HEADINGS) and positions!=sorted(positions): errors.append("章节顺序错误")
    for q in QUARTERS:
        if not re.search(rf"(?m)^{re.escape(q)}\s*$",text): errors.append(f"缺少季度：{q}")
    if SAFETY not in text: errors.append("缺少专业边界声明")
    if not all(x in text for x in ("观察事实","来源","情境","解释或假设","置信度")): errors.append("证据地图字段不完整")
    if len(re.findall(r"(?m)^### (?:重点|支持重点)[：:]",text))>3: errors.append("支持重点超过三个")
    chunks=re.split(r"(?m)^### 实验[：:]",text)[1:]
    if not chunks: errors.append("缺少行动实验")
    for i,c in enumerate(chunks,1):
        for f in FIELDS:
            if not re.search(rf"(?m)^[-*]?\s*\*{{0,2}}{re.escape(f)}\*{{0,2}}[：:]",c): errors.append(f"实验 {i} 缺少字段：{f}")
        if not re.search(r"(?m)^[-*]?\s*\*{0,2}基线\*{0,2}[：:]",c): warnings.append(f"实验 {i} 缺少可比基线；新版报告应先定义基线和复盘时点")
    for pattern in RISKS:
        if re.search(pattern,text): errors.append(f"命中风险表达：{pattern}")
    if re.search(r"\{\{|\[(?:TODO|待填|请替换)",text,re.I): errors.append("仍有占位符")
    if any(re.search(p,text) for p in AGENCY):
        warnings.append("检测到孩子能动性断言（如“共同设计/共同选定/全程参与选择”）：请人工核对原始材料中孩子是否确实参与选择；若未参与，应改写为“待与孩子共同确认”的前瞻步骤，不得写成已完成。")
    if TEACHER.search(text):
        warnings.append("疑似保留第三方姓名（如“某老师”）：建议泛化为“教师/班主任”等角色，避免可识别的第三方信息。")
    if re.search(TYPICALITY,text):
        warnings.append("检测到正向发育定性（如“不是异常/属于正常”）：报告不得从正反任一方向替代专业判断。")
    if re.search(OVERCLAIM,text):
        warnings.append("检测到可能用“说明/证明”升格证据：请改为“提示/与……一致/待复现”，并核对证据强度。")
    return sorted(set(errors)), sorted(set(warnings))

def sample():
    parts=[]
    for h in HEADINGS:
        parts += [h,"正文"]
        if h=="## 证据地图": parts += ["观察事实｜来源｜情境｜解释或假设｜置信度","E01"]
        if h=="## 当前支持重点": parts += ["### 重点：日常参与","E01"]
        if h=="## 90 天家庭行动实验": parts += ["### 实验：日常互动","**目标：** 参与更顺畅","**依据：** E01","**成人与环境行动：** 调整节奏","**频率：** 每天","**成功信号：** 更愿意参与","**停止或调整条件：** 明显不适","**记录方式：** 简记"]
        if h=="## 全年路线图":
            for q in QUARTERS: parts += [q,"月度观察锚点与调整条件"]
    parts.insert(3,SAFETY)
    return "\n\n".join(parts)

def main():
    p=argparse.ArgumentParser(); p.add_argument("plan",nargs="?",type=Path); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    if a.self_test:
        ok=not validate(sample())[0] and bool(validate(sample().replace(SAFETY,"无边界"))[0]); print("SELF-TEST PASS" if ok else "SELF-TEST FAIL"); return 0 if ok else 1
    if not a.plan: p.error("plan required")
    try: text=a.plan.read_text(encoding="utf-8")
    except OSError as exc: print(f"ERROR: {exc}",file=sys.stderr); return 2
    errors,warnings=validate(text); print("PASS" if not errors else "FAIL"); [print(f"WARNING: {w}") for w in warnings]; [print(f"ERROR: {e}") for e in errors]; return 0 if not errors else 1
if __name__=="__main__": raise SystemExit(main())
