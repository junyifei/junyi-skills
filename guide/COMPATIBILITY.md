# 兼容性与安装说明

最后核验：2026-07-18。

## 已验证范围

| 项目 | 状态 | 核验结果 |
|---|---|---|
| 仓库自动发现 | 已验证 | `skills` CLI 能发现 7 个公开 Skills |
| Codex 项目级复制安装 | 已验证 | 隔离目录中安装 7/7，`SKILL.md` 与资源目录完整 |
| Codex 显式调用 | 已验证 | 支持 `$skill-name` 与自然语言指定 Skill |
| GitHub Copilot 目录发现 | 部分验证 | 安装工具识别共享 `.agents/skills`，未完成独立任务回归 |
| Claude Code | 结构兼容，待回归 | 尚未完成本版本的独立端到端测试 |
| OpenClaw | 结构兼容，待回归 | 尚未完成本版本的独立端到端测试 |
| WorkBuddy、豆包等其他 Agent | 待验证 | 不在 README 中承诺已经支持 |

“结构兼容”只表示包含标准 `SKILL.md` 及可选 resources，不等于相关客户端的安装、触发、脚本权限和输出都已经验证。

## 自动发现

```bash
npx -y skills add junyifei/junyi-skills --list
```

期望发现：

```text
junyi
junyi-deep-dialogue
junyi-doc-reader
junyi-growth-spark-recorder
junyi-po-leng-shui
junyi-positioning
junyi-xhs-benchmark
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
