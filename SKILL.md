---
name: juji-mgmt-skills
description: 通过据吉只读开放 API 查询企业、成员角色汇总、项目列表、项目详情和项目统计，并生成中文业务摘要或图表。用于用户提供据吉 API Key 配置后的企业与项目查询；不用于成员明细、任务明细、采集记录搜索或写操作。
version: 0.1.0
---

# 据吉企业管理技能

使用本 Skill 通过据吉开放 API 完成只读的企业和项目查询。所有服务端数据范围由 API Key 绑定的用户、Membership 和企业决定，不要求也不接受用户另行指定企业 ID。

## 使用前检查

1. 读取 `instructions/api_config.md`，确认 `api-config.json` 已配置。
2. 首次使用或遇到认证问题时，调用 `GET /api/open-api/v1/me` 验证 Key。
3. 不在输出、日志或错误信息中回显完整 API Key。
4. 只调用 `tools/` 中声明的真实接口，不猜测或调用内部 `/api/projects`、`/api/users` 等 JWT 接口。

## 场景路由

- 企业名称、企业 ID 或成员角色数量：读取 `instructions/enterprise_user_management.md` 和 `tools/enterprise_user_tools.json`。
- 项目列表、项目详情或项目完成进度：读取 `instructions/project_progress.md` 和 `tools/project_management_tools.json`。
- 用户询问采集记录、任务明细或数据搜索：读取 `instructions/data_collection_search.md`，明确当前能力边界，并提供现有项目级统计作为可选替代。
- 需要中文结构化摘要或图表：使用 `scripts/data_summary.py` 或 `scripts/chart_visualization.py` 处理已经取得的 API 响应。

## 标准工作流

1. 明确用户需要企业汇总、项目查询还是项目统计。
2. 从 `api-config.json` 读取 `base_url` 和 `api_key`；默认 `base_url` 为 `https://jujidata.com`。
3. 使用 `X-API-Key` 请求头调用对应只读接口。
4. 保留服务端权限结果，不尝试扩大数据范围；项目不存在或无权限时统一按 404 处理。
5. 将响应整理为简洁中文结论；只有用户需要图表时才运行可视化脚本。

## 安全与能力边界

- API Key 默认 14 天有效，可被管理员随时撤销；401 时提示用户检查 Key 是否缺失、格式错误、过期、撤销或绑定身份失效。
- API Key 只绑定有效的企业管理员身份。Skill 不能创建、列出或撤销 Key，因为这些管理接口使用登录 JWT，不属于开放 API。
- 当前 API 只返回企业最小信息、成员角色聚合和项目安全字段，不返回联系方式、项目 Token、任务数据账号、密码或标签配置。
- 当前没有开放成员明细、任务列表、采集记录搜索、数据导出和修改接口。不得用占位路径伪造这些能力。
