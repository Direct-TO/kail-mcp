# `netcat_connect`

- Purpose: Open TCP connections, listeners, and lightweight banner checks.

## Parameters
- `target` (string): Target host, IP, range, or domain, depending on the tool.
- `port` (integer, required): Target port.
- `mode` (string, default="connect"): Connection mode. Allowed: `connect`, `listen`.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "netcat_connect",
  "arguments": {
    "target": "192.168.56.10",
    "port": 80,
    "mode": "connect",
    "extra_args": "-w 3"
  }
}
```

## Related Knowledge
- [knowledge/tools/netcat.md](../../../knowledge/tools/netcat.md)
