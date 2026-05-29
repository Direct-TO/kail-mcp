# `shell_command`

- Purpose: Run simple shell commands through the MCP server.

## Parameters
- `command` (string, required): Command to run.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "shell_command",
  "arguments": {
    "command": "pwd"
  }
}
```
