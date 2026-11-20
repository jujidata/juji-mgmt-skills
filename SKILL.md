---
name: juji-mgmt-skills
description: 使用据吉 API Key 查询企业、成员角色汇总、项目进度、采集项目人脸去重用量、企业人脸去重剩余额度和所管理员工的工作统计。支持按姓名或员工 ID 查个人工作量，并为单个项目或权限内全部项目绘制工作统计柱状图和折线图。
metadata:
  version: "0.6.0"
---

# 据吉企业管理技能

使用本 Skill 通过据吉开放 API 查询企业、项目、人脸去重额度及员工工作统计。服务端根据 API Key 绑定的用户、Membership 和企业确定数据范围。

## 使用前检查

1. 读取 `instructions/api_config.md`，确认 `api-config.json` 已配置。
2. 首次使用或遇到认证问题时，调用 `GET /api/open-api/v1/me` 验证 Key。
3. 不在输出、日志或错误信息中回显完整 API Key。
4. 只调用 `tools/` 中声明的真实接口，不猜测或调用内部 `/api/projects`、`/api/users` 等 JWT 接口。

## 场景路由

- 企业名称、企业 ID 或成员角色数量：读取 `instructions/enterprise_user_management.md` 和 `tools/enterprise_user_tools.json`。
- 项目列表、项目详情或项目完成进度：读取 `instructions/project_progress.md` 和 `tools/project_management_tools.json`。
- 采集项目人脸去重用量或企业人脸去重剩余额度：读取 `instructions/face_dedup_quota.md`，复用 `tools/project_management_tools.json` 的项目工具和 `tools/enterprise_user_tools.json` 的企业额度工具。
- 单个项目或权限内全部项目的工作统计图：读取 `instructions/work_statistics.md` 的「项目工作统计图」，使用项目列表或详情确定范围，汇总所管理员工的每日产出。默认柱状图，按要求生成折线图或两种图，仅支持这两种类型。
- 员工的标注、审核、打回或采集工作量：读取 `instructions/work_statistics.md` 和 `tools/work_statistics_tools.json`。查询各员工或按姓名查询个人时，先读取当前 Key 可查看统计的员工名单。
- 用户询问采集记录、任务明细或数据搜索：读取 `instructions/data_collection_search.md`，明确当前能力边界，并提供现有项目级统计作为可选替代。
- 企业角色汇总或项目进度需要中文结构化摘要或图表时，使用 `scripts/data_summary.py` 或 `scripts/chart_visualization.py` 处理相应的 API 响应。

## 标准工作流

1. 根据问题选择对应场景。
2. 从 `api-config.json` 读取 `base_url` 和 `api_key`；默认 `base_url` 为 `https://jujidata.com`。
3. 使用 `X-API-Key` 请求头调用对应只读接口。
4. 按服务端权限结果回答。项目或员工工作统计返回 404 时，告知资源不存在或当前身份无权访问。
5. 将响应整理为简洁中文结论；只有用户需要图表时才运行可视化脚本。

## 安全与能力边界

- API Key 默认 14 天有效，可被管理员随时撤销；401 时提示用户检查 Key 是否缺失、格式错误、过期、撤销或绑定身份失效。
- API Key 只绑定有效的企业管理员身份。Skill 不能创建、列出或撤销 Key，因为这些管理接口使用登录 JWT，不属于开放 API。
- 工作统计开放 API 提供授权员工的姓名、展示名称、企业角色、用户 ID 和聚合工作量。
- 当前没有开放完整成员资料、任务列表、采集记录搜索、数据导出和修改接口。不得用占位路径伪造这些能力。
