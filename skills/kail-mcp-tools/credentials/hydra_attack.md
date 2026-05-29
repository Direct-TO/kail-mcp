# `hydra_attack`

- Purpose: Run online password guessing or password spraying with Hydra.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `service` (string, required): Target service. Allowed: `ssh`, `ftp`, `http-get`, `http-post`, `http-post-form`, `smb`, `rdp`, `mysql`, `mssql`, `postgres`, `vnc`, `telnet`, `smtp`, `pop3`, `imap`.
- `port` (integer): Target port.
- `username` (string): Username or username file.
- `username_list` (string): Username list path.
- `password_list` (string, required): Password list path.
- `threads` (integer, default=4): Thread count.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "hydra_attack",
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
- Use threads to control concurrency; password spraying is also supported.

## Related Knowledge
- [knowledge/tools/hydra.md](../../../knowledge/tools/hydra.md)
