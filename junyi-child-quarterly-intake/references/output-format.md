# `quarterly-update.md` 输出契约

版本：`junyi-child-quarterly-update/v1`

只生成一个 Markdown 文件。使用 YAML frontmatter 提供最少机器路由字段，正文保留家长和 Agent 都能复核的证据。

## 完整模板

```markdown
---
schema_version: junyi-child-quarterly-update/v1
status: ready
plan_track: preschool
quarter_start: 2026-07-01
quarter_end: 2026-09-30
as_of: 2026-06-28
child_id: CHILD-001
age_months: 52
annual_plan_as_of: 2026-01-15
previous_plan_status: provided
child_voice_status: direct-simple
track_transition: false
evidence_count: 3
context_count: 2
---

# CHILD-001 季度更新资料

## 1. 季度变化与执行复盘

### 上一季度实际执行

- 原计划：
- 实际做了：
- 没有做及原因：

### 效果、代价与保留调整

- 有效：
- 无效或代价过高：
- 保留：
- 调整：
- 停止：

### 未来 90 天家庭优先情境

- 想改善的真实生活情境：
- 如果无需解决问题，最想保护或观察的自然发展：
- 为什么是现在：
- 不愿牺牲的底线：

### 家庭执行条件

- 主要陪伴者及时间：
- 主要陪伴者的优势与孩子现有互动方式：
- 忙碌周最低投入：
- 必须保留的纯陪伴：
- 已稳定存在的习惯与资源：
- 新资源：
- 限制与尚未确认事项：
- 未来 90 天重要节点：

### 孩子的声音或行为信号

- 直接原话或行为：
- 取得方式：
- 仍待确认的成人目标：

## 2. 证据与来源

### Q01
- 类型：惊喜事件
- 大概时间：2026-05
- 场景：家庭共同游戏
- 事实或原话：
- 成人回应：
- 结果：
- 来源：家长
- 解释：none
- 置信度：medium
- 未知：具体日期

### Q02
...

### Q03
...

## 3. 资料完整性与未知

### 已达到的主题

- [x] 全年知识底座
- [x] 上季度执行与效果
- [x] 三个具体事件、至少两个情境
- [x] 符合年龄要求的孩子声音或行为信号
- [x] 家庭优先情境与底线
- [x] 家庭实际投入和最低版本
- [x] 资源变化与重要节点
- [x] 安全检查

### 关键未知

- none

### 资料矛盾

- none

### 证据限制

- 单次事件不代表稳定特质。

### 更正记录

- none

## 4. 月龄路由与交接结果

- 季度开始完整月龄：52
- 当前轨道：preschool
- 全年底座轨道：infant
- 是否发生轨道过渡：是；旧全年规划作为历史知识继续保留
- 交接状态：ready
- 下游 Skill：junyi-preschool-quarterly-plan
```

## Frontmatter 规则

| 字段 | 允许值或格式 |
|---|---|
| `schema_version` | 固定 `junyi-child-quarterly-update/v1` |
| `status` | `ready`、`needs-observation`、`blocked-safety`、`blocked-upstream` |
| `plan_track` | `infant`、`preschool`、`school-age` |
| `quarter_start`、`quarter_end`、`as_of` | `YYYY-MM-DD` |
| `child_id` | 匿名代号，不是真实姓名或昵称 |
| `age_months` | 季度开始日的完整月龄 |
| `annual_plan_as_of` | `YYYY-MM-DD`；缺失时写 `unknown` 并将状态设为 `blocked-upstream` |
| `previous_plan_status` | `provided`、`first-cycle`、`unavailable` |
| `child_voice_status` | `behavioral`、`direct`、`direct-simple`、`direct-reflection`、`unavailable` |
| `track_transition` | `true` 或 `false` |
| `evidence_count` | 证据事件数量 |
| `context_count` | 去重后的生活情境数量 |

`Q1` 与 `Q01` 都是合法编号，但同一文件内保持一种格式。`evidence_count` 只统计具体事件；模糊评价和没有事件要素的整体印象放在第 1、3 节，不建立 `Qxx`。`status: ready` 的每个事件必须填写非空“事实或原话”和已知“来源”，不能用“空、unknown、none、待补充、未提供”占位。

## 非 `ready` 状态的附加结构

### `needs-observation`

在第 3 节之后、第 4 节之前增加：

```markdown
## 7—14 天预备观察方案

### 要观察的场景
### 每次只记录什么
### 临时支持动作
### 忙碌日最低版本
### 复盘日期与升级条件
```

并将第 4 节交接状态写成 `needs-observation`，不得写入正式季度报告下游 Skill。

### `blocked-safety`

保留安全相关事实、实际来源、未知和当地升级提示。不要继续形成一般发展方向或行动计划。

### `blocked-upstream`

明确缺少的全年底座或路由信息，并给出 `junyi-child-annual-intake` 及相应年度报告 Skill 的补齐顺序。

## 更正规则

不能直接覆盖已经确认的 `Qxx` 事实。使用：

```markdown
- YYYY-MM-DD｜更正 Q02｜原内容：……｜修正为：……｜来源：……｜对季度判断的影响：……
```
