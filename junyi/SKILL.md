---
name: junyi
description: 君一方法论总入口。仅在用户显式调用 /junyi、$junyi、君一方法论，或明确要求“帮我选择君一的哪个 Skill/从哪里开始”时使用。面向已经在用 AI 做真实工作、希望把经验与判断变成可调用方法的一人公司经营者、知识型创作者和创业父母；识别当前任务、已有证据与所处阶段，路由到仓库中最合适的一个 Skill 或最短调用链，包括儿童全年资料采集、分龄全年知识底座、季度资料更新与分龄季度行动计划。它不代替下游 Skill 执行，也不在证据不足时编造经历、案例、用户洞察、儿童资料或平台数据。
---

# 君一方法论

从真实问题和真实材料开始，选择最短有效路径。一次只解决当前最关键的一层。

## 路由流程

1. 读取用户已经提供的目标、材料、事实、边界和当前上下文。
2. 判断任务是人的思考与反方审查、真实材料蒸馏、学习消化、知识库管理、家庭实践、儿童全年或季度成长、个人 IP，还是个人官网。
3. 优先选择一个 Skill。只有上一步产出确实是下一步必要输入时，才组合多个 Skill。
4. 告诉用户选择了哪个 Skill、为什么、还缺什么关键输入。
5. 调用所选 Skill，并遵循它自己的边界、步骤和质量门。不要在本入口内模拟下游流程。

## 路由表

| 用户现在要做什么 | 路由 |
|---|---|
| 通过追问想清楚体验、情绪、矛盾或选择 | `junyi-deep-dialogue` |
| 主动要求挑刺、找漏洞、做魔鬼代言人评审 | `junyi-po-leng-shui` |
| 转换、分块、索引或归档大文档 | `junyi-doc-reader` |
| 从短记录、每日录音或超长录音中提炼真实内容、证据、原则和待办 | `junyi-content-distiller` |
| 把课程、文章、书、访谈或长材料转成自己的理解、边界和实验 | `junyi-learning-distiller` |
| 新建知识库、归档新内容，或只读诊断已有混乱知识库 | `junyi-vault` |
| 记录孩子的具体片段并做发展观察与模型复盘 | `junyi-growth-spark-recorder` |
| 首次收集、导入、补充或审核孩子全年成长规划资料 | `collect-child-growth-intake` |
| 计划日期为 0—35 月龄，全年资料已通过校验，要生成全年判断底座 | `build-infant-growth-plan` |
| 计划日期为 36—71 月龄，全年资料已通过校验，要生成全年判断底座 | `build-preschool-growth-plan` |
| 计划日期为 72—144 月龄，全年资料已通过校验，要生成全年判断底座 | `build-school-age-growth-plan` |
| 已有全年底座，要导入记录、填写季度问卷或判断资料能否生成正式季度计划 | `collect-child-quarterly-update` |
| 季度开始日为 0—35 月龄，资料已 ready，要生成观察线与环境提供方案 | `build-infant-quarterly-growth-plan` |
| 季度开始日为 36—71 月龄，资料已 ready，要生成聚焦与游戏化支持计划 | `build-preschool-quarterly-growth-plan` |
| 季度开始日为 72—144 月龄，资料已 ready，要生成主攻、维持与每周行动计划 | `build-school-age-quarterly-growth-plan` |
| 定位诊断、战略书、商业与内容验证设计 | `junyi-positioning` |
| 找小红书对标账号、样本和爆款标本 | `junyi-xhs-benchmark` |
| 从定位、真实素材和设计方向构建或重做个人/品牌官网 | `junyi-personal-website` |

## 最短调用链

- 不知道从哪里开始：使用 `junyi` 选一个入口，不一次调用全部 Skills。
- 要建立或审核个人 IP 战略：直接走 `junyi-positioning`。
- 只需要研究小红书对标账号与内容样本：直接走 `junyi-xhs-benchmark`。
- 对重大方向既想看见自己又想防止自欺：先 `junyi-deep-dialogue`；形成明确判断后，仅在用户显式要求时调用 `junyi-po-leng-shui`。
- 已有一个亲子片段，只想记录与复盘：直接走 `junyi-growth-spark-recorder`。
- 第一次建立儿童全年规划：先走 `collect-child-growth-intake`；校验通过后，按计划日期完整月龄只进入 `build-infant-growth-plan`、`build-preschool-growth-plan`、`build-school-age-growth-plan` 中的一个。
- 已有兼容全年底座、要做下一季度计划：先走 `collect-child-quarterly-update`；只有 `status: ready` 时，再按季度开始日完整月龄进入三个报告 Skill 中的一个。
- 没有日常成长故事或月报：仍走 `collect-child-quarterly-update` 的年龄自适应问卷路径；不得要求家庭必须持续录音或写月报。
- 缺少兼容全年 `intake.json` 或完整全年规划：返回 `blocked-upstream`，并路由到 `collect-child-growth-intake` 和对应全年报告 Skill；不得用季度问卷代替全年资料采集。
- 季度中途跨过年龄边界：当前季度仍使用开始日对应 Skill；下一季度再重新路由，不中途切换方法。
- 已有大文档，只需要转换、索引或归档：直接走 `junyi-doc-reader`。
- 要从生活、录音或日常记录中找内容素材：走 `junyi-content-distiller`；它不代替外部课程学习蒸馏。
- 要消化外部课程、文章、书或访谈：走 `junyi-learning-distiller`；它不把来源观点冒充自己的结论。
- 要从零搭知识库：`junyi-vault` 建库模式；已有稳定结构只需放新内容：同一 Skill 的归档模式；结构混乱时先走只读诊断模式。
- 从零建立个人 IP 战略：直接走 `junyi-positioning`；需要独立研究小红书对标时，再走 `junyi-xhs-benchmark`。
- 建个人官网：已有完整《IP战略书》时直接走 `junyi-personal-website`；定位仍不清楚时先走 `junyi-positioning`。官网 Skill 自己判断静态站、内容站或应用，不默认堆框架。
- 长期个人材料路径：`junyi-content-distiller` → `junyi-learning-distiller` → `junyi-vault`；只调用当前缺少的一步，不强迫重跑全链。

## 证据门

将事实、推断、假设和未知分开：

- 有真实材料：保留出处、原话与不确定性。
- 只有方向：先索取一个最小真实样本，或把产出明确标为待验证假设。
- 缺少目标、材料或交付形式且会改变路由：只问最关键的一个问题。
- 不得把外部案例改写成用户经历，不得用流行表达冒充用户洞察，不得承诺未经验证的传播结果。

## 边界

- 本 Skill 是路由器，不是万能生成器。
- 不因为完整链路看起来专业，就强迫用户从第一步重跑。
- 不同时调用职责重叠的 Skill。
- 不自动发布内容、写入外部系统或替用户作最终决策。
