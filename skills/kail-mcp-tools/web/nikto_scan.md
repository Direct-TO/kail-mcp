# `nikto_scan`

- Purpose: Scan web servers for common findings and misconfigurations.

## Parameters
- `target_url` (string, required): Target URL.
- `tuning` (string): Nikto tuning options.
- `max_time` (integer): Maximum scan time in seconds.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "nikto_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "max_time": 300
  }
}
```

## Related Knowledge
- [knowledge/tools/nikto.md](../../../knowledge/tools/nikto.md)
