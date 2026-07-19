# 长录音工作流

## 目录

- [任务目录](#任务目录)
- [清单与状态](#清单与状态)
- [说话人映射](#说话人映射)
- [人名映射](#人名映射)
- [分块与单块蒸馏](#分块与单块蒸馏)
- [会话隔离](#会话隔离)
- [合并](#合并)
- [机械验收](#机械验收)
- [断点恢复](#断点恢复)

## 任务目录

在用户指定的工作目录下建立独立任务目录；未指定时使用当前目录下的 `.junyi-content-distiller/<日期或任务名>/`：

```text
任务目录/
├── raw/                 # 原始输入副本，不写 AI 摘要
├── chunks/              # chunk_001.md 与 chunk_001.distilled.md
├── speakers.md          # 分段说话人映射及依据
├── names.md             # 可选：用户确认的人名变体与待确认项
├── unconfirmed-names.md # 可选：表外疑似人名及原文证据
├── manifest.json        # 断点状态
└── final.md             # 验收通过的最终稿
```

不得覆盖用户原文件。原始副本与中间产物必须实际存在，不能只保留在对话上下文。

## 清单与状态

manifest 至少记录：

- 来源路径、大小、事件日期和时间范围；
- chunk 路径、字符数、覆盖时间、状态和对应 `.distilled.md`；
- `pending / distilled / merged / skipped` 状态；
- skipped 的明确原因；
- 是否需要隔离执行、采用的隔离模式，以及主会话是否读取过原始 chunk；
- 每个完成 chunk 的 worker/run 标识和执行模式；
- 最终文件路径和验收结果。

只有所有应处理 chunk 都为 `distilled` 或有理由的 `skipped`，才能合并。

## 说话人映射

在分块蒸馏前创建：

```markdown
| 分段/文件 | 原始编号 | 身份 | 依据 | 状态 |
|---|---|---|---|---|
| 上午段 | 说话人 1 | A | 开场自报姓名 | 已确认 |
| 下午段 | 说话人 1 | [未确认说话人] | 只有口吻相似 | 未确认 |
```

说话人编号可能在每个文件或录音段重新编号。映射必须以“分段/文件”为作用域，不能跨段继承。

## 人名映射

只有用户提供或确认过映射时，才创建 `names.md`：

```markdown
| 正式姓名 | 别名/转写变体 | 依据 | 状态 |
|---|---|---|---|
| A | 阿A、转写变体 | 用户确认 | 已确认 |
```

- 映射用于参与者标签、索引和分析说明，不静默改写 `📎 原话`。
- 变体撞名、数字连读或无法消歧时保持未知。
- 表外疑似人名写入 `unconfirmed-names.md`，记录疑似词、原文上下文和证据位置；等待用户确认，不自动修改知识库或人物档案。

## 分块与单块蒸馏

运行：

```bash
python3 scripts/split_recording_md.py raw/transcript.md --out-dir chunks --max-chars 8000
```

脚本会创建 chunk 和 manifest。每次只读取：当前 chunk、对应说话人映射、`extraction-rules.md` 和 `output-contract.md`。

单块完成后立即写 `chunk_NNN.distilled.md` 并把 manifest 状态改为 `distilled`。不要等所有 chunk 做完后才保存。

## 会话隔离

### 少于 3 个 chunk

主会话可以逐块处理，但每次只打开一个 chunk，产物立即落盘，不把多个原文同时放入提示或回复。

### 不少于 3 个 chunk：强制隔离

“一次只读一个”不等于隔离；同一主会话依次读取多个 chunk 仍会累计上下文。此时必须执行：

1. 主会话只建立 manifest、原始副本、chunks、`speakers.md` 和可选 `names.md`。
2. 每个 chunk 交给独立 sub-agent/worker 或新的空白会话。每个执行上下文只获得：单个 chunk 路径、该段说话人映射、人名映射、提取规则、输出契约和目标 `.distilled.md` 路径。
3. worker 直接写产物文件，只返回状态、产物路径和待确认项；不要把 chunk 原文或完整蒸馏稿回传给主会话。
4. 主会话记录每个 chunk 的 `worker_mode` 和非空 `worker_run`，但禁止打开 `chunk_NNN.md`。
5. 所有产物完成后，主会话运行确定性合并脚本；脚本只读取 `.distilled.md`。

manifest 顶层必须记录：

```json
{
  "isolation": {
    "required": true,
    "threshold": 3,
    "mode": "isolated-worker",
    "orchestrator_read_raw_chunks": false
  }
}
```

`mode` 只能是 `isolated-worker` 或 `fresh-session`。每个非跳过 chunk 记录相同范围内的 `worker_mode` 与可审计的 `worker_run` 标识。

如果当前平台没有 sub-agent、worker 或启动新空白会话的能力，完成分块和 manifest 后停止，交付状态写 `prepared_for_isolated_processing`。不得为了省一次调度而让主会话继续读取原文。

## 合并

运行：

```bash
python3 scripts/merge_chunks.py chunks final.md --title "内容蒸馏 · YYYY-MM-DD" --source "原始文件名" --manifest chunks/manifest.json
```

合并规则：

- 按“今日核心事件→情绪地图→故事→观点→金句→场景→冲突→数据案例→决策原则→工作待办安排”归并；
- 每个栏目只出现一次；
- 类别内保持 chunk 和原文时间顺序并重新编号；
- 以标题和证据位置去除明显重复，保留证据更完整的版本；
- 收集所有 chunk 待办表，只在最后输出一张表；
- 修复必须重新读取原始 `.distilled.md`，不在旧 `final.md` 上反复做减法。

## 机械验收

运行：

```bash
python3 scripts/validate_distillation.py final.md --manifest chunks/manifest.json
```

验收至少覆盖：

- 原始文件和 chunk 文件存在；
- chunk 数量与 manifest 一致；
- 没有未说明的 `pending`；
- 所有应处理 chunk 都存在 `.distilled.md`；
- chunk 不少于 3 时，isolation 契约完整，每个非跳过 chunk 都有隔离执行记录；
- 栏目顺序正确且不重复；
- 素材条目都有证据位置和原话；
- 待办表只在最后栏目出现；
- 没有“说话人 N”残留被当成已确认姓名；
- 没有 U+FFFD 乱码。

## 断点恢复

中断后先读取 manifest：

1. 核对原始副本和已有 chunk 是否仍存在。
2. 跳过已完成且文件有效的 `distilled` chunk。
3. 从第一个无说明的 `pending` 继续。
4. 隔离模式下仍由新 worker/空白会话继续；主会话不得因为恢复任务而读取 pending chunk。
5. 如果分类规则或输出契约发生变化，明确标记需要重新蒸馏的 chunk，不混合两个版本的中间产物。
6. 最终合并通过后，将参与合并的 chunk 标记为 `merged`，并记录验证时间。
