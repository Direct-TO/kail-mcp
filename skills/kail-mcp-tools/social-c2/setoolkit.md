# `setoolkit`

- Purpose: Run Social Engineering Toolkit workflows.

## Parameters
- `attack_vector` (integer, required): Attack vector selection. Allowed: `1`, `2`, `3`, `4`, `5`.
- `web_attack_type` (integer): Web attack type selection. Allowed: `1`, `2`, `3`, `4`.
- `clone_url` (string): URL to clone.
- `payload` (string): Payload name.
- `lhost` (string): Listener host IP.
- `lport` (integer): Listener port.
- `email_template` (string): Email template.
- `target_email` (string): Target email address.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "setoolkit",
  "arguments": {
    "attack_vector": 2,
    "web_attack_type": 3,
    "clone_url": "http://192.168.56.10"
  }
}
```

## Notes
- Supports mail, cloned pages, and credential collection workflows.

## Related Knowledge
- [knowledge/tools/social_engineering.md](../../../knowledge/tools/social_engineering.md)
