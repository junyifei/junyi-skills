# 标准资料包结构

版本：`junyi-child-growth-intake/v1`

```json
{
  "schema_version": "junyi-child-growth-intake/v1",
  "plan_track": "infant | preschool | school-age",
  "plan_as_of": "YYYY-MM-DD",
  "child": {
    "id": "匿名代号",
    "birth_date": "YYYY-MM-DD",
    "age_months": 48,
    "current_context": "家庭、托育、幼儿园或学校环境的非识别性描述"
  },
  "completed_sections": ["context", "goals", "strengths", "routines", "observations", "multiple_sources", "attempts"],
  "family_goals": [],
  "child_goals": [],
  "strengths": [],
  "context": {"routines": [], "resources": [], "constraints": [], "languages": []},
  "observations": [
    {
      "id": "E01",
      "domain": "关系与沟通",
      "observation": "具体事实或准确原话",
      "source": "家长、孩子、教师或专业人员",
      "observed_at": "YYYY-MM-DD 或 null",
      "situation": "发生情境",
      "interpretation": "暂时解释或 null",
      "confidence": "high | medium | low",
      "unknowns": []
    }
  ],
  "attempts": [],
  "professional_inputs": [],
  "contradictions": [],
  "data_gaps": [],
  "safety_flags": []
}
```

## 数据规则

- `age_months` 必须由出生日期和计划日期计算，不凭文字年龄猜测。
- 每条观察只写一个事实；解释放入 `interpretation`。
- `source` 记录事实的实际提供者，而不是文件提交者。家长汇总材料中的“孩子自己说”“教师反馈”等内嵌标注必须映射为“孩子”“教师”；来源不明时保留未知，不得默认写成“家长”。
- `observed_at: null` 表示时间未知。后续报告不得把它改写成“最近”“近一学期”“长期”或其他未经材料支持的时间范围。
- `professional_inputs` 只转述来源明确的专业结论，不由 Agent 推导。
- `safety_flags` 只记录报告者提出的情况和下一步升级，不写诊断。
- `child_goals` 只收孩子原话或明确表达；家长期望、教师转述或成人推断不得写入 `child_goals`，应放入 `family_goals` 或对应观察的 `interpretation`，并标注“待与孩子确认”。
- 不保存真实姓名、学校全名、住址、联系方式、访问令牌或私有文件路径。
- 第三方（教师、医生等）姓名一律泛化为角色（如“教师”“班主任”“儿保医生”），不保留姓氏；孩子只用匿名代号，其小名/昵称不得出现在任何正文、家长可见产物或过程日志中（即使在“说明已匿名”时也不复述原名）。
- `family_goals` 必须说明家庭想改变或守住的真实生活情境；`strengths` 必须指向具体观察或作品证据。笼统标签、空泛评价和占位文本应留在 `data_gaps`，不得用来满足完整度。
- `completed_sections` 只登记已达到生成门槛的主题。若该主题仍有会改变重点、行动强度或安全判断的关键缺口，就不得标为完成。
- 证据层一经输出即视为冻结。下游可以增加明确标注的假设，但不得静默改写观察、来源、日期、时间范围、置信度或未知项。
