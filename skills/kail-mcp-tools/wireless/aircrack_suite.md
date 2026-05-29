# `aircrack_suite`

- Purpose: Run Aircrack-ng monitoring, capture, injection, and cracking workflows.

## Parameters
- `command` (string, required): Command to run. Allowed: `airodump`, `aireplay`, `aircrack`, `airmon`, `packetforge`.
- `interface` (string): Network interface.
- `bssid` (string): Target BSSID.
- `channel` (integer): Target channel.
- `essid` (string): Target ESSID.
- `capture_file` (string): Capture file path.
- `wordlist` (string): Wordlist path.
- `attack_type` (string): Attack type. Allowed: `deauth`, `arp`, `fragment`, `cafe`.
- `client` (string): Associated client MAC address.
- `output_prefix` (string): Output filename prefix.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "aircrack_suite",
  "arguments": {
    "command": "airodump",
    "interface": "wlan0mon",
    "output_prefix": "/tmp/wifi-audit"
  }
}
```

## Notes
- Requires a wireless adapter and monitor mode.

## Related Knowledge
- [knowledge/tools/wireless.md](../../../knowledge/tools/wireless.md)
