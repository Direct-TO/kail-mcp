# `joomscan`

- Purpose: Scan Joomla components and known findings.

## Parameters
- `target_url` (string, required): Target URL.
- `enumerate` (string, default="all"): Joomla enumeration mode. Allowed: `components`, `vuln`, `all`.
- `cookie` (string): Session cookie.
- `user_agent` (string): Custom user agent.
- `proxy` (string): Proxy URL.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "joomscan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "enumerate": "all"
  }
}
```

## Related Knowledge
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
