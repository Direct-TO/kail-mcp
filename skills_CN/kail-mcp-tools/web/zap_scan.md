# `zap_scan`

- 用途：运行 OWASP ZAP 的爬取、被动、主动或完整网页扫描。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `scan_type`（字符串，默认值="full"）：ZAP 扫描类型。 可选值：`spider`, `active`, `passive`, `full`。
- `api_key`（字符串）：接口密钥。
- `port`（整数，默认值=8080）：目标端口。
- `context_name`（字符串）：上下文名称。
- `include_patterns`（字符串数组）：要包含的地址模式。
- `exclude_patterns`（字符串数组）：要排除的地址模式。
- `max_children`（整数，默认值=5）：爬取的最大子项数量。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "zap_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "scan_type": "spider",
    "max_children": 5
  }
}
```

## 使用要点
- passive、spider、active 和 full 代表不同扫描深度。

## 相关知识
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
