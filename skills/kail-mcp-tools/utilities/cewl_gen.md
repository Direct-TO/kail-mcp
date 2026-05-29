# `cewl_gen`

- Purpose: Generate custom wordlists from target website content.

## Parameters
- `target_url` (string, required): Target URL.
- `depth` (integer, default=2): Spider depth.
- `min_word_length` (integer, default=3): Minimum word length.
- `max_word_length` (integer, default=20): Maximum word length.
- `output_file` (string): Output file path.
- `with_numbers` (boolean, default=false): Include numbers.
- `email_addresses` (boolean, default=false): Extract email addresses.
- `meta_data` (boolean, default=false): Extract metadata.
- `user_agent` (string): Custom user agent.
- `proxy` (string): Proxy URL.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "cewl_gen",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "depth": 1,
    "min_word_length": 5,
    "output_file": "/tmp/site-words.txt"
  }
}
```

## Notes
- Useful for building dictionaries from target-specific website language.

## Related Knowledge
- [knowledge/tools/wordlist_gen.md](../../../knowledge/tools/wordlist_gen.md)
