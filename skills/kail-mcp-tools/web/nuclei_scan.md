# `nuclei_scan`

- Purpose: Run template-based checks for CVEs, exposures, and misconfigurations.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `templates` (string): Template tags or paths.
- `severity` (string): Minimum severity to report. Allowed: `info`, `low`, `medium`, `high`, `critical`.
- `rate_limit` (integer, default=150): Maximum requests per second.
- `proxy` (string): Proxy URL.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

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

## Notes
- Review template matches together with service versions and reachable paths.

## Related Knowledge
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
