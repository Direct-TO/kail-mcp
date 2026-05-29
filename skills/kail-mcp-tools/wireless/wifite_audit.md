# `wifite_audit`

- Purpose: Run automated WiFi auditing with Wifite.

## Parameters
- `interface` (string, required, default="wlan0"): Network interface.
- `target_bssid` (string): Specific target BSSID.
- `target_channel` (integer): Specific target channel.
- `attack` (string, default="wpa"): Attack type. Allowed: `wep`, `wpa`, `wps`.
- `wordlist` (string): Wordlist path.
- `wps_pin` (boolean, default=true): Try WPS PIN attacks.
- `no_wps` (boolean, default=false): Disable WPS attacks.
- `power` (integer, default=-80): Minimum signal strength.
- `clients` (boolean, default=true): Show connected clients.
- `wep_attack` (string): Specific WEP attack. Allowed: `arp`, `chopchop`, `fragment`.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "wifite_audit",
  "arguments": {
    "interface": "wlan0",
    "attack": "wpa",
    "no_wps": true,
    "power": -70
  }
}
```

## Notes
- Use BSSID and channel filters to narrow target selection.

## Related Knowledge
- [knowledge/tools/wireless.md](../../../knowledge/tools/wireless.md)
