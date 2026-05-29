# `dirb_scan`

- Purpose: Discover web content with DIRB.

## Parameters
- `target_url` (string, required): Target URL.
- `wordlist` (string, default="/usr/share/wordlists/dirb/common.txt"): Wordlist path.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "dirb_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "wordlist": "/usr/share/wordlists/dirb/common.txt"
  }
}
```

## Related Knowledge
- [knowledge/tools/dirb.md](../../../knowledge/tools/dirb.md)
