# 企业概览与成员角色汇总

## 可用能力

当前开放 API 支持：

- 查询 API Key 绑定企业的 `id` 和 `name`。
- 查询该企业有效成员按角色聚合的数量和总人数。

当前不支持成员列表、成员详情、联系方式、状态筛选以及新增、更新或停用成员。不要调用占位接口或内部 JWT 接口补齐这些数据。

## 查询流程

1. 按 `api_config.md` 验证 API Key。
2. 调用 `GET /api/open-api/v1/enterprise` 获取绑定企业。
3. 用户需要人员规模或角色分布时，调用 `GET /api/open-api/v1/enterprise/users/summary`。
4. 使用 `total_count` 与 `by_role` 输出中文汇总；不要把缺失角色自行补成有业务含义的数据。
5. 需要结构化报告时，将角色汇总响应交给 `scripts/data_summary.py --kind enterprise-users`。

## 响应语义

企业接口只返回：

```json
{
  "id": 13,
  "name": "示例企业"
}
```

成员汇总接口返回：

```json
{
  "total_count": 10,
  "by_role": {
    "admin": 2,
    "employee": 8
  }
}
```

`by_role` 的键来自服务端实际角色值。汇报时可以翻译常见角色名称，但应保留原始角色值以避免歧义。

## 输出建议

优先回答企业名称、成员总数、各角色人数及其占比。明确说明这是角色聚合数据，不是成员明细，也不能用于识别具体人员。
