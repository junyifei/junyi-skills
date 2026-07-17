# 君一方法论

把真实经验蒸馏成可调用、可验证、可迭代的 Skill。

`junyi-skills` 不是提示词陈列柜。每个正式 Skill 都要回答四个问题：什么任务触发、需要什么证据、按什么流程做、怎样判断结果可信。尚未形成稳定流程的内容先保留为知识，不为了数量硬包装成 Skill。

当前版本：**0.1.1** · 正式入口与 Skill：**7 个**

## 从这里开始

不知道该用哪个 Skill 时，显式调用：

```text
/junyi 我现在想做的事是……我手上已有的材料是……
```

在支持 `$skill-name` 的工具中也可以写：

```text
$junyi 帮我选择最短路径，不要让我重跑已经完成的步骤。
```

总入口只做诊断与路由，随后把任务交给职责最明确的 Skill。详见 [`junyi/SKILL.md`](junyi/SKILL.md)。

## 产品结构

```text
真实问题与真实材料
        ↓
junyi 总入口：判断目标、证据与当前阶段
        ↓
单个 Skill 或最短调用链
        ↓
可追溯产出 → 人工判断 → 真实反馈
        ↓
修订方法、案例和质量门
```

仓库内有四层：

- `junyi/`：总入口，只负责路由。
- `<skill-name>/`：可独立安装、具有明确任务边界的正式 Skill。
- `knowledge/`：尚未蒸馏成 Skill 的知识卡与待验证方法。
- `tools/`：资产盘点和仓库维护工具，不是用户 Skill。

机器可读清单见 [`skill-index.json`](skill-index.json)，方法成熟度与版本不会写进 `SKILL.md` frontmatter，以保持跨平台兼容。

## 基础方法能力

| Skill | 用途 | 成熟度 |
|---|---|---|
| [`junyi-deep-dialogue`](junyi-deep-dialogue/SKILL.md) | 通过苏格拉底式追问把体验变成自己的判断 | 已发布 |
| [`junyi-po-leng-shui`](junyi-po-leng-shui/SKILL.md) | 只有用户明确说“泼冷水、挑刺”等触发词时，才启动魔鬼代言人评审 | 已发布 |
| [`junyi-growth-spark-recorder`](junyi-growth-spark-recorder/SKILL.md) | 把亲子片段变成记录、发展分析与模型复盘 | 已发布 |
| [`junyi-doc-reader`](junyi-doc-reader/SKILL.md) | 转换、分块、索引并归档大文档 | 已发布 |

## 证据型个人 IP 能力链

| 阶段 | Skill | 作用 | 当前成熟度 |
|---|---|---|---|
| 战略定位 | [`build-evidence-based-ip-book`](build-evidence-based-ip-book/SKILL.md) | 定位诊断；建立、审核和迭代证据型 IP 战略书 | 已投入项目 |
| 对标研究 | [`find-xiaohongshu-benchmarks`](find-xiaohongshu-benchmarks/SKILL.md) | 发现、核验、分层和选择对标样本 | 测试中 |

这里公开的是目前愿意承担方法承诺的能力。用户研究、选题、标题、内容生产与审核等方法仍在本地实盘验证，跑通并积累可说明的证据后再发布。

## 方法论原则

- **真实证据先于漂亮结论**：事实、推断、假设和未知分开。
- **一项职责一个入口**：新写与审核、研究与选题不混在同一个 Skill。
- **先候选，再晋升**：反复有效、有边界、可复用，才升级为正式方法。
- **不替用户编故事**：不把外部案例冒充个人经历，不制造不存在的效果。
- **结果进入反馈环**：好结果、差结果和人工修改都用于下一版本校准。

## 安装

复制整个仓库，或只复制需要的 Skill 目录到你使用的 Agent 的 skills 目录。以 Codex 为例：

```bash
cp -R junyi ~/.codex/skills/
cp -R build-evidence-based-ip-book ~/.codex/skills/
cp -R find-xiaohongshu-benchmarks ~/.codex/skills/
```

不同工具的目录可能不同；安装前先检查是否存在同名目录，避免覆盖本地未同步的修改。安装后开启新会话，让工具重新发现 Skill。

## 原创与许可

本仓库是君一基于自己的实战、记录、课程、咨询和内容项目独立蒸馏的方法论实现，不复制第三方项目的具体文案、代码、视觉资产或品牌表达。

本仓库采用 [CC BY 4.0](LICENSE)：可以使用、修改和再分发，包括商业使用；请署名“君一”并保留许可链接。权利与迁移记录见 [`RIGHTS.md`](RIGHTS.md)。

## 作者

君一 · 费君一
