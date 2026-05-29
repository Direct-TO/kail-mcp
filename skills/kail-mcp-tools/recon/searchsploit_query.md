# `searchsploit_query`

- Purpose: Search the local Exploit-DB index for public exploit references.

## Parameters
- `query` (string, required): Search terms.
- `exact` (boolean, default=false): Use exact matching.
- `json_output` (boolean, default=true): Return JSON output.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "searchsploit_query",
  "arguments": {
    "query": "OpenSSH 7.9",
    "exact": false,
    "json_output": true
  }
}
```

## Related Knowledge
- [knowledge/tools/searchsploit.md](../../../knowledge/tools/searchsploit.md)
