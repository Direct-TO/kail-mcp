# `shell_command`

- 用途：通过 MCP 服务端运行简单 shell 命令。

## 参数
- `command`（字符串，必填）：要运行的命令。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "shell_command",
  "arguments": {
    "command": "pwd"
  }
}
```
