---
name: junyi-ai-weekly-review
description: AI 周度复盘。把你这一周和各个 AI agent 的日常协作记录，自动收集、清洗、按天蒸馏，沉淀成《本周记录》（给自己看的事实底账加复盘）和《本周内容素材》（能直接写成内容的片段）两份本地产出，每条都标原始出处。一周跑一次、抓过去 7 天，只在本地跑、本地存、不外发。内置 Claude Code、OpenClaw、Codex 适配器（已验证）与 custom 兜底（Hermes、WorkBuddy 为占位待验证）。需要本机装 Node.js。触发词：AI周度复盘、周报、本周AI复盘、本周和AI干了什么、ai weekly review、复盘这周的AI对话。
---

# AI 周度复盘 · junyi-ai-weekly-review

> 一句话：你这一周和 AI 聊过、干过的事，自动汇成一份周报 + 一份能写的素材，不用你手动翻记录。

**做什么**
把你这一周和各个 AI agent 的日常协作记录自动收集、清洗、按天蒸馏，沉淀成两份产出：《本周记录》（给本人看的事实底账 + 复盘）+《本周内容素材》（给写作 / 做内容用）。只在本地跑、本地存，不外发。

**什么时候用**
一周结束想复盘"这周和 AI 都干了什么、沉淀下哪些方法 / 判断 / 工具想法"，或想把一周对话里能写的料捞出来时。一周跑一次，抓过去 7 天。
触发词：AI周度复盘、周报、本周AI复盘、本周和AI干了什么、ai weekly review、复盘这周的AI对话

**用完得到什么**
两份本地 Markdown——《本周记录》（各 agent 本周工作 + 多天反复印证的方法 / 判断 + 本周新增）和《本周内容素材》（能直接写成内容的片段），每条都标原始出处。

## 适配器状态（诚实标注，2026-06-25 落地真机探测）

| 适配器 | 状态 | 本机验证 | 存储路径 / 格式 |
|--------|------|----------|----------------|
| **Claude Code** | ✅ 支持 | ✅ 已验证（真实数据跑通） | `~/.claude/projects/**/*.jsonl`，`type∈{user,assistant}`，文本在 `message.content`（string 或 block list）。排除 `claude-mem-observer`。 |
| **OpenClaw** | ✅ 支持 | ✅ 已验证（多 agent 跑通） | `~/.openclaw/agents/<agentId>/sessions/*.jsonl`，`type==="message"`，role/content 在 `message.*`，user 消息清洗元数据噪音。 |
| **Codex CLI** | ✅ 支持 | ✅ 已验证（落地时现场探测确认） | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`，行结构 `{timestamp,type,payload}`，`type==="response_item"`且`payload.type==="message"`，role 在 `payload.role`，文本在 `payload.content[].text`。丢 developer 角色 + `<environment_context>`/compaction 等注入块。 |
| **Hermes** | ⚠️ 未支持 | ❌ **未经真机验证** | 落地机器**未探测到** Hermes 本地会话存储（探测过 `~/.hermes`、`~/Library/Application Support/Hermes` 等候选，均无）。无样本，未写解析。要用请走 **custom** 适配器，或在 `adapters/hermes.mjs` 按真实格式补全后再标已验证。 |
| **WorkBuddy** | ⚠️ 未支持 | ❌ **未经真机验证** | 落地机器**完全未发现** WorkBuddy 痕迹。同 Hermes，走 custom 或补全 `adapters/workbuddy.mjs`。 |
| **custom（兜底）** | ✅ 支持 | 通用字段推断 | `--custom-path <文件/目录>`，自动推断常见字段（role/content/timestamp）。推断不出会如实报错，不伪造。 |

> 🔴 **未验证适配器首次使用请检查路径 / 字段**：标 ⚠️ 的适配器没在你的机器上用真实数据跑通过，第一次用时务必核对它探测的路径对不对、字段解析对不对，不要假设都测过了。
> 🔴 **落地铁律**：对未知来源，先 `ls` / 读样本确认真实格式再写解析，禁止凭想象写死路径；探测不到就标 `unsupported` 并在产出里如实说「未找到 XX 的记录」，不伪造数据。

---

## 执行流程（6 步）

### Step 0　确定时间窗口
默认过去 7 天（本地时区）。可传参覆盖。

### Step 1　抓取 + 标准化 + 分块（纯脚本，不调模型）

```bash
cd scripts                             # 进入本 skill 的 scripts 目录
node collect.mjs                       # 默认过去 7 天，输出到 ./ai-weekly-review-output
# 指定窗口:  node collect.mjs --since 2026-06-19 --until 2026-06-25
# 指定输出:  node collect.mjs --out ~/周报
# 只跑某些源: node collect.mjs --adapters claude_code,openclaw,codex
# 别的工具:  node collect.mjs --custom-path ~/导出/我的对话.jsonl
```

脚本自动完成（复用成熟逻辑）：跑 5 内置适配器（+ custom）归一成统一记录 → 只留真实对话（user/assistant）→ 去工具独白 → 去 OpenClaw 元数据噪音 → 自指排除（本 skill 自己的蒸馏 session 不被再蒸馏）→ 跨源去重（`sha256(role+content)`）→ 超长截断（>2000 字保留来源指针）→ **按天分组**，每天内按 `源>agent>session>时间` 分块（≤10000 字）。

产出在 `<out>/<YYYY-Wxx>/`：
- `manifest.md`：窗口 / **适配器报告（哪些命中、哪些 unsupported、各源记录数）** / 各 agent 记录数 / 各天 chunk 数
- `adapters-report.json`：机器可读的适配器命中情况
- `records.cleaned.jsonl`：清洗去重后的统一记录
- `days/<YYYY-MM-DD>/chunk_NNN.md`：逐日 chunk

脚本打印 JSON 摘要。**status=empty-week** → 跳到 Step 5 出空周报，如实说明扫描范围。

### Step 2　逐日蒸馏（按天，保颗粒度）
读 `references/distill-rules.md`。**不要 7 天揉一坨**：对 `days/<date>/` 每天的 chunk 逐日蒸馏（7 天 = 7 次），每次只面对一天，抽三类候选：**方法工作流 / 判断原则 / 工具想法**。chunk 多时可派 sub-agent 批量蒸馏省上下文。

### Step 3　汇周（去重 + 印证）
7 份日级结果合并：同一条判断 / 方法多天反复出现 → **不重复列**，合并成一条标「本周印证 N 次」；印证越多越值得固化，置顶 / 高亮。单次出现 → 列入「本周新增」。

### Step 4　多 agent 工作概览（按需）
看 `manifest.md` 的「各 agent 记录数」：>1 个 agent → 出《本周记录》的「各 agent 本周工作」一节（各 agent 这周做了啥 / 产出 / 卡点）；只有 1 个 agent → **自动省略本节**，不搭空架子。

### Step 5　生成两份 Markdown
读 `references/output-templates.md`，按模板出《本周记录》+《本周内容素材》，写到 `<out>/<YYYY-Wxx>/`。

### Step 6　自检
破折号（——）0 处 / 横线（━）0 处 / 无乱码 U+FFFD / **每条都有原始出处**（record_id 前 8 位 / chunk 号 / 日期）。看不准的标 `[此处不确定]`，宁缺毋假。输出最终路径。

---

## 排版规范（产出文件）

- 大类标题用中文序号或清晰 Markdown 标题，不堆 `━━━` 横线。
- 🔴 全文禁用破折号（——），用逗号 / 句号 / 括号代替。
- 引号用中文弯引号「」或 “ ”。

## 安全 / 隐私

- 原始聊天记录只留本机，产出只写本地，不外发。
- 金额 / token / 密钥 / 账号一律不进正文。
- 人名可保留，但提醒用户：要对外发布的内容素材需自行脱敏。
- 不自动改用户任何配置 / 人格文件，不自动建 skill，只产 Markdown。

## 兜底：内置都没命中时

若某来源没找到文件、或用户用的是别的工具：
1. 问用户「你的 AI 对话记录在哪？是导出文件还是某工具的本地存储？」
2. 给到路径 → `node collect.mjs --custom-path <路径>`（custom 适配器自动推断字段）。
3. 还是推断不出 → 如实说「这个来源暂不支持，需要你手动整理成 {role, timestamp, content} 的 jsonl」。

## 目录结构

```
junyi-ai-weekly-review/
├── SKILL.md
├── scripts/
│   ├── collect.mjs            # 抓取+标准化+按天分块（Step 1-3）
│   ├── lib.mjs                # 共享工具（时间/提取/清洗/自指排除/扫描）
│   └── adapters/
│       ├── claude-code.mjs    # ✅ 已验证
│       ├── openclaw.mjs       # ✅ 已验证
│       ├── codex.mjs          # ✅ 已验证（现场探测）
│       ├── hermes.mjs         # ⚠️ unsupported（未探测到存储）
│       ├── workbuddy.mjs      # ⚠️ unsupported（未探测到存储）
│       └── custom.mjs         # 兜底：自带路径 + 字段推断
└── references/
    ├── distill-rules.md       # 三类候选 + 三段式写法 + 汇周去重印证
    └── output-templates.md    # 两份产出模板
```

> 抓取脚本用 Node 运行（`node scripts/collect.mjs`），需要本机装有 Node.js，无需其他额外依赖。
