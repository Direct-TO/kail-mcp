# `nikto_scan`

- 用途：扫描网页服务器的常见发现项和错误配置。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `tuning`（字符串）：Nikto 调优选项。
- `max_time`（整数）：最大扫描时间，单位为秒。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "nikto_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "max_time": 300
  }
}
```

## 相关知识
- [knowledge/tools/nikto.md](../../../knowledge/tools/nikto.md)
