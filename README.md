# 据吉企业管理技能

这是一个通过据吉开放 API 查询企业、项目、人脸去重额度和员工工作统计的只读 Skill，使用据吉平台签发的 API Key。

## 目录结构

- `SKILL.md`：Skill 入口、能力边界和标准工作流。
- `manifest.yaml`：Skill 元数据清单。
- `instructions/`：API 配置及各业务场景的操作说明。
  - `api_config.md`
  - `enterprise_user_management.md`
  - `project_progress.md`
  - `face_dedup_quota.md`
  - `work_statistics.md`
  - `data_collection_search.md`
- `tools/`：真实开放 API 的 HTTP 工具定义。
  - `enterprise_user_tools.json`
  - `project_management_tools.json`
  - `work_statistics_tools.json`
  - `data_collection_tools.json`
- `scripts/`：将 API 响应转换为摘要或图表的本地辅助脚本。
- `api-config.example.json`：本地 API 配置样例。

## 当前能力

- 验证 API Key 并读取其绑定身份。
- 查询 API Key 绑定企业的名称和 ID。
- 查询企业成员的角色聚合数量。
- 分页查询当前身份有权访问的项目。
- 查询单个项目的安全字段和聚合进度统计。
- 「各采集项目用了多少人脸去重额度，企业还剩多少？」逐项目展示累计扣费次数，并查询企业总额度、已用和剩余额度。此功能依赖后端开放企业额度接口、项目统计返回去重用量字段。
- 「各员工的工作统计」会按 API Key 的管理范围展示员工姓名，逐人列出工作量并汇总。
- 「查一下张三最近 7 天的工作统计」按姓名查询。查无匹配时提示核对，重名时列出企业角色和员工 ID，请用户选择。
- 支持按员工 ID 查询、指定日期范围及按项目筛选，统计标注、审核、打回和采集工作量。
- 将企业角色统计或项目统计整理成中文摘要、图表数据和柱状图。

姓名查询依赖后端工作统计名单提供姓名、展示名称和企业角色。完整成员资料、任务明细、采集记录搜索及写操作不在 Skill 能力范围内。

## 使用前配置

1. 登录 [据吉平台](https://jujidata.com/login)。
2. 请当前企业的 Admin 或 Super Admin 通过据吉平台的 API Key 管理能力创建 Key。完整 Key 只显示一次，默认 14 天过期。
3. 复制 `api-config.example.json` 为 `api-config.json`，填入真实 Key。
4. 按 `instructions/api_config.md` 先调用身份验证接口。

`api-config.json` 已加入 `.gitignore`，禁止提交真实 Key。HTTP 请求统一使用 `X-API-Key`，不使用 Bearer Token，也不通过 MCP 调用。
