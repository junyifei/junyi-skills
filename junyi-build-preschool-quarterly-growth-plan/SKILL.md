---
name: junyi-build-preschool-quarterly-growth-plan
description: 为季度开始日完整月龄 36—71 个月的学前儿童生成未来 90 天个性化成长计划。用于家庭已有有效全年 intake 和全年规划，并提供 status ready 的 quarterly-update.md，或提供足够的近期成长记录、幼儿园反馈、作品和家庭观察，需要把长期底座与季度新证据转成温暖、具体、游戏化的家长行动指南时。生成 1—2 个聚焦方向、1—2 个自然维持方向、游戏与生活建议、陪伴者互动、家长话术和复盘信号；季度中途跨过 72 月龄仍使用本 Skill。不生成全年规划，不做医学心理诊断、发育筛查、入学预测、学习类型测评或超前学科训练。
---

# 36—71 月龄季度成长计划

把全年规划作为长期知识底座，把最近资料和季度变化转成未来 90 天的游戏、环境与生活支持。计划给家长阅读，不重新做全年定位或入学能力评判。

## 1. 校验年龄与资料

必须取得：

1. `junyi-child-growth-intake/v1` 的全年 `intake.json`；
2. 完整全年规划；
3. `junyi-child-quarterly-update/v1` 的 `quarterly-update.md`，且 `status: ready`。

用户直接提供原始语料时，先使用 `junyi-collect-child-quarterly-update` 提取和验证。资料不足时返回 7—14 天预备观察方案，不生成低证据正式计划。

按季度开始日计算完整月龄。只有 36—71 月龄可以继续；季度中途跨过 72 月龄不换 Skill。全年底座来自旧轨道时，只要仍有效且季度资料记录了过渡，可以作为历史知识继续使用。

```bash
python scripts/validate_bundle.py \
  --intake path/to/intake.json \
  --update path/to/quarterly-update.md \
  --annual-plan path/to/annual-plan.md
```

## 2. 提炼五维度画像

读取：

- [references/preschool-method.md](references/preschool-method.md)
- [references/decision-method.md](references/decision-method.md)
- [references/evidence-and-safety.md](references/evidence-and-safety.md)

从全年底座与本季新资料中提炼：家庭教育目标、孩子优势与成长中课题、重要陪伴者的风格与现实投入、现有资源、本季新数据。关键事实绑定 `Exx` 或 `Qxx`。

孩子必须至少有一项对喜欢、困难、拒绝或愿望的直接表达。成人推断不能代替孩子声音。单次事件可以如实记录，但不能被写成稳定特质。

## 3. 选择聚焦与自然维持方向

按 [references/decision-method.md](references/decision-method.md) 从数据中选择：

- 聚焦方向 1—2 个；
- 自然维持方向 1—2 个。

每个聚焦方向写明：具体证据、为什么是这个季度、孩子怎样表达、三个月后的可观察画面，以及为什么其他方向暂不加码。选择优先考虑发展萌芽、孩子内在动力、外部节点、证据强度和家庭可执行性，不把聚焦写成短板清单。

## 4. 生成游戏化家长指南

严格使用 [references/output-format.md](references/output-format.md)。基础计划通常约 4000—7000 个中文字符。

- 3—4 岁更接近观察与环境支持；
- 4—5 岁可加入轻量游戏目标和过程步骤；
- 5—6 岁可增加生活自主、合作与入学环境准备，但不提前学科化；
- 为每个聚焦方向设计 3—5 个可选择的游戏或生活建议，不要求全部执行；
- 用角色扮演、有限选择、可见步骤和真实家庭任务承载建议；
- 根据真实家庭结构设计重要陪伴者专属互动，不默认父亲角色；
- 家长话术覆盖至少 5 个高频场景；
- 写 3—5 条个性化避坑提醒；
- 用绿灯、黄灯、红灯观察孩子体验、实际效果和家庭负担。

## 5. 验收与交付

```bash
python scripts/validate_plan.py path/to/quarterly-plan.md
```

人工检查：

- 关键判断是否绑定 `Exx` 或 `Qxx`；
- 是否真正包含孩子直接表达；
- 聚焦是否为 1—2 个、自然维持是否为 1—2 个；
- 是否把单次事件写成稳定特质；
- 是否出现奖励交换、比较、羞辱、威胁或超前学科指标；
- 建议是否符合 3—4、4—5 或 5—6 岁的不同强度；
- 家庭成员与资源是否有证据，是否替他人承诺；
- 停止或求助信号是否只用于调整和联系合格支持，而非诊断。

未经用户明确要求，不写入飞书、Obsidian、客户文件夹或其他外部系统。
