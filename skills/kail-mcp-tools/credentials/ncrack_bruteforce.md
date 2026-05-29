# `ncrack_bruteforce`

- Purpose: Run high-speed network authentication cracking with Ncrack.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `service` (string, required): Target service. Allowed: `ssh`, `rdp`, `ftp`, `telnet`, `http`, `https`, `smb`, `mysql`, `vnc`.
- `user_list` (string, required): Username list path.
- `pass_list` (string, required): Password list path.
- `timing` (string, default="T3"): Timing template. Allowed: `T0`, `T1`, `T2`, `T3`, `T4`, `T5`.
- `port` (integer): Target port.
- `connections` (integer, default=5): Parameter value.
- `save` (string): File path for saving results.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "ncrack_bruteforce",
  "arguments": {
    "target": "192.168.56.10:22",
    "service": "ssh",
    "user_list": "/tmp/users.txt",
    "pass_list": "/tmp/passwords.txt",
    "timing": "T2",
    "connections": 2
  }
}
```

## Notes
- A high-speed tool; tune timing and connections deliberately.

## Related Knowledge
- [knowledge/tools/brute_alt.md](../../../knowledge/tools/brute_alt.md)
