---
name: junyi-preschool-annual-plan
description: 从通过校验的 `junyi-child-growth-intake/v1` 资料包生成 36—71 月龄儿童的个性化全年成长规划与家庭成长顾问 Agent 长期知识底座。用于家庭已经完成适龄问卷、plan_track=preschool、孩子处于学前生活阶段，并需要优势画像、游戏与学习过程、生活自主、社会情感、家庭与幼儿园协作、90 天行动实验、四季度路线图和入学过渡支持时。不得用于其他月龄、资料采集、医学心理诊断、发育筛查、固定学习类型或入学准备度评分；资料不足时路由到 junyi-child-annual-intake。
---

# 3—6 岁全年成长规划

只处理 `plan_track=preschool`。不要读取婴幼儿或学龄期方法、问卷与报告结构。

本 Skill 产出家庭成长顾问 Agent 的年度判断底座：整理证据、年度方向和首轮可验证假设。它优先作为 Agent 长期读取的基础语料，同时也应让父母和孩子能够理解和更正。报告中的 90 天实验不等同于完整季度执行指南；需要更新季度计划时，先使用 `junyi-child-quarterly-intake` 整理本季新证据，资料为 `status: ready` 后再路由到 `junyi-preschool-quarterly-plan`。

## 1. 验证输入

```bash
python scripts/validate_bundle.py path/to/intake.json
```

轨道或月龄不符立即退出。缺少跨情境观察、家庭目标或孩子视角时，返回缺口并调用 `junyi-child-annual-intake`。不要用常识补齐孩子经历。

## 2. 建立证据中间层

区分事实、来源、情境、暂时解释和未知。先写兴趣、优势、重要关系和环境资源，再选择最多三个支持重点。读取 [references/preschool-method.md](references/preschool-method.md) 和 [references/evidence-and-safety.md](references/evidence-and-safety.md)。

证据地图沿用 intake 的冻结内容：不得补写未知日期、改变来源、删除冲突，或把单次观察升级为稳定能力。正文的时间范围和确定性不得高于证据层；单次材料只能写成“提示/待复现”，不能写“说明、证明、已经稳定”。

不把 VARK、多元智能、左右脑或一次表现写成固定类型；不生成入学准备度分数。

孩子目标与偏好只能来自孩子原话或明确表达；教师转述或成人推断不得写成孩子自己的目标，须标注来源并注明“待与孩子确认”。

## 3. 设计全年计划

以游戏、真实生活参与和关系协作为主。每个重点设计一个 6—12 周实验，写清目标、证据、孩子/成人/环境行动、频率、成功信号、停止或调整条件和最少记录。

每个成功信号先给出可比基线和复盘时点。凡依赖家庭或园所尚未确认的资源、活动、入学安排或重大改变，只能写成“确认后启动”的备选项，不得列为既定路线。标题中的“家庭与学前行动”只表示协作场景，不代表孩子已经参与设计；孩子未实际参与选择时必须写“待与孩子确认”。

四季度路线图应覆盖家庭、学前环境和必要的入学过渡，但不能承诺识字量、竞赛、录取或未来成就。

## 4. 分章生成与验收

严格使用 [references/report-structure.md](references/report-structure.md)。逐章生成时显式列出顺序，每章先验证证据与隐私，再拼装并人工通读。

```bash
python scripts/validate_plan.py path/to/plan.md
```

校验器 PASS 只表示结构和已知风险表达通过；仍须人工核对证据忠实度、发育定性、孩子能动性和安全边界。

未经用户要求，不写入飞书或其他外部系统。
