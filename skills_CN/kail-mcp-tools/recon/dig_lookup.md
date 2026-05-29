# `dig_lookup`

- 用途：查询 DNS 记录和解析器。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `record_type`（字符串，默认值="A"）：DNS 记录类型。 可选值：`A`, `AAAA`, `MX`, `NS`, `TXT`, `SOA`, `CNAME`, `ANY`。
- `server`（字符串）：要查询的 DNS 服务器。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "dig_lookup",
  "arguments": {
    "target": "example.test",
    "record_type": "MX",
    "server": "8.8.8.8"
  }
}
```

## 相关知识
- [knowledge/tools/dig.md](../../../knowledge/tools/dig.md)
