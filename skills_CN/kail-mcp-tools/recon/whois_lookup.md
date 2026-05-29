# `whois_lookup`

- 用途：查询域名或 IP 的注册信息。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "whois_lookup",
  "arguments": {
    "target": "example.test"
  }
}
```

## 相关知识
- [knowledge/tools/whois.md](../../../knowledge/tools/whois.md)
