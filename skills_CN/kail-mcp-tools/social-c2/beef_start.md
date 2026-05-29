# `beef_start`

- 用途：启动或控制 BeEF 浏览器利用框架。

## 参数
- `action`（字符串，默认值="start"）：要执行的动作。 可选值：`start`, `stop`, `status`, `hook`, `command`。
- `port`（整数，默认值=3000）：目标端口。
- `target_url`（字符串）：目标地址。
- `command_module`（字符串）：参数值。
- `hook_id`（字符串）：参数值。
- `options`（对象）：模块选项。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "beef_start",
  "arguments": {
    "action": "status",
    "port": 3000
  }
}
```

## 使用要点
- 支持 status、start、hook 和 command 操作。

## 相关知识
- [knowledge/tools/social_engineering.md](../../../knowledge/tools/social_engineering.md)
