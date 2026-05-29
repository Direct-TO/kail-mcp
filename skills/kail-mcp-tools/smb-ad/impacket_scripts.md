# `impacket_scripts`

- Purpose: Run Impacket scripts for Windows or AD authentication, enumeration, and execution.

## Parameters
- `script` (string, required): Script name. Allowed: `psexec.py`, `wmiexec.py`, `smbexec.py`, `secretsdump.py`, `GetUserSPNs.py`, `GetNPUsers.py`, `ticketer.py`, `raiseChild.py`.
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `username` (string): Username or username file.
- `password` (string): Password or password file.
- `hash` (string): NTLM hash.
- `domain` (string): Domain name.
- `command` (string): Command to run.
- `port` (integer): Target port.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "impacket_scripts",
  "arguments": {
    "script": "GetNPUsers.py",
    "target": "dc01.example.test",
    "domain": "EXAMPLE",
    "username": "audit",
    "password": "<known-password>"
  }
}
```

## Notes
- Each script has different options; use extra_args for script-specific flags.

## Related Knowledge
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
- [knowledge/tools/smb_advanced.md](../../../knowledge/tools/smb_advanced.md)
