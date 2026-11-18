# 项目查询与进度展示

## 可用能力

- 按项目类型分页查询当前 API Key 身份有权访问的项目。
- 查询单个项目的安全字段。
- 查询单个项目的聚合任务统计和完成率。

服务端会同时使用 API Key 绑定的用户和企业做权限过滤。Skill 不传入企业 ID，也不能通过遍历项目 ID 扩大访问范围。

## 项目列表

调用：

```text
GET /api/open-api/v1/projects?project_type=annotation&page=1&page_size=20
```

约束：

- `project_type` 必填，仅支持 `annotation`（标注项目）或 `collection`（采集项目）；缺失或非法值返回 400。
- `page` 从 1 开始，默认 1。
- `page_size` 默认 20，最大 100。
- 响应通过 `has_more` 表示是否继续请求下一页。
- 用户要求“全部项目”时，分别按两种项目类型逐页读取，直到各自的 `has_more=false`；设置合理上限并避免无界请求。

列表和详情中的每个项目只包含 `id`、`title`、`description`、`project_type`、`job_type`、`job_status`、`created_at` 和 `updated_at`。

- `project_type`：`annotation` 为标注项目，`collection` 为采集项目。
- `job_type`：标注项目中 `SELF_ANNOTATION` 为自标，`OUTSOURCE` 为外包；采集项目或未关联作业时为 `null`，不要据此推断为外包。
- `job_status`：项目返回的作业状态；已知值 `in-process` 表示进行中，`aborted` 表示已中止。不再返回 `is_published` 和 `is_draft`。

## 中文展示

面向用户的项目列表和项目详情默认使用中文字段和值：

- 项目类型：`annotation` 显示为“标注项目”，`collection` 显示为“采集项目”。
- 作业类型：`SELF_ANNOTATION` 显示为“自标”，`OUTSOURCE` 显示为“外包”；`null` 显示为“未关联作业”。
- 作业状态：`in-process` 显示为“进行中”，`aborted` 显示为“已中止”；`null` 显示为“—”。不要根据作业类型推断作业状态。
- 遇到未列出的状态值时，保留服务端原值，不猜测其中文含义。

建议使用“项目类型、作业类型、作业状态、创建时间”等中文列名。只有用户要求核对 API 原始值时，才同时展示原值。

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

先从项目详情读取 `project_type`，再按类型解释统计数据。统计摘要命令必须显式指定类型，例如：

```text
python scripts/data_summary.py --kind project-statistics --project-type annotation
python scripts/data_summary.py --kind project-statistics --project-type collection
```

### 标注项目

- `total_tasks`：任务总数。
- `completed_tasks`：已完成任务数。
- `pending_review_tasks`：待审核任务数。
- `tasks_with_annotations`：已有标注的任务数。
- `skipped_annotations`：跳过的标注数。
- `completion_rate`：0 到 1 的完成率；任务总数为 0 时为 0。

标注项目摘要沿用任务完成和待审核的解读方式。

### 采集项目

- `total_tasks`：总采集次数，例如人脸采集中的拍照（含查重）次数。
- `completed_tasks`：数据提交次数；不包含被查重以及正在提交的数据。
- `completion_rate`：提交率，范围为 0 到 1。
- `completion_percentage`：将 `completion_rate` 转换为百分比后的值。

采集项目的摘要 JSON 只包含采集相关指标，不要求也不输出 `pending_review_tasks`、`tasks_with_annotations` 或 `skipped_annotations`。摘要将 `completed_tasks` 解读为已提交次数，并将完成率称为提交率；不要用 `completed_tasks / total_tasks` 重新计算，因为总采集次数包含查重等不计为提交的次数。

## 汇报流程

1. 用户只给项目名称时，按指定项目类型分页查询并匹配；未指定类型时分别查询两种类型，同名时列出候选 ID 请求确认。
2. 获取项目详情和统计数据，根据项目详情中的 `project_type` 区分项目。
3. 使用 `scripts/data_summary.py --kind project-statistics --project-type <annotation|collection>` 生成对应的结构化摘要。
4. 用户明确需要图表时，标注项目可使用 `scripts/chart_visualization.py --kind project-statistics`；采集项目不要使用该图表，因为它展示的是标注项目指标。
5. 只根据返回的聚合指标描述进度，不推断负责人、截止日期、风险或任务明细。
