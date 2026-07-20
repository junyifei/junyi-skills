# 季度计划的全年底座要求

季度资料采集和三个季度报告 Skill 不负责首次建立全年成长规划。使用者必须已经持有兼容的全年知识底座；缺少时返回 `blocked-upstream`，再使用 `junyi-child-annual-intake` 和对应年龄段全年报告 Skill 建立底座，不得临时拼出一份全年判断。

## 必需文件

### 1. `intake.json`

至少包含：

```json
{
  "schema_version": "junyi-child-growth-intake/v1",
  "plan_track": "preschool",
  "child": {
    "id": "CHILD-001",
    "birth_date": "2022-02-15"
  }
}
```

- `child.id` 使用匿名代号，不写真实姓名或昵称；
- `birth_date` 使用 `YYYY-MM-DD`，只用于计算季度开始日完整月龄；
- `plan_track` 为 `infant`、`preschool` 或 `school-age`。

### 2. 完整全年规划

全年规划至少应包含：

- 家庭教育目标与不愿牺牲的底线；
- 孩子的优势、兴趣和当前支持方向；
- 重要陪伴者的实际投入、优势与限制；
- 已有时间、环境、活动、关系和其他资源；
- 关键事实的来源、未知与专业边界；
- 生成或最近更新日期。

文档标题使用当前轨道对应标题：

- `# 0—3 岁全年成长规划`
- `# 3—6 岁全年成长规划`
- `# 6—12 岁全年成长规划`

并包含：

```text
本规划不替代医疗、心理、发育筛查或教育专业评估
```

年龄轨道刚发生变化时，可以按下游 bundle 校验规则继续使用上一轨道全年规划作为历史底座，不因为人为月龄边界强制重做。

## 不能提供时

如果缺少 `intake.json`、无法确认出生日期、全年规划不完整，或家庭发生了足以改变长期判断的重大变化：

1. 将 `quarterly-update.md` 标为 `status: blocked-upstream`；
2. 列出缺少或需要更新的资料；
3. 不生成正式季度报告；
4. 路由到 `junyi-child-annual-intake`，资料通过后再按 `plan_track` 进入：
   - `junyi-infant-annual-plan`
   - `junyi-preschool-annual-plan`
   - `junyi-school-age-annual-plan`
