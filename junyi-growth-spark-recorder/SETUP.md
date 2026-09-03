# junyi-growth-spark-recorder · 安装与初始化

## 1. 安装

将整个 `junyi-growth-spark-recorder` 文件夹安装到你使用的 Agent 的 Skills 目录。安装后新开一个会话，让 Agent 重新发现 Skill。

第一次可这样测试：

> 用 junyi-growth-spark-recorder 只分析这个虚构片段，不要保存：小雨今天搭积木倒了三次，第四次请爸爸扶住底座，最后自己搭完了。

输出包含“记录、发展观察、模型复盘”，且结尾显示“仅分析｜未写入”，说明主体可用。

## 2. 不配置也能用

不提供配置时，Skill 只在当前对话中分析，不会创建文件，也不会声称已经记住孩子资料。

## 3. 需要长期保存时再建立私人配置

不要修改公开 `SKILL.md`，也不要把真实家庭资料放进 GitHub 仓库。

1. 复制 `references/config.example.json` 到：
   `~/.config/junyi-skills/junyi-growth-spark-recorder.json`
2. 在复制后的私人文件里填写孩子标识和归档根目录。
3. 运行：

```bash
python3 scripts/validate_config.py ~/.config/junyi-skills/junyi-growth-spark-recorder.json
```

也可以把配置保存在其他私人位置，并设置环境变量 `JUNYI_GROWTH_SPARK_CONFIG` 指向它。

配置只提供身份映射与本地路径，不应包含账号密码、访问令牌、诊断标签或准备公开的真实案例。

## 4. 保存与长期档案是两次授权

- “帮我分析”只分析。
- “记录一下／存下来”允许保存一条事件。
- “把它写成里程碑／更新长期档案”才允许修改长期档案。
- 发布、发送给他人或上传云端始终需要单独授权。

## 5. 验证保存

先用虚构资料和临时目录测试：

> 记录一下这个虚构事件，日期是 2026-01-15，当事人是小雨：她搭积木倒了三次，第四次请爸爸扶住底座，最后自己搭完了。不要更新长期档案。

确认只生成一份事件主记录、原始描述仍在、长期档案没有被修改后，再用于真实家庭材料。
