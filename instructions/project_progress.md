# 项目查询与进度展示

## 可用能力

- 分页查询当前 API Key 身份有权访问的项目。
- 查询单个项目的安全字段。
- 查询单个项目的聚合任务统计和完成率。

服务端会同时使用 API Key 绑定的用户和企业做权限过滤。Skill 不传入企业 ID，也不能通过遍历项目 ID 扩大访问范围。

## 项目列表

调用：

```text
GET /api/open-api/v1/projects?page=1&page_size=20
```

约束：

- `page` 从 1 开始，默认 1。
- `page_size` 默认 20，最大 100。
- 响应通过 `has_more` 表示是否继续请求下一页。
- 用户要求“全部项目”时逐页读取，直到 `has_more=false`；设置合理上限并避免无界请求。

每个项目只包含 `id`、`title`、`description`、`is_published`、`is_draft`、`job_status`、`created_at` 和 `updated_at`。

## 项目详情

调用：

```text
GET /api/open-api/v1/projects/{projectId}
```

`projectId` 必须是正整数。不存在和无权限统一返回 404，不要向用户断言是哪一种情况。

## 项目统计

调用：

```text
GET /api/open-api/v1/projects/{projectId}/statistics
```

响应字段：

- `total_tasks`：任务总数。
- `completed_tasks`：已完成任务数。
- `pending_review_tasks`：待审核任务数。
- `tasks_with_annotations`：已有标注的任务数。
- `skipped_annotations`：跳过的标注数。
- `completion_rate`：0 到 1 的完成率；任务总数为 0 时为 0。

## 汇报流程

1. 用户只给项目名称时，先分页查询项目并匹配；同名时列出候选 ID 请求确认。
2. 获取项目详情和统计数据。
3. 使用 `scripts/data_summary.py --kind project-statistics` 生成结构化摘要，或直接将 `completion_rate` 转成百分比。
4. 用户明确需要图表时，使用 `scripts/chart_visualization.py --kind project-statistics`。
5. 只根据返回的聚合指标描述进度，不推断负责人、截止日期、风险或任务明细。
