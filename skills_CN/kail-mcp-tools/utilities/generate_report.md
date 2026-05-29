# `generate_report`

- 用途：从扫描历史生成 Markdown 报告。

## 参数
- `target`（字符串）：目标主机、IP、范围或域名，具体含义取决于工具。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "generate_report",
  "arguments": {
    "target": "192.168.56.10"
  }
}
```

## 使用要点
- 这个工具只根据扫描历史生成报告；如果没有历史记录，就不会产生新的扫描结果。
