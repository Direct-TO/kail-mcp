# `whatweb_scan`

- Purpose: Fingerprint web technologies and application stacks.

## Parameters
- `target_url` (string, required): Target URL.
- `aggression` (string, default="1"): WhatWeb aggression level. Allowed: `1`, `3`, `4`.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "whatweb_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "aggression": "1"
  }
}
```

## Related Knowledge
- [knowledge/tools/whatweb.md](../../../knowledge/tools/whatweb.md)
