# `searchsploit_query`

- 用途：在本地 Exploit-DB 索引中搜索公开利用参考。

## 参数
- `query`（字符串，必填）：搜索词。
- `exact`（布尔值，默认值=false）：使用精确匹配。
- `json_output`（布尔值，默认值=true）：返回 JSON 输出。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "searchsploit_query",
  "arguments": {
    "query": "OpenSSH 7.9",
    "exact": false,
    "json_output": true
  }
}
```

## 相关知识
- [knowledge/tools/searchsploit.md](../../../knowledge/tools/searchsploit.md)
