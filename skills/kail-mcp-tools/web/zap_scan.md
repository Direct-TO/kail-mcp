# `zap_scan`

- Purpose: Run OWASP ZAP spider, passive, active, or full web scans.

## Parameters
- `target_url` (string, required): Target URL.
- `scan_type` (string, default="full"): ZAP scan type. Allowed: `spider`, `active`, `passive`, `full`.
- `api_key` (string): API key.
- `port` (integer, default=8080): Target port.
- `context_name` (string): Context name.
- `include_patterns` (array<string>): URL include patterns.
- `exclude_patterns` (array<string>): URL exclude patterns.
- `max_children` (integer, default=5): Maximum spider children.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "zap_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "scan_type": "spider",
    "max_children": 5
  }
}
```

## Notes
- passive, spider, active, and full cover different scan depths.

## Related Knowledge
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
