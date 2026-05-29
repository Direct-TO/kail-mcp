# `ettercap_mitm`

- Purpose: Run Ettercap MITM attacks and plugins.

## Parameters
- `target1` (string, required): First target IP.
- `target2` (string, required): Second target IP.
- `interface` (string, default="eth0"): Network interface.
- `attack_type` (string, default="arp"): Attack type. Allowed: `arp`, `dhcp`, `port`, `icmp`.
- `filters` (array<string>): Filters to apply.
- `plugins` (array<string>): Plugins to load.
- `mode` (string, default="text"): Interface mode. Allowed: `text`, `curses`, `daemon`.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "ettercap_mitm",
  "arguments": {
    "target1": "192.168.56.10",
    "target2": "192.168.56.1",
    "interface": "eth0",
    "attack_type": "arp",
    "mode": "text"
  }
}
```

## Notes
- Use for MITM workflows that observe or alter communication paths.

## Related Knowledge
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
