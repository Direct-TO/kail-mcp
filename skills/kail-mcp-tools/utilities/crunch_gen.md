# `crunch_gen`

- Purpose: Generate wordlists by length, charset, or pattern.

## Parameters
- `min_length` (integer, required): Minimum length.
- `max_length` (integer, required): Maximum length.
- `charset` (string): Character set.
- `pattern` (string): Generation pattern.
- `output_file` (string): Output file path.
- `start_string` (string): Start string.
- `stop_string` (string): Stop string.
- `compress` (boolean, default=false): Compress output.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "crunch_gen",
  "arguments": {
    "min_length": 8,
    "max_length": 8,
    "charset": "abc123",
    "output_file": "/tmp/custom-wordlist.txt"
  }
}
```

## Notes
- Control length and charset to avoid oversized output files.

## Related Knowledge
- [knowledge/tools/wordlist_gen.md](../../../knowledge/tools/wordlist_gen.md)
