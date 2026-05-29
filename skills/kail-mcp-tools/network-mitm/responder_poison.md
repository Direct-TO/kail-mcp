# `responder_poison`

- Purpose: Run Responder analysis or LLMNR, NBT-NS, and mDNS poisoning.

## Parameters
- `interface` (string, required, default="eth0"): Network interface.
- `mode` (string, default="poison"): Responder mode. Allowed: `analyze`, `poison`.
- `services` (array<string>): Services to enable.
- `wpad` (boolean, default=true): Enable WPAD server behavior.
- `fingerprint` (boolean, default=true): Enable fingerprinting.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "responder_poison",
  "arguments": {
    "interface": "eth0",
    "mode": "analyze",
    "wpad": false,
    "fingerprint": true
  }
}
```

## Notes
- analyze mode observes traffic; poison mode performs poisoning.

## Related Knowledge
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
