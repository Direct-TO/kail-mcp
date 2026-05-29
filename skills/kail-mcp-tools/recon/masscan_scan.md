# `masscan_scan`

- Purpose: Find open TCP ports quickly across large ranges.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `ports` (string, default="1-1000"): Port specification or range.
- `rate` (integer, default=1000): Packets per second.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "masscan_scan",
  "arguments": {
    "target": "192.168.56.0/24",
    "ports": "80,443,445,3389",
    "rate": 1000
  }
}
```

## Notes
- Use it for fast TCP discovery, then confirm services with nmap_scan.

## Related Knowledge
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
