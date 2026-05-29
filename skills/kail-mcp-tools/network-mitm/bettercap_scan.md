# `bettercap_scan`

- Purpose: Run BetterCAP network discovery, sniffing, and MITM workflows.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `gateway` (string): Gateway IP address.
- `module` (string, default="arp.spoof"): Module name. Allowed: `arp.spoof`, `dns.spoof`, `http.proxy`, `https.proxy`, `net.sniff`, `tcp.proxy`.
- `action` (string): Action to perform. Allowed: `scan`, `spoof`, `sniff`, `proxy`.
- `interface` (string): Network interface.
- `script` (string): Script name.
- `commands` (array<string>): Commands to run.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "bettercap_scan",
  "arguments": {
    "target": "192.168.56.10",
    "action": "scan",
    "interface": "eth0"
  }
}
```

## Notes
- scan and sniff observe traffic; spoof and proxy change traffic paths.

## Related Knowledge
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
