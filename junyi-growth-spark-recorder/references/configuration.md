# 私人配置契约

公开 Skill 只定义字段，不保存任何家庭的真实值。每位使用者在自己的电脑上维护一份私人配置。

## 必填字段

- `schema_version`：当前固定为 `1`。
- `archive_root`：事件档案的绝对路径。必须指向使用者明确选择的私人目录。
- `subjects`：至少一位孩子；每位包含稳定的 `id` 和显示名 `display_name`。
- `write_policy.event_records`：是否允许在用户明确授权后保存事件。
- `write_policy.profile_updates_require_separate_confirmation`：必须为 `true`。

## 可选字段

- `birth_date`：`YYYY-MM-DD`。不知道时留空，不得估算。

## 约束

- `id` 只使用小写英文字母、数字和短横线，避免姓名进入文件名。
- 多位孩子的 `id` 和 `display_name` 都不能重复。
- 配置不保存密码、令牌、医疗诊断、完整学校地址或准备公开的真实案例。
- Agent 只在当前任务需要时读取相关字段，不在回复中完整复述配置。
- 配置文件建议权限为仅本人可读写，例如 macOS/Linux 使用 `chmod 600 <配置文件>`。
