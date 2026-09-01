# 兼容性与安装说明

最后核验：2026-09-01（`wechat-article-writer` 1.0.0 候选；结构、安全、三端隔离发现和三轮真实写作客观门禁已通过。补入脱敏的“人物主线与系统线”通用编辑决策后，第一轮第四次复评由公开候选版胜出；结合已经胜出的第二、第三轮，三轮主观门禁全部通过。GitHub v1.8.0 尚待发布，作者生产入口尚待独立切换与回退复跑）。

> 不想敲命令行？装 Skill 的大白话版见 [README 的「安装」](../README.md#安装)和[新手指南](START-HERE.md)。这份文档是给需要**精确命令**、排查 Agent 兼容性或做手动安装的人。

## 已验证范围

| 项目 | 状态 | 核验结果 |
|---|---|---|
| 仓库自动发现 | 已验证 | `skills` CLI 能发现 22 个（21 个 Skill + 1 个「君一 Skills 导航」，技术名称 `junyi`）|
| Codex 项目级复制安装 | 已验证 | 隔离目录中安装 22/22，`SKILL.md` 与资源目录完整 |
| `wechat-article-writer` 1.0.0 | 客观与三轮主观门禁通过；待发布、待切换 | 结构、安全、三端隔离发现、无配置、模拟创作者、三轮真实写作客观门禁和回退复跑均通过；第二、第三轮公开候选版已胜出，第一轮在补入脱敏通用编辑决策后第四次复评也由公开候选版胜出。GitHub v1.8.0 发布和作者生产入口切换仍分别待验收。详见[候选验收记录](WECHAT-ARTICLE-WRITER-VALIDATION.md) |
| `junyi-relationship-manager` 1.1.0 | 已验证 | 隔离安装包含 SKILL、agents、assets、references 与校验脚本；3 组独立前向情境和 6 项脚本自检通过 |
| Codex 显式调用 | 已验证 | 支持 `$skill-name` 与自然语言指定 Skill |
| GitHub Copilot 目录发现 | 部分验证 | 安装工具识别共享 `.agents/skills`，未完成独立任务回归 |
| Claude Code | 隔离发现已验证 | 项目级复制安装和独立新会话发现通过；作者生产入口继续保持冻结旧版 |
| OpenClaw | 隔离发现已验证 | 工作区级精确加载只发现一个同名 Skill，资源完整；作者生产入口未切换 |
| WorkBuddy、豆包等其他 Agent | 待验证 | 不在 README 中承诺已经支持 |

“结构兼容”只表示包含标准 `SKILL.md` 及可选 resources，不等于相关客户端的安装、触发、脚本权限和输出都已经验证。

## 自动发现

```bash
npx -y skills add junyifei/junyi-skills --list
```

期望发现：

```text
junyi
junyi-ai-weekly-review
wechat-article-writer
junyi-content-distiller
junyi-deep-dialogue
junyi-doc-reader
junyi-growth-spark-recorder
junyi-learning-distiller
junyi-personal-website
junyi-po-leng-shui
junyi-positioning
junyi-relationship-manager
junyi-vault
junyi-xhs-benchmark
junyi-child-annual-intake
junyi-infant-annual-plan
junyi-preschool-annual-plan
junyi-school-age-annual-plan
junyi-child-quarterly-intake
junyi-infant-quarterly-plan
junyi-preschool-quarterly-plan
junyi-school-age-quarterly-plan
```

## Codex 项目级安装

在希望使用 Skills 的项目目录执行：

```bash
npx -y skills add junyifei/junyi-skills --agent codex --skill '*' -y --copy
```

隔离测试中，文件被复制到项目的 `.agents/skills/`。实际位置可能随安装工具和 Agent 版本变化，应以命令输出为准。

## 全局安装

```bash
npx -y skills add junyifei/junyi-skills -g --all
```

全局安装会向工具识别出的 Agent 写入 Skills。执行前先查看命令输出和目标目录；如果已有同名 Skill，先备份本地修改。

## 手动安装

复制完整文件夹，不要只复制 `SKILL.md`：

```bash
mkdir -p .agents/skills
cp -R junyi .agents/skills/
cp -R junyi-positioning .agents/skills/
```

有些 Skill 依赖 `references/`、`scripts/` 或 `assets/`。缺少这些目录时，Skill 可能能被发现但无法完整执行。

## 调用方式

| 环境能力 | 推荐写法 |
|---|---|
| 支持显式 Skill 提及 | `$junyi-positioning` |
| 支持斜杠命令并已注册 | `/junyi-positioning` |
| 不确定客户端能力 | `使用 junyi-positioning，帮我……` |

README 不把 `/skill` 宣称为所有 Agent 的统一原生命令。

## 报告兼容性问题

请使用[问题模板](https://github.com/junyifei/junyi-skills/issues/new?template=problem.yml)，提供：Agent 名称与版本、安装方式、Skill 名称、期望行为、实际行为和可公开的错误信息。不要提交账号凭据、私有路径或客户材料。
