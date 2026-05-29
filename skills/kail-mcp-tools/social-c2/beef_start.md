# `beef_start`

- Purpose: Start or control the BeEF browser exploitation framework.

## Parameters
- `action` (string, default="start"): Action to perform. Allowed: `start`, `stop`, `status`, `hook`, `command`.
- `port` (integer, default=3000): Target port.
- `target_url` (string): Target URL.
- `command_module` (string): Parameter value.
- `hook_id` (string): Parameter value.
- `options` (object): Module options.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "beef_start",
  "arguments": {
    "action": "status",
    "port": 3000
  }
}
```

## Notes
- Supports status, start, hook, and command actions.

## Related Knowledge
- [knowledge/tools/social_engineering.md](../../../knowledge/tools/social_engineering.md)
