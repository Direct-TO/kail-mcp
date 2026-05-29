# `get_scan_history`

- 用途：查询保存在 SQLite 中的扫描历史。

## 参数
- `tool`（字符串）：工具名过滤器。
- `target`（字符串）：目标主机、IP、范围或域名，具体含义取决于工具。
- `limit`（整数，默认值=20）：最大结果数量。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "get_scan_history",
  "arguments": {
    "target": "192.168.56.10",
    "limit": 10
  }
}
```

## 使用要点
- 这个工具只查询已保存的扫描记录，不会启动新的扫描。
