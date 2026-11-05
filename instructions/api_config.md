# API 配置与调用说明

在使用 `tools/` 下的能力前，必须先配置正确的 `api-config.json`。  
`tools/` 里的调用方式是 **curl 命令** 或 **Python requests**，不是 MCP。

## 1) 配置文件

1. 复制 `api-config.example.json` 为 `api-config.json`
2. 填写实际 `api_key`
3. `base_url` 默认使用 `https://jujidata.com`

示例：

```json
{
  "api_key": "YOUR_REAL_API_KEY",
  "base_url": "https://jujidata.com"
}
```

## 2) API Key 获取方式

1. 登录：https://jujidata.com/login  
2. 进入密钥管理页生成 Key：https://jujidata.com/users/key-mgmt

## 3) 调用约定

- 请求头统一使用：`Authorization: Bearer <api_key>`
- `Content-Type: application/json`
- 工具里的相对路径（如 `/api/projects/{project_id}/summary`）需要拼接到 `base_url`

## 4) 快速验证

### curl 示例

```bash
API_KEY=$(jq -r '.api_key' api-config.json)
BASE_URL=$(jq -r '.base_url // "https://jujidata.com"' api-config.json)

curl -sS -X GET \
  "${BASE_URL}/api/projects/demo-project/summary" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"
```

### Python requests 示例

```python
import json
import requests

with open("api-config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

base_url = cfg.get("base_url") or "https://jujidata.com"
api_key = cfg["api_key"]

resp = requests.get(
    f"{base_url}/api/projects/demo-project/summary",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    timeout=30,
)
print(resp.status_code, resp.text)
```
