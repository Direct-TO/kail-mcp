# `dig_lookup`

- Purpose: Query DNS records and resolvers.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `record_type` (string, default="A"): DNS record type. Allowed: `A`, `AAAA`, `MX`, `NS`, `TXT`, `SOA`, `CNAME`, `ANY`.
- `server` (string): DNS server to query.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "dig_lookup",
  "arguments": {
    "target": "example.test",
    "record_type": "MX",
    "server": "8.8.8.8"
  }
}
```

## Related Knowledge
- [knowledge/tools/dig.md](../../../knowledge/tools/dig.md)
