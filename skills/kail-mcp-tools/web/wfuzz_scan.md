# `wfuzz_scan`

- Purpose: Fuzz paths, parameters, virtual hosts, and other web inputs.

## Parameters
- `target_url` (string, required): Target URL.
- `wordlist` (string, required): Wordlist path.
- `hide_codes` (string): Response codes to hide.
- `hide_chars` (string): Character count to hide.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "wfuzz_scan",
  "arguments": {
    "target_url": "http://192.168.56.10/FUZZ",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "hide_codes": "404"
  }
}
```

## Notes
- The target_url must contain FUZZ; hide obvious 404 or 302 noise first.

## Related Knowledge
- [knowledge/tools/wfuzz.md](../../../knowledge/tools/wfuzz.md)
