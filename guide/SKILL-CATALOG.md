# 全部 Skill 用户目录

这不是技术文件清单，而是按用户任务整理的选择页。每一行回答：什么时候使用、需要准备什么、会得到什么。若仍无法判断，从 `$junyi` 开始。

## 总入口

| 我现在的情况 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 不知道该用哪个 Skill，或任务可能需要一条短链 | [`junyi`](../junyi/SKILL.md) | 当前目标、已有材料、不能违反的边界 | 一个入口、关键缺口与下一步 |

## 陪孩子成长

这条路径按“成长记录 → 全年底座 → 季度行动”工作。全年底座优先给 Agent 读取，季度计划优先给家长执行。

### 记录一个成长片段

| 我现在想完成什么 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 记录孩子的一个具体片段，并理解为什么有效 | [`junyi-growth-spark-recorder`](../junyi-growth-spark-recorder/SKILL.md) | 发生了什么、谁在场、孩子怎样回应 | 事件记录、发展观察和家长思维模型复盘 |

### 第一次建立全年知识底座

先采集资料，再按计划日期完整月龄进入一个报告 Skill；三个年龄报告 Skill 不混用。

| 年龄与任务 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 0—12 岁首次采集、导入、补充或审核资料 | [`junyi-child-annual-intake`](../junyi-child-annual-intake/SKILL.md) | 计划日期、出生日期、家庭观察；按需要补孩子或教师视角 | `intake.json`、证据地图、完整度和唯一年龄路由 |
| 计划日 0—35 月龄，资料已通过校验 | [`junyi-infant-annual-plan`](../junyi-infant-annual-plan/SKILL.md) | `plan_track=infant` 的有效资料包 | 婴幼儿全年判断底座、首轮实验和四季度路线图 |
| 计划日 36—71 月龄，资料已通过校验 | [`junyi-preschool-annual-plan`](../junyi-preschool-annual-plan/SKILL.md) | `plan_track=preschool` 的有效资料包 | 学前全年判断底座、首轮实验和四季度路线图 |
| 计划日 72—144 月龄，资料已通过校验 | [`junyi-school-age-annual-plan`](../junyi-school-age-annual-plan/SKILL.md) | `plan_track=school-age` 的有效资料包和孩子视角 | 学龄全年判断底座、共同行动实验和四季度路线图 |

### 更新未来 90 天

季度报告需要兼容的全年 `intake.json`、完整全年规划和状态为 `ready` 的本季更新。没有持续记录时可以填写适龄季度问卷。

| 年龄与任务 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 导入本季记录、填写季度问卷或检查资料状态 | [`junyi-child-quarterly-intake`](../junyi-child-quarterly-intake/SKILL.md) | 全年底座、本季新资料或问卷、上季结果 | `quarterly-update.md`、资料状态、补问或观察方案 |
| 季度开始日 0—35 月龄，资料为 `ready` | [`junyi-infant-quarterly-plan`](../junyi-infant-quarterly-plan/SKILL.md) | 全年底座与本季更新 | 观察线、环境提供、互动话术和复盘信号 |
| 季度开始日 36—71 月龄，资料为 `ready` | [`junyi-preschool-quarterly-plan`](../junyi-preschool-quarterly-plan/SKILL.md) | 全年底座与本季更新 | 聚焦方向、自然维持方向和游戏化支持 |
| 季度开始日 72—144 月龄，资料为 `ready` | [`junyi-school-age-quarterly-plan`](../junyi-school-age-quarterly-plan/SKILL.md) | 全年底座、本季更新与孩子表达 | 主攻、维持、最多四个每周行动和最低版本 |

这些 Skill 不做医学心理诊断、发育筛查、学习类型测评或结果预测，也不替代合格专业人员。

## 父母先成长

| 我现在想完成什么 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 把课程、文章、书或访谈真正学会 | [`junyi-learning-distiller`](../junyi-learning-distiller/SKILL.md) | 外部材料与想解决的学习问题 | 来源主张、自己的理解、迁移边界和行动实验 |
| 转换、分块、索引或归档大文档 | [`junyi-doc-reader`](../junyi-doc-reader/SKILL.md) | Word、PDF、TXT、Markdown 或支持的云文档 | 结构化 Markdown、分块索引和归档结果 |
| 新建、归档或诊断知识库 | [`junyi-vault`](../junyi-vault/SKILL.md) | 目标、现有目录或待归档材料 | 建库方案、归档预览或只读诊断报告 |
| 通过追问想清楚体验、情绪、矛盾或选择 | [`junyi-deep-dialogue`](../junyi-deep-dialogue/SKILL.md) | 一个真实问题和愿意回答的当前体验 | 逐层追问、自己的判断和可选觉知记录 |
| 明确要求挑刺、找漏洞或做魔鬼代言人评审 | [`junyi-po-leng-shui`](../junyi-po-leng-shui/SKILL.md) | 已有方案、决定或文稿，以及希望挑战的位置 | 关键漏洞、反证、失败风险和优先修改项 |

## 把成长表达出来

| 我现在想完成什么 | 使用入口 | 准备什么 | 会得到什么 |
|---|---|---|---|
| 把录音、日记或聊天记录变成可追溯素材 | [`junyi-content-distiller`](../junyi-content-distiller/SKILL.md) | 原始记录；有条件时提供说话人和时间戳 | 事件、情绪、故事、观点、金句、证据、原则和待办 |
| 建立、审核或迭代个人 IP 战略 | [`junyi-positioning`](../junyi-positioning/SKILL.md) | 经历、用户证据、内容数据、产品与边界 | 定位决定、证据缺口、验证计划或完整《IP 战略书》 |
| 发现并核验小红书对标 | [`junyi-xhs-benchmark`](../junyi-xhs-benchmark/SKILL.md) | 定位、目标用户、内容与商业路径 | 候选池、核验、分层、评分、排除理由和使用建议 |
| 从定位与真实素材建立个人官网 | [`junyi-personal-website`](../junyi-personal-website/SKILL.md) | 定位、内容、证明、视觉偏好和部署边界 | 原创、响应式、可验收和可部署的网站 |

表达不是家庭教育的必修课，也不能把孩子当作内容素材。只有用户主动选择对外表达时，才进入这条路径。

## 怎样阅读 Skill 页面

每个链接打开的是给 Agent 执行的 `SKILL.md`，因此会比普通产品说明更严格。重点看四处：顶部 `description` 说明什么时候触发；正文开头说明职责；步骤说明 Agent 怎样工作；边界说明什么时候必须停机或把决定交还给人。

安装、调用语法与环境差异见[新手指南](START-HERE.md)和[兼容性说明](COMPATIBILITY.md)。版本与成熟度以根目录 [`skill-index.json`](../skill-index.json) 为准。
