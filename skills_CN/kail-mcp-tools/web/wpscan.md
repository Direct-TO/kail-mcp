# `wpscan`

- 用途：扫描 WordPress 核心、插件、主题和用户。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `enumerate`（字符串数组）：要枚举的 WordPress 组件。
- `username`（字符串）：用户名或用户名文件。
- `password_list`（字符串）：密码列表路径。
- `api_token`（字符串）：接口令牌。
- `plugins_version`（布尔值，默认值=true）：检测插件版本。
- `random_agent`（布尔值，默认值=true）：使用随机用户代理。
- `stealthy`（布尔值，默认值=false）：使用较低请求量的扫描行为。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "wpscan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "enumerate": [
      "vp",
      "vt",
      "u"
    ],
    "random_agent": true,
    "stealthy": true
  }
}
```

## 相关知识
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
