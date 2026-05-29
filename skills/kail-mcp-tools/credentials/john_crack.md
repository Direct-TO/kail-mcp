# `john_crack`

- Purpose: Crack password hashes offline and identify formats with John the Ripper.

## Parameters
- `hash_file` (string, required): File containing hashes.
- `wordlist` (string): Wordlist path.
- `format` (string): John hash format.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "john_crack",
  "arguments": {
    "hash_file": "/tmp/hashes.txt",
    "wordlist": "/usr/share/wordlists/rockyou.txt",
    "format": "raw-md5"
  }
}
```

## Notes
- Let John auto-detect uncertain formats first, then add format if needed.

## Related Knowledge
- [knowledge/tools/john.md](../../../knowledge/tools/john.md)
