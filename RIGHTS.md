# 权利与许可记录

## 许可

除非某个目录另有明确的 `LICENSE`，本仓库中的 Skill、reference、模板、资源与随附材料统一按 [CC BY-NC 4.0](LICENSE) 发布。推荐署名格式：

> 君一的 AI 时代家庭教育 Skills，作者：君一，许可：CC BY-NC 4.0，来源：https://github.com/junyifei/junyi-skills

CC BY-NC 4.0 不包含对“君一”姓名、肖像或商标的额外授权，也不代表作者为衍生作品背书。商业使用需另行获得作者书面授权。

## 2026-07-17 迁移记录

以下 10 个 Skill 曾在 `million-follower-ip-skills` 仓库以 MIT 发布。作者确认它们均为本人原创，或本人持有完整的重新许可权；迁入本仓库后统一使用 `junyi-*` 名称。当前 GitHub 公开版只发布其中前两项，其余继续保留在本地验证：

- `junyi-positioning`（原 `build-evidence-based-ip-book`）
- `junyi-xhs-benchmark`（原 `find-xiaohongshu-benchmarks`）
- `junyi-audience`（原 `research-audience-insights`，本地）
- `junyi-xhs-topics`（原 `plan-xiaohongshu-topics`，本地）
- `junyi-xhs-title`（原 `write-xiaohongshu-titles`，本地）
- `junyi-xhs-write`（原 `write-xiaohongshu-content`，本地）
- `junyi-xhs-audit`（原 `audit-xiaohongshu-content`，本地）
- `junyi-channels-title`（原 `write-wechat-channels-titles`，本地）
- `junyi-channels-write`（原 `write-wechat-channels-content`，本地）
- `junyi-channels-audit`（原 `audit-wechat-channels-content`，本地）

此前已经取得的 MIT 版本继续受当时的 MIT 许可约束；本记录不撤销既有许可，只说明本仓库当前版本的许可依据。

本地 Skills 只有在完成实盘验证、隐私和权利检查并被显式加入 Git 后，才构成未来公开版本的一部分。

## 2026-07-19 新增公开 Skill 来源记录

以下方法由作者本人在课程、OpenClaw 工作流、长期记录与知识库实践中形成，并为本仓库重新设计为通用版本：

- `junyi-content-distiller`：吸收每日录音蒸馏与长材料分块经验，仅保留可公开的通用结构、证据与恢复机制；
- `junyi-learning-distiller`：把课程中的学习蒸馏流程改写为来源主张、自己的理解、迁移边界与实验闭环；
- `junyi-vault`：把 `junyi-vault-builder` 与 `junyi-vault-filer` 合并为建库、归档、只读诊断三种模式；
- `junyi-personal-website`：从作者课程中的 AI 建站流程重新设计技术决策、原创视觉、证据、无障碍、安全与部署验收。

家庭成员姓名、内部 Agent 名称、飞书账号与资源标识、私人文件路径、关系日志、客户材料、访问凭证和未授权案例均不属于公开授权范围，也不得进入公开文件。

## 2026-07-20 儿童全年 Skill 公开转换记录

`junyi-child-annual-intake`、`junyi-infant-annual-plan`、`junyi-preschool-annual-plan` 和 `junyi-school-age-annual-plan` 从作者本人长期使用的儿童成长语料库与规划工作流中抽取资料采集、年龄分流、证据整理、分章生成和质量校验机制，并为本项目重新设计和表述后公开。公开版本不包含客户资料、内部系统配置、飞书资源标识、访问凭证、文件路径、交付渠道和未经公开验证的评分规则。

## 2026-07-20 儿童季度 Skill 公开转换记录

以下四个 Skill 由作者本人在长期家庭记录与 OpenClaw 儿童季度规划工作流中形成，并转换为面向外部使用者的通用版本：

- `junyi-child-quarterly-intake`
- `junyi-infant-quarterly-plan`
- `junyi-preschool-quarterly-plan`
- `junyi-school-age-quarterly-plan`

公开转换只保留资料采集、证据规则、分龄方法、家长报告结构和确定性校验。作者家庭成员姓名与事件、学校与关系网络、内部 Agent、私有方法名、自动写入规则、账号资源标识、文件路径和真实家庭报告不属于本次公开授权材料。

## 2026-07-24 许可变更与新增公开 Skill 记录

**许可变更**：本仓库许可从 CC BY 4.0 调整为 CC BY-NC 4.0（署名—非商业）。此前已按 CC BY 4.0 获得的版本继续受当时许可约束，本次变更不撤销既有授权，只说明自本版本起的许可依据；商业使用需另行获得作者书面授权。

**新增公开 Skill**：`junyi-relationship-manager` 由作者本人的「AI 实战课（第三期）学员 Skill 包」中的 `relationship-manager` 转为公开通用版。公开版只保留通用的关系记录结构、字段设计、跟进节奏与资源撮合规则；示例人物均为占位（张三/李四），飞书 app_token、table_id 与 vault 路径均为占位符，不含任何真实联系人、账号资源标识或私人文件路径。

## 2026-07-25 新增公开 Skill 记录

**新增公开 Skill**：`junyi-ai-weekly-review` 由作者本人的「AI 实战课（第三期）学员 Skill 包」中的 `ai-weekly-review` 转为公开通用版，归入「理解自己，形成判断」。公开版保留通用的抓取、清洗、按天蒸馏与两份产出模板；随附的 Node 采集脚本经逐个审阅，只用 `os.homedir()` 定位各 AI 工具的本地会话目录，只做本地读写且无网络请求，不含硬编码的私有路径、密钥或联系人。后续蒸馏是否由云端模型处理取决于用户选择的 Agent，Skill 会在读取脱敏 chunk 前告知并确认。Hermes、WorkBuddy 适配器为未验证占位，已在文档中如实标注。

## 2026-08-31 文章创作协作 Skill 公开转换记录

`junyi-article-writing-companion` 来自作者当前私人使用的 `wechat-article-writer` 与长期文章改稿实践，并重新设计为不依赖特定创作者身份的公开通用版。公开版只保留长文协作流程、输入输出、外置配置契约、证据隐私规则和权限边界。

作者本人的定位、写作 DNA、完整范文、选题库、素材库、发布规则、私人文件路径、真实人物与客户案例、业务行动邀请、内部复盘，以及来自第三方的独特表达或专有公式均未进入公开版，也不属于本次公开授权材料。公开版与私人版的名称和发布状态分开管理；本次公开不代表作者已切换当前私人写作入口。

## 案例与示例

- `examples/junyi-positioning-junyi-methodology.md` 使用本仓库自身的真实定位改版作为公开案例，不包含客户资料。
- `examples/junyi-xhs-benchmark-synthetic.md` 是明确标注的合成示例，其中账号、名称和数字均不代表真实平台事实。

外部网页、平台数据、出版物、量表、图示和框架仍归各自权利人所有，不因本仓库采用 CC BY-NC 4.0 而被重新许可。

## 公开边界

- 仓库只接收已确认可公开的通用方法、合成示例或已获授权的脱敏材料。
- 客户记录、家庭信息、账号凭据、绝对路径和私有知识库内容不得随 Skill 发布。
- 从私有实战提炼出来的方法，必须先完成去身份化、可移植性和权利检查。
