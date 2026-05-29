# `hashcat_crack`

- Purpose: Crack password hashes offline with Hashcat.

## Parameters
- `hash_file` (string, required): File containing hashes.
- `hash_type` (integer, required): Hashcat hash type code.
- `wordlist` (string, required): Wordlist path.
- `rules` (string): Hashcat rule file path.
- `extra_args` (string): Additional tool arguments.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "hashcat_crack",
  "arguments": {
    "hash_file": "/tmp/hashes.txt",
    "hash_type": 0,
    "wordlist": "/usr/share/wordlists/rockyou.txt"
  }
}
```

## Notes
- Identify hash_type first; the wrong mode wastes time.

## Related Knowledge
- [knowledge/tools/hashcat.md](../../../knowledge/tools/hashcat.md)
