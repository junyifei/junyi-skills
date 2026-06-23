# junyi-skills

君一的 Skill 合集

每个文件夹是一个独立的 skill，包含 `SKILL.md`（技能本体）和可选的 `references/`。
拿来即用，已做去个人化处理，任何人都能装。

## 技能列表

### junyi-deep-dialogue · 苏格拉底式深度对话
通过一轮轮追问，帮你在对话中挖掘自己的内在体验和深层认知，最终（可选）产出一篇完全由你原话构成的觉知日记。
适合：情绪强烈但说不清、看完电影或书有余震、在两个选择之间纠结、想从感性体验里提炼认知。
详见 [junyi-deep-dialogue/SKILL.md](junyi-deep-dialogue/SKILL.md)。

### junyi-growth-spark-recorder · 闪光瞬间三层复盘
把家长随手发来的一句观察，变成「记录 → 发展分析 → 思维模型复盘」三层结构，并自动归档成成长编年史。背后是一个 62 个思维模型的库（芒格多元思维 + 儿童发展心理学），用大白话给出"下次可以试"的具体行动。
适合：随手记录孩子的闪光瞬间、想看懂一次亲子互动、复盘冲突或表扬、纠结要不要报班这类教养决策。
详见 [junyi-growth-spark-recorder/SKILL.md](junyi-growth-spark-recorder/SKILL.md)。

### junyi-po-leng-shui · 泼冷水
专治 AI 拍马屁的反谄媚开关。一开它就切到「魔鬼代言人」，不给情绪价值，专挑你想法里的毛病、戳破你没看见的风险、指出最可能崩的那一点；泼完还帮你收口（把问题分成必须改/可不改两堆 + 一句总判断 + 你拍板）。
适合：需求或技术方案 review、产品定价决策、入场某个市场前、跳槽搬家 all in 等重大个人决定、判断一篇稿子值不值得发。
详见 [junyi-po-leng-shui/SKILL.md](junyi-po-leng-shui/SKILL.md)。

## 怎么安装

每个 skill 都遵循 [agentskills.io](https://agentskills.io) 开放标准，Claude Code / OpenClaw / Codex / Hermes / WorkBuddy 都能用。把需要的 skill 文件夹复制进对应平台的 skills 目录即可自动发现，例如装 junyi-po-leng-shui：

```
cp -r junyi-po-leng-shui ~/.claude/skills/           # Claude Code
cp -r junyi-po-leng-shui ~/.openclaw/shared-skills/   # OpenClaw
cp -r junyi-po-leng-shui ~/.agents/skills/           # Codex
cp -r junyi-po-leng-shui ~/.hermes/skills/            # Hermes
cp -r junyi-po-leng-shui ~/.workbuddy/skills/        # WorkBuddy
```

装完重开一个新会话 / 重启 agent 即生效。

**或者让 AI 一键装**——不想手动复制的话，把下面这段整段发给对方的 agent（任何工具通用）：

> 帮我从 https://github.com/junyifei/junyi-skills 装一个 skill，只装 `junyi-growth-spark-recorder` 这一个（换成你要的那个）。请把仓库克隆到临时目录，只把这个文件夹复制到你这个工具的 skills 目录——Claude Code `~/.claude/skills/`、OpenClaw `~/.openclaw/shared-skills/`、Codex `~/.agents/skills/`、Hermes `~/.hermes/skills/`、WorkBuddy `~/.workbuddy/skills/`，你是哪个就放哪个——再删掉临时克隆、别留下仓库里其它 skill。装好后读一下它的 SKILL.md，告诉我用什么话触发。

## 许可

本仓库的文字内容（各 skill 的 `SKILL.md` 与 `references/`）采用 [CC BY 4.0（署名 4.0 国际）](https://creativecommons.org/licenses/by/4.0/) 许可：可自由使用、修改、再分发（含商用），前提是署名「君一」。许可全文见 [LICENSE](LICENSE)。

## 关于

作者：君一
