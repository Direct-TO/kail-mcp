# `ffuf_fuzz`

- Purpose: Run fast web fuzzing for directories, parameters, and virtual hosts.

## Parameters
- `url` (string, required): Target URL containing the FUZZ placeholder.
- `wordlist` (string, default="/usr/share/wordlists/dirb/common.txt"): Wordlist path.
- `mode` (string, default="dir"): Fuzzing mode. Allowed: `dir`, `vhost`, `param`.
- `extensions` (string): File extensions to append or search.
- `threads` (integer, default=40): Thread count.
- `filter_codes` (string, default="404"): HTTP status codes to filter out.
- `match_codes` (string): HTTP status codes to match.
- `proxy` (string): Proxy URL.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "ffuf_fuzz",
  "arguments": {
    "url": "http://192.168.56.10/FUZZ",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "mode": "dir",
    "filter_codes": "404"
  }
}
```

## Notes
- The url must contain FUZZ; vhost mode usually needs Host header handling.

## Related Knowledge
- [knowledge/tools/wfuzz.md](../../../knowledge/tools/wfuzz.md)
