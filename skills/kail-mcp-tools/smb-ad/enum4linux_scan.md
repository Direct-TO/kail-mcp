# `enum4linux_scan`

- Purpose: Enumerate SMB and NetBIOS users, shares, groups, and policies.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `options` (string, default="all"): Module options. Allowed: `all`, `users`, `shares`, `policies`, `groups`.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "enum4linux_scan",
  "arguments": {
    "target": "192.168.56.10",
    "options": "all"
  }
}
```

## Notes
- Commonly used for initial SMB enumeration before credential testing.

## Related Knowledge
- [knowledge/tools/enum4linux.md](../../../knowledge/tools/enum4linux.md)
