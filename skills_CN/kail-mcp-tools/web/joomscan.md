# `joomscan`

- 用途：扫描 Joomla 组件和已知发现项。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `enumerate`（字符串，默认值="all"）：Joomla 枚举模式。 可选值：`components`, `vuln`, `all`。
- `cookie`（字符串）：会话 Cookie。
- `user_agent`（字符串）：自定义用户代理。
- `proxy`（字符串）：代理地址。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "joomscan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "enumerate": "all"
  }
}
```

## 相关知识
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
