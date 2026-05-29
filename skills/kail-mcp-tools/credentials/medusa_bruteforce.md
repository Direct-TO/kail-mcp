# `medusa_bruteforce`

- Purpose: Run parallel online password guessing with Medusa.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `service` (string, required): Target service. Allowed: `ssh`, `ftp`, `telnet`, `http`, `pop3`, `imap`, `smb`, `mysql`, `mssql`, `postgres`.
- `username` (string): Username or username file.
- `user_list` (string): Username list path.
- `password_list` (string, required): Password list path.
- `port` (integer): Target port.
- `threads` (integer, default=5): Thread count.
- `timeout` (integer, default=10): Timeout in seconds.
- `verbose` (boolean, default=false): Verbose output.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "medusa_bruteforce",
  "arguments": {
    "target": "192.168.56.10",
    "service": "ssh",
    "username": "test",
    "password_list": "/usr/share/wordlists/rockyou.txt",
    "threads": 2
  }
}
```

## Notes
- Similar to hydra_attack, and useful for parallel attempts.

## Related Knowledge
- [knowledge/tools/brute_alt.md](../../../knowledge/tools/brute_alt.md)
