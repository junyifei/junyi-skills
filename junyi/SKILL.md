---
name: junyi
description: 君一方法论总入口。仅在用户显式调用 /junyi、$junyi、君一方法论，或明确要求“帮我选择君一的哪个 Skill/从哪里开始”时使用。识别用户当前任务、已有证据、目标平台与所处阶段，路由到仓库中最合适的一个 Skill 或最短调用链；它不代替下游 Skill 执行，也不在证据不足时编造经历、案例、用户洞察或平台数据。
---

# 君一方法论

从真实问题开始，选择最短有效路径。一次只解决当前最关键的一层。

## 路由流程

1. 用用户已经提供的信息判断：他要想清楚、做决策、整理材料、记录成长，还是打造与运营个人 IP。
2. 检查输入是否足够：真实事件、原话、草稿、数据、研究材料或明确目标至少要有一种。
3. 优先选择一个 Skill。只有上一步的产出确实是下一步的必要输入时，才组合多个 Skill。
4. 告诉用户选择了哪个 Skill、为什么、还缺什么关键输入。
5. 调用所选 Skill，并严格遵循它自己的边界、步骤和质量门。不要在本入口内模拟下游流程。

## 路由表

### 思考、判断与知识处理

| 用户现在要做什么 | 路由 |
|---|---|
| 通过追问想清楚体验、情绪、矛盾或选择 | `junyi-deep-dialogue` |
| 主动要求挑刺、找漏洞、做魔鬼代言人评审 | `junyi-po-leng-shui` |
| 记录孩子的具体片段并做发展与模型复盘 | `junyi-growth-spark-recorder` |
| 转换、分块、索引或归档大文档 | `junyi-doc-reader` |

### 证据型个人 IP

| 用户现在要做什么 | 路由 |
|---|---|
| 定位诊断、战略书、商业与内容验证设计 | `build-evidence-based-ip-book` |
| 研究目标用户的真实问题、语言、付费与任务 | `research-audience-insights` |
| 找小红书对标账号、样本和爆款标本 | `find-xiaohongshu-benchmarks` |
| 根据上游证据生成、筛选和排序小红书选题 | `plan-xiaohongshu-topics` |
| 生成小红书封面文案与标题 | `write-xiaohongshu-titles` |
| 生成视频号封面文案与发布标题 | `write-wechat-channels-titles` |
| 从真实素材新写小红书内容 | `write-xiaohongshu-content` |
| 审核并改写已有小红书草稿 | `audit-xiaohongshu-content` |
| 从真实素材新写视频号内容 | `write-wechat-channels-content` |
| 审核并改写已有视频号草稿 | `audit-wechat-channels-content` |

## 最短调用链

- 已有草稿，只想改好：直接走对应平台的 `audit-*`，不要先重做定位。
- 已有真实素材，只缺标题：直接走对应平台的 `write-*-titles`。
- 已有清晰定位和用户证据，要持续生产：`plan-xiaohongshu-topics` → 对应平台的 `write-*` → `audit-*`。
- 从零建立个人 IP：`build-evidence-based-ip-book` → `research-audience-insights` → 必要时 `find-xiaohongshu-benchmarks` → 选题、创作、审核。
- 对一个重大方向既想看见自己又想防止自欺：先 `junyi-deep-dialogue`，形成明确判断后，仅在用户显式要求时再调用 `junyi-po-leng-shui`。
- 已有一个亲子片段，只想记录与复盘：直接走 `junyi-growth-spark-recorder`。

## 证据门

将事实、推断、假设和未知分开：

- 有真实材料：保留出处、原话与不确定性。
- 只有方向：先索取一个最小真实样本，或把产出明确标为待验证假设。
- 缺少平台、目标、受众或交付形式且会改变路由：只问最关键的一个问题。
- 不得把外部案例改写成用户经历，不得用流行表达冒充用户洞察，不得承诺未经验证的传播结果。

## 边界

- 本 Skill 是路由器，不是“万能生成器”。
- 不因为完整链路看起来专业，就强迫用户从第一步重跑。
- 不同时调用职责重叠的 Skill。
- 不自动发布内容、写入外部系统或替用户作最终决策。
