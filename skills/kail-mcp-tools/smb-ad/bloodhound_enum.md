# `bloodhound_enum`

- Purpose: Collect Active Directory relationship data for BloodHound analysis.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `username` (string, required): Username or username file.
- `password` (string, required): Password or password file.
- `domain` (string, required): Domain name.
- `collector` (string, default="BloodHound.py"): Collector implementation. Allowed: `BloodHound.py`.
- `collection_methods` (array<string>): Collection methods.
- `zip_filename` (string): Output ZIP filename.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "bloodhound_enum",
  "arguments": {
    "target": "dc01.example.test",
    "username": "audit",
    "password": "<known-password>",
    "domain": "example.test",
    "collection_methods": [
      "Group",
      "LocalAdmin"
    ]
  }
}
```

## Notes
- Requires valid domain credentials; output feeds BloodHound relationship analysis.

## Related Knowledge
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
