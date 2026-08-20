# 君一的 AI 协作 Skills 新手指南

这份指南帮助第一次使用的人完成三件事：安装、判断自己正处于“理解孩子，支持成长、理解自己，形成判断、沉淀经验，长成事业”中的哪个阶段，并完成第一次真实任务。

## 1. 先选择安装范围

装 Skill 不用自己敲命令行。打开一个能安装 Skill、能读文件的 AI 助手（比如 Claude），把下面对应的那句话整段发给它，它会自己去 GitHub 上装好。

**想全部装上，让「君一 Skills 导航」帮你自动选**：

```text
请帮我从君一的 GitHub 仓库 junyifei/junyi-skills，把公开的 skill 都装上。
```

**只想先看看有哪些、暂时不装**：

```text
帮我看看君一的 GitHub 仓库 junyifei/junyi-skills 里都有哪些 skill，先别安装。
```

**已经知道要哪一个（比如做 IP 定位）**：

```text
请帮我从 junyifei/junyi-skills 只安装 junyi-positioning 这个 skill。
```

装好后，新开一个对话让 AI 重新识别一下就能用了。（想手动安装或看精确命令，见[兼容性与安装说明](COMPATIBILITY.md)。）

<details>
<summary>习惯命令行？点这里</summary>

```bash
npx -y skills add junyifei/junyi-skills -g --all                          # 全部装上
npx -y skills add junyifei/junyi-skills --list                            # 只看不装
npx -y skills add junyifei/junyi-skills -g --skill junyi-positioning -y   # 只装一个
```

手动安装时复制**整个 Skill 文件夹**（不要只复制 `SKILL.md`，否则 references、scripts、assets 可能缺失）。安装后开启一个新会话，让 Agent 重新发现 Skills。
</details>

## 2. 不知道从哪里开始

像平时说话一样，把你的难题直接告诉 AI，比如：

```text
我现在有个问题想解决：……。君一的 GitHub 仓库 junyifei/junyi-skills 里，有没有能帮我的 skill？是哪一个？帮我用它。
```

它会挑出最合适的那个、帮你开始，不用你自己判断该用哪个。「君一 Skills 导航」的技术名称是 `junyi`，只负责判断最短路径，不代替下游 Skill 完成所有工作。想按普通人的任务语言浏览全部能力，先看[全部 Skill 用户目录](SKILL-CATALOG.md)。

## 3. 已经知道任务时直接调用

| 现在要做什么 | 直接使用 |
|---|---|
| 记录孩子的具体片段并复盘 | `$junyi-growth-spark-recorder` |
| 首次收集、导入或审核孩子的全年成长规划资料 | `$junyi-child-annual-intake` |
| 为计划日 0—35 月龄孩子生成全年判断底座 | `$junyi-infant-annual-plan` |
| 为计划日 36—71 月龄孩子生成全年判断底座 | `$junyi-preschool-annual-plan` |
| 为计划日 72—144 月龄孩子生成全年判断底座 | `$junyi-school-age-annual-plan` |
| 已有全年成长底座，要整理本季度新资料或填写季度问卷 | `$junyi-child-quarterly-intake` |
| 为季度开始日 0—35 月龄孩子生成季度计划 | `$junyi-infant-quarterly-plan` |
| 为季度开始日 36—71 月龄孩子生成季度计划 | `$junyi-preschool-quarterly-plan` |
| 为季度开始日 72—144 月龄孩子生成季度计划 | `$junyi-school-age-quarterly-plan` |
| 把课程、文章、书或访谈转成自己的理解与实验 | `$junyi-learning-distiller` |
| 转换、分块、索引或归档大文档 | `$junyi-doc-reader` |
| 新建、归档或只读诊断知识库 | `$junyi-vault` |
| 通过追问想清楚体验、矛盾或选择 | `$junyi-deep-dialogue` |
| 明确要求挑刺、找漏洞或魔鬼代言人 | `$junyi-po-leng-shui` |
| 从录音、日记或聊天记录中提炼真实内容 | `$junyi-content-distiller` |
| 设计、审核或迭代个人 IP 定位 | `$junyi-positioning` |
| 发现并核验小红书对标 | `$junyi-xhs-benchmark` |
| 从定位与真实素材建立个人官网 | `$junyi-personal-website` |

不要为了看起来完整而从第一步重跑。已有草稿、材料或决定时，直接从当前缺失的一层开始。

儿童成长链有两次分龄：首次使用先通过 `junyi-child-annual-intake` 生成并校验全年资料，再按计划日期完整月龄只进入一个全年报告 Skill；更新季度时，三个季度报告 Skill 都要求兼容的全年 `intake.json`、完整全年规划和 `status: ready` 的季度更新。没有持续日常记录时可以填写季度问卷；没有全年底座时先回到全年资料采集，不能直接生成正式季度计划。详见[全年底座要求](../junyi-child-quarterly-intake/references/upstream-requirements.md)。

## 4. 第一次任务怎样提供材料

至少提供以下一项：

- 一个真实事件或任务；
- 一段原始材料、草稿或对话；
- 一份数据、研究记录或已有结论；
- 一个明确目标和不能违反的边界。

建议同时说明：

```text
哪些是事实：
哪些只是我的判断：
哪些信息不能公开：
我希望得到的交付形式：
```

资料不足不等于无法开始。合格的 Skill 应完成可完成部分，把重要缺口标为未知，而不是补写一个顺滑答案。

## 5. 怎样判断结果能不能用

检查五件事：

1. 关键结论是否能回到输入材料；
2. 是否区分事实、推断、假设和未知；
3. 是否写清不适用边界；
4. 是否给出可以执行或验证的下一步；
5. 是否把最终判断和责任留给人。

发现问题时，不要只说“效果不好”。记录：任务、输入类型、哪里失败、人工怎样修改、修改后是否更可用。可以通过[使用反馈模板](https://github.com/junyifei/junyi-skills/issues/new?template=usage-feedback.yml)提交脱敏记录。

## 6. 调用语法为什么不同

- Codex 等支持显式 Skill 提及的环境通常使用 `$junyi`。
- 有些客户端支持 `/junyi` 形式的斜杠命令。
- 不确定时，直接写“使用 junyi 帮我选择最短路径”。

`/` 和 `$` 是客户端交互方式，不是 Skill 方法本身。不要因为某个平台不支持斜杠命令，就判断 Skill 无法使用。

## 7. 更新与本地资料

更新前先备份自己修改过的 Skill 和私有资料。公开仓库不负责保存用户的客户材料、家庭记录、报告、密钥或本地工作台。

版本变化见 [Releases](https://github.com/junyifei/junyi-skills/releases) 和 [`CHANGELOG.md`](../CHANGELOG.md)。
