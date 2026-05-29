# `get_scan_history`

- Purpose: Query saved scan history from SQLite.

## Parameters
- `tool` (string): Tool name filter.
- `target` (string): Target host, IP, range, or domain, depending on the tool.
- `limit` (integer, default=20): Maximum result count.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "get_scan_history",
  "arguments": {
    "target": "192.168.56.10",
    "limit": 10
  }
}
```

## Notes
- This tool only queries saved scan records; it does not start a new scan.
