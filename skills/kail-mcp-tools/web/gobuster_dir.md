# `gobuster_dir`

- Purpose: Discover web directories and files with wordlists.

## Parameters
- `target_url` (string, required): Target URL.
- `wordlist` (string, default="/usr/share/wordlists/dirb/common.txt"): Wordlist path.
- `extensions` (string): File extensions to append or search.
- `threads` (integer, default=10): Thread count.
- `status_codes` (string): Positive HTTP status codes.
- `proxy` (string): Proxy URL.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "gobuster_dir",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "extensions": "php,txt",
    "threads": 10
  }
}
```

## Notes
- Choose extensions from the discovered stack, such as php, aspx, or jsp.

## Related Knowledge
- [knowledge/tools/gobuster.md](../../../knowledge/tools/gobuster.md)
