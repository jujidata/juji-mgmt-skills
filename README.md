# 据吉客户管理技能

这是一个基于技能目录结构的占位模板，适用于企业客户管理、项目进度跟踪以及数据收集项目的协作场景。

## 目录结构

- `SKILL.md`：技能说明与基础工作流说明。
- `manifest.yaml`：技能元数据清单。
- `instructions/`：业务流程说明文档。
  - `enterprise_user_management.md`
  - `project_progress.md`
  - `data_collection_search.md`
  - `api_config.md`
- `tools/`：工具定义文件，描述可调用 API 能力。
  - `enterprise_user_tools.json`
  - `project_management_tools.json`
  - `data_collection_tools.json`
- `scripts/`：脚本占位文件，用于数据汇总和图表可视化。
  - `chart_visualization.py`
  - `data_summary.py`
- `api-config.example.json`：API 调用配置样例（需复制为 `api-config.json` 后填写真实密钥）

## 适用场景

- 企业用户管理与权限维护
- 项目进度监控与汇报
- 数据收集项目中的检索与统计
- 业务数据的中文化说明与图表展示

## 说明

当前内容均为示例占位文件，便于后续在真实业务系统中扩展实现。后续可以按项目实际需求替换为真实 API、数据库查询和脚本逻辑。

使用 `tools/` 下能力前，必须先正确配置 `api-config.json`。调用方式为 **curl** 或 **Python requests**，不是 MCP。API Key 可在登录 https://jujidata.com/login 后，前往 https://jujidata.com/users/key-mgmt 生成。
