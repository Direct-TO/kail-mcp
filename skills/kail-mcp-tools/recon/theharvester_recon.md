# `theharvester_recon`

- Purpose: Collect emails, subdomains, hosts, and employee names.

## Parameters
- `domain` (string, required): Domain name.
- `sources` (string, default="google,bing,crtsh"): Data sources to query.
- `limit` (integer, default=100): Maximum result count.
- `dns_brute` (boolean, default=false): Perform DNS brute force.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "theharvester_recon",
  "arguments": {
    "domain": "example.test",
    "sources": "google,bing,crtsh",
    "limit": 50,
    "dns_brute": false
  }
}
```

## Related Knowledge
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
