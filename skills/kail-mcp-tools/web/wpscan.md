# `wpscan`

- Purpose: Scan WordPress core, plugins, themes, and users.

## Parameters
- `target_url` (string, required): Target URL.
- `enumerate` (array<string>): WordPress components to enumerate.
- `username` (string): Username or username file.
- `password_list` (string): Password list path.
- `api_token` (string): API token.
- `plugins_version` (boolean, default=true): Detect plugin versions.
- `random_agent` (boolean, default=true): Use a random user agent.
- `stealthy` (boolean, default=false): Use lower-request scan behavior.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "wpscan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "enumerate": [
      "vp",
      "vt",
      "u"
    ],
    "random_agent": true,
    "stealthy": true
  }
}
```

## Related Knowledge
- [knowledge/tools/web_scanners.md](../../../knowledge/tools/web_scanners.md)
