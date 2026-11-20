# 员工工作统计

## 查询员工名单

查询各员工或按姓名查询个人时，先按 `api_config.md` 验证身份，再调用 `GET /api/open-api/v1/work-statistics/managed-users?page=1&page_size=50`。名单沿用平台工作统计权限，范围由 API Key 决定，排除 Key 持有人。

- 只要 `has_more` 为 `true` 就请求下一页，包括 `items` 为空的情况。按 `employee_id` 去重，保留不同 ID 的同名员工。设置合理的翻页上限，未查完时说明结果范围。
- `full_name` 是员工已填写的姓名，`display_name` 优先使用企业账号名。展示时优先用 `full_name`，其次用 `display_name`，两者都空时标记为「未设置姓名（员工 ID …）」。
- 如果接口只返回员工 ID 或返回的员工项没有角色，提示当前后端版本暂未提供姓名数据。仍可按员工 ID 查询统计。

## 查询所管理的员工

用户询问「各员工的工作统计」或类似问题时，对名单中的每个 `employee_id` 调用单员工统计接口。所有请求使用同一日期范围及项目筛选。未指定日期时，按上海时区确定含当天的最近 7 个自然日，并向每个请求传入同一对日期。

每位员工一行，展示姓名、标注数、审核数、打回数、采集数及四项指标的各自合计。同名员工保留独立行，附上企业角色和员工 ID。名单为空时说明暂无可统计的其他员工。接口未部署、个别员工查询失败或翻页未完成时说明覆盖范围，失败项不计作零产出。

## 查询单个员工

用户指定员工 ID 时直接调用 `GET /api/open-api/v1/work-statistics/users/{target_user_id}`。用户明确询问自己时，可从 `/me` 获取目标员工 ID。

用户按姓名提问时，在名单的 `full_name` 和 `display_name` 中做精确匹配。比较前使用 Unicode NFKC、去除首尾空白，英文字母忽略大小写。同一员工两个字段都命中时只算一次。

- 恰好一人匹配且名单已查完时，用匹配的员工 ID 查询，并在结果中展示员工姓名。
- 名单已查完且没有匹配时，提示「在当前 API Key 可查看统计的员工中，未找到『某某』」，请用户核对姓名或提供员工 ID。
- 匹配到多人时，列出候选的姓名、企业角色和员工 ID，企业账号名与姓名不同时也列出。请用户回复候选序号或员工 ID。收到选择后，按选定 ID 和原问题的日期与项目条件查询统计。
- 名单未查完或后端未提供姓名数据时，说明无法确认匹配结果。待查完名单或用户提供明确员工 ID 后再查询。

| 参数 | 位置 | 规则 |
| --- | --- | --- |
| `target_user_id` | 路径 | 必填，由用户提供、按姓名确认，或从 `/me` 获取的正整数用户 ID。 |
| `start_date`、`end_date` | 查询 | 成对传入 `YYYY-MM-DD`，按 `Asia/Shanghai` 自然日统计，包含首尾两天，最多 31 天。一起省略时查询截至今天的最近 7 个自然日。 |
| `project_id` | 查询 | 可选，授权项目的正整数 ID。省略时统计该员工的全部授权项目。 |

工作统计按员工在指定日期内的产出聚合。查询整个项目的总体进度时，使用 `project_progress.md`。

## 读取结果

- `employee_id` 和 `range` 标明员工用户 ID、实际生效的日期范围和时区。
- `summary` 提供标注数 `annotated`、审核数 `reviewed`、打回数 `returned`、采集数 `collected` 和有产出天数 `productive_days`。审核数包含打回，说明各项指标时避免把它们相加当作去重任务数。
- 趋势使用 `daily` 中每天按项目拆分的计数，项目对比使用 `project_distribution`。报告注明实际统计区间和已选的项目筛选条件。
- `200` 响应中的零计数或空项目分布表示当前查询范围内无对应产出或项目数据。

## 项目工作统计图

图表按天展示所管理员工的标注、审核、打回和采集数量，默认使用分组柱状图。用户指定折线图时使用折线图，同时要求两种时用同一份数据分别绘制。指定其他图表类型时，提示目前只支持柱状图和折线图，请用户选择。审核数包含打回，四项指标独立展示。

1. 读取 `tools/project_management_tools.json` 和 `tools/work_statistics_tools.json`。单个项目按 ID 使用 `get_project` 确认，按名称使用 `list_projects` 分页查找并精确匹配项目标题。匹配前按 NFKC 规范化、去除首尾空白并忽略英文字母大小写。列表查完后仍无匹配时提示核对名称或 ID，重名时列出项目类型和 ID 请用户选择。
2. 权限内全部项目通过 `list_projects` 分别读取 `annotation` 和 `collection` 全部分页，按项目 ID 去重。按天将这些项目的四项统计分别加总。明确要求逐项目绘图时，复用查询结果，分别按单项目 ID 绘制。项目列表未查完时说明实际范围。没有可见项目时说明情况。
3. 按「查询员工名单」取得完整名单。对每个不同的员工 ID 查询一次 `get_employee_work_statistics`，传入相同的日期范围并省略 `project_id`。这样能在同一份响应中取得该员工的所有授权项目，由绘图脚本按所选项目 ID 过滤，单项目也无需逐个尝试员工与项目的权限组合。沿用最近 7 个上海自然日的默认范围，最多 31 天。
4. 将成功响应原样放入 `employees`，使脚本直接用 `daily[].projects` 计算每日计数。名单为空、无成功响应，或成功响应均未覆盖所选项目时，说明没有可用的项目工作统计数据。个别员工查询失败时记录在 `failed_employee_count`，说明图表只覆盖成功查询的员工。可见但未出现在每日数据中的项目不计入实际覆盖范围，说明未覆盖的项目，避免将缺失统计当作零产出。

脚本接收一个 JSON 对象，包含 `range`（与员工响应的日期及 `Asia/Shanghai` 时区一致）、`project_ids`（单项目为一个 ID，全部项目为去重后的可见项目 ID）、`employees`（成功的完整员工统计响应数组）及可选的 `failed_employee_count`（查询失败的员工数）。在 Skill 目录中运行，绘图需要 Matplotlib 和支持中文的系统字体（如 Noto Sans CJK SC）。

```bash
python3 scripts/chart_visualization.py --kind project-work-statistics \
  --input project-work.json --output project-work-bar.png --title '项目名称（ID 123）工作统计'
python3 scripts/chart_visualization.py --kind project-work-statistics --chart-type line \
  --input project-work.json --output project-work-line.png --title '可见项目工作统计汇总'
```

按实际项目范围设置标题，同时输出两种图时使用两个输出文件。回复中包含图片、日期范围和权限覆盖说明。项目任务进度快照按 `project_progress.md` 处理。

## 错误处理

- `400` 检查员工 ID、项目 ID、日期格式和日期范围。
- `401` 回到 `api_config.md` 检查 Key 和绑定身份。
- 员工统计返回 `404` 时，说明员工或项目不存在或当前身份无权访问。名单接口返回 `404` 时，说明当前环境尚无法读取管理员工名单。
