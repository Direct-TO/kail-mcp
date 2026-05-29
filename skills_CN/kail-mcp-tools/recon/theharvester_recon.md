# `theharvester_recon`

- 用途：收集邮箱、子域、主机名和人员名称。

## 参数
- `domain`（字符串，必填）：域名。
- `sources`（字符串，默认值="google,bing,crtsh"）：要查询的数据源。
- `limit`（整数，默认值=100）：最大结果数量。
- `dns_brute`（布尔值，默认值=false）：执行 DNS 暴力枚举。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "theharvester_recon",
  "arguments": {
    "domain": "example.test",
    "sources": "google,bing,crtsh",
    "limit": 50,
    "dns_brute": false
  }
}
```

## 相关知识
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
