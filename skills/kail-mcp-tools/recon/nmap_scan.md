# `nmap_scan`

- Purpose: Scan host discovery, ports, services, and scripts with Nmap.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `scan_type` (string, default="quick"): Nmap scan profile. Allowed: `quick`, `full`, `stealth`, `vuln`, `scripts`, `discovery`, `udp`.
- `ports` (string): Port specification or range.
- `timing` (string, default="T3"): Timing template. Allowed: `T0`, `T1`, `T2`, `T3`, `T4`, `T5`.
- `scripts` (string): NSE scripts to run.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "nmap_scan",
  "arguments": {
    "target": "192.168.56.10",
    "scan_type": "quick",
    "timing": "T3"
  }
}
```

## Notes
- Use discovery for CIDR ranges before port scanning live hosts.
- Use extra_args only for flags not covered by the profile parameters.

## Related Knowledge
- [knowledge/tools/nmap.md](../../../knowledge/tools/nmap.md)
