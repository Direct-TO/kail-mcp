# `generate_report`

- Purpose: Generate a Markdown report from scan history.

## Parameters
- `target` (string): Target host, IP, range, or domain, depending on the tool.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "generate_report",
  "arguments": {
    "target": "192.168.56.10"
  }
}
```

## Notes
- This tool builds a report from scan history only; it does not create new scan results.
