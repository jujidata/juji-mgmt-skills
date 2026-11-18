# API 配置与调用说明

使用 `tools/` 中的任何能力前，必须先配置并验证 `api-config.json`。调用方式是 **curl** 或 **Python requests**，不是 MCP。

## 1. 配置文件

复制样例并填入创建时仅显示一次的完整 API Key：

```bash
cp api-config.example.json api-config.json
```

```json
{
  "api_key": "juji_sk_完整APIKey",
  "base_url": "https://jujidata.com"
}
```

`api-config.json` 已被 `.gitignore` 忽略。不要提交、打印或在对话回复中展示完整 Key。

## 2. API Key 获取与生命周期

1. 使用当前企业的 Admin 或 Super Admin 登录据吉平台。
2. 通过平台提供的 API Key 管理能力创建 Key；对应后端管理接口需要正常登录 JWT，不属于本 Skill。
3. 创建响应中的完整 Key 只返回一次，应立即交付到安全的密钥配置中。

Key 默认有效期为 14 天，可由同一企业的管理员撤销。用户的企业管理员 Membership 失效后，绑定的 Key 也会立即失效。Skill 只消费已有 Key，不调用使用登录 JWT 的 Key 创建、列表或撤销接口。

## 3. 调用约定

- 默认 Base URL：`https://jujidata.com`
- 开放 API 前缀：`/api/open-api/v1`
- 认证请求头：`X-API-Key: <api_key>`
- 只使用 GET 请求。
- 认证只使用 `X-API-Key` 请求头。
- 不要把 `enterprise_id`、`user_id` 或 `membership_id` 作为客户端权限参数；服务端从 Key 恢复可信身份。

### 本地测试环境（自签名证书）

当 `api-config.json` 中 `insecure_skip_verify` 为 `true` 时，表示正在连接本地部署的测试服务（通常使用自签名证书）。此时所有 curl 调用需附加 `-k`（即 `--insecure`），Python requests 调用需附加 `verify=False`，否则会因证书校验失败而返回 HTTP 000。该开关仅用于本地开发测试；正式环境必须移除该字段或设为 `false`，保持默认严格校验。

## 4. 快速验证

### curl

```bash
API_KEY=$(jq -r '.api_key' api-config.json)
BASE_URL=$(jq -r '.base_url // "https://jujidata.com"' api-config.json)

curl --fail-with-body -sS \
  "${BASE_URL}/api/open-api/v1/me" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Accept: application/json"
```

成功响应包含 `auth_type`、`credential_id`、`user_id`、`membership_id`、`enterprise_id`、`scopes` 和 `expires_at`。除非用户明确需要，不要在最终回复中暴露这些内部标识。

### Python requests

```python
import json
import requests

with open("api-config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

base_url = (config.get("base_url") or "https://jujidata.com").rstrip("/")
response = requests.get(
    f"{base_url}/api/open-api/v1/me",
    headers={"X-API-Key": config["api_key"], "Accept": "application/json"},
    timeout=30,
)
response.raise_for_status()
print(response.json())
```

## 5. 错误处理

- `400`：查询参数或项目 ID 格式错误；修正输入，不要盲目重试。
- `401`：Key 缺失、格式错误、摘要不匹配、已过期、已撤销，或绑定的企业身份已失效。停止调用并请用户更新配置。
- `404`：资源不存在或当前身份无权访问；不要据此判断项目 ID 是否真实存在。
- `5xx`：服务端异常；保留状态码和不含 Key 的错误摘要，有限次数重试后停止。
