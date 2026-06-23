# Changelog

本仓库每个 skill 的版本变更记录。版本号写在各 skill `SKILL.md` frontmatter 的 `version` 字段——想更新就重新拉取仓库、覆盖安装，靠 `version` 区分新旧。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。许可见 [LICENSE](LICENSE)（CC BY 4.0）。

---

## junyi-growth-spark-recorder

### [1.0.0] — 2026-06-23
- 首次发布。孩子闪光瞬间三层复盘：📸 记录 → 🔬 发展分析 → 🧠 思维模型复盘，自动归档到 `growth-records/`。
- 内置 62 个思维模型库（芒格多元思维模型 + 儿童发展心理学），全部做了育儿场景落地改写。
- 已去个人化，开箱即用；附 `SETUP.md` 小白安装指南。

---

## junyi-deep-dialogue

### [1.0.0] — 2026-06-23
- 首次发布。苏格拉底式深度对话：通过一轮轮追问帮你想清楚，可选产出一篇完全由你原话构成的觉知日记。

---

## junyi-po-leng-shui

### [1.0.0] — 2026-06-23
- 首次发布。泼冷水反谄媚开关：强制切换魔鬼代言人模式，挑想法的毛病、戳破风险、指出最可能崩的一点，泼完帮你收口（必须改／可不改 + 一句总判断，你拍板）。

---

## junyi-doc-reader

### [1.0.0] — 2026-06-24
- 首次发布。大文档归档检索管线：转换 → 分块 → 可选 LLM 增强，输出结构化 Markdown + 索引存进 Obsidian。支持本地文件（Word/PDF/TXT/Markdown）和飞书云文档，飞书工作日志可按日期拆成 daily notes。
- 基础管线完全离线；飞书凭据仅在用 `--source feishu` 时读取、网络出口仅限官方 API（open.feishu.cn）；LLM 外发默认关闭，需显式设置环境变量开启。
- 纯 Python 标准库实现，无第三方依赖（.docx 需 pandoc、.pdf 需 poppler）。已去个人化，开箱即用。
