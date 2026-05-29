# `tcpdump_capture`

- Purpose: Capture network traffic as text or pcap.

## Parameters
- `interface` (string, required, default="eth0"): Network interface.
- `filter` (string): BPF filter.
- `count` (integer, default=100): Packet count.
- `output_file` (string): Output file path.
- `verbose` (boolean, default=false): Verbose output.
- `duration` (integer): Capture duration in seconds.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "tcpdump_capture",
  "arguments": {
    "interface": "eth0",
    "filter": "host 192.168.56.10",
    "count": 100,
    "output_file": "/tmp/capture.pcap"
  }
}
```

## Notes
- Use filter, count, or duration to narrow captures.

## Related Knowledge
- [knowledge/tools/netcat.md](../../../knowledge/tools/netcat.md)
