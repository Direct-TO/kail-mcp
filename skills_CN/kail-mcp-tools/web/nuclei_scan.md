# `nuclei_scan`

- 用途：使用模板检查漏洞、暴露面和错误配置。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `templates`（字符串）：模板标签或路径。
- `severity`（字符串）：报告的最低严重度。 可选值：`info`, `low`, `medium`, `high`, `critical`。
- `rate_limit`（整数，默认值=150）：每秒最大请求数。
- `proxy`（字符串）：代理地址。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "nuclei_scan",
  "arguments": {
    "target": "http://192.168.56.10",
    "templates": "cve,misconfig",
    "severity": "medium",
    "rate_limit": 50
  }
}
```

## 使用要点
- 结合服务版本和可访问路径复核模板命中结果。

## 相关知识
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
