# `crackmapexec`

- Purpose: Validate credentials, enumerate, and run modules across Windows or AD networks.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `protocol` (string, default="smb"): Protocol to use. Allowed: `smb`, `ssh`, `winrm`, `mssql`, `ldap`, `ftp`.
- `username` (string): Username or username file.
- `password` (string): Password or password file.
- `hash` (string): NTLM hash.
- `module` (string): Module name.
- `command` (string): Command to run.
- `exec_method` (string): Execution method. Allowed: `wmiexec`, `smbexec`, `atexec`, `psexec`.
- `port` (integer): Target port.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "crackmapexec",
  "arguments": {
    "target": "192.168.56.10",
    "protocol": "smb",
    "username": "audit",
    "password": "<known-password>"
  }
}
```

## Notes
- Can validate credentials, enumerate, execute commands, dump data, and run modules.

## Related Knowledge
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
