# `auto_recon`

- Purpose: Run initial reconnaissance with whois, dig, nmap, whatweb, and gobuster.

## Parameters
- `target` (string, required): Target host, IP, range, or domain, depending on the tool.
- `ports` (string): Port specification or range.
- `web_ports` (string): Ports to check for web services.
- `wordlist` (string, default="/usr/share/wordlists/dirb/common.txt"): Wordlist path.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "auto_recon",
  "arguments": {
    "target": "192.168.56.10",
    "ports": "80,443,8080",
    "web_ports": "80,443",
    "wordlist": "/usr/share/wordlists/dirb/common.txt"
  }
}
```

## Notes
- Use for a first pass; set ports and web_ports manually for large targets.

## Related Knowledge
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
