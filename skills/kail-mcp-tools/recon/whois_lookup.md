# `whois_lookup`

- Purpose: Look up domain or IP registration records.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "whois_lookup",
  "arguments": {
    "target": "example.test"
  }
}
```

## Related Knowledge
- [knowledge/tools/whois.md](../../../knowledge/tools/whois.md)
