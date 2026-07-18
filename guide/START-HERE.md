# 君一方法论新手指南

这份指南帮助第一次使用的人完成三件事：安装、选择入口、完成第一次真实任务。

## 1. 先选择安装范围

### 安装全部公开 Skills

适合希望使用总入口，让 Agent 自动选择路径的人：

```bash
npx -y skills add junyifei/junyi-skills -g --all
```

### 先查看，不安装

```bash
npx -y skills add junyifei/junyi-skills --list
```

### 只安装一个 Skill

```bash
npx -y skills add junyifei/junyi-skills -g --skill junyi-positioning -y
```

安装工具会根据 Agent 选择实际目录。需要手动安装时，把整个 Skill 文件夹复制到当前 Agent 支持的 skills 目录；不要只复制 `SKILL.md`，否则 references、scripts 和 assets 可能缺失。

安装后开启一个新会话，让 Agent 重新发现 Skills。

## 2. 不知道从哪里开始

使用总入口：

```text
$junyi
我现在要完成的是：……
我已经有的真实材料是：……
我最担心 Agent 编造或误判的是：……
```

`junyi` 只负责判断最短路径，不代替下游 Skill 完成所有工作。

## 3. 已经知道任务时直接调用

| 现在要做什么 | 直接使用 |
|---|---|
| 通过追问想清楚体验、矛盾或选择 | `$junyi-deep-dialogue` |
| 明确要求挑刺、找漏洞或魔鬼代言人 | `$junyi-po-leng-shui` |
| 转换、分块、索引或归档大文档 | `$junyi-doc-reader` |
| 记录孩子的具体片段并复盘 | `$junyi-growth-spark-recorder` |
| 设计、审核或迭代个人 IP 定位 | `$junyi-positioning` |
| 发现并核验小红书对标 | `$junyi-xhs-benchmark` |

不要为了看起来完整而从第一步重跑。已有草稿、材料或决定时，直接从当前缺失的一层开始。

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
