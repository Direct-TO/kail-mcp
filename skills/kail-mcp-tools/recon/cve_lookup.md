# `cve_lookup`

- Purpose: Query NVD CVE data by CVE ID, keyword, CPE, severity, or dates.

## Parameters
- `cve_id` (string): Exact CVE identifier.
- `keyword` (string): Keyword search string.
- `exact_match` (boolean, default=false): Require an exact keyword match.
- `cpe_name` (string): CPE 2.3 name filter.
- `virtual_match_string` (string): CPE match string filter.
- `cvss_severity` (string): CVSS v3 severity filter. Allowed: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- `pub_start_date` (string): Publication start date in YYYY-MM-DD format.
- `pub_end_date` (string): Publication end date in YYYY-MM-DD format.
- `last_mod_start_date` (string): Last-modified start date in YYYY-MM-DD format.
- `last_mod_end_date` (string): Last-modified end date in YYYY-MM-DD format.
- `no_rejected` (boolean, default=false): Exclude rejected CVEs.
- `max_results` (integer, default=5): Maximum result count.

## Example
Use through MCP `tools/call`:

```json
{
  "name": "cve_lookup",
  "arguments": {
    "keyword": "OpenSSH 7.9",
    "cvss_severity": "HIGH",
    "no_rejected": true,
    "max_results": 5
  }
}
```

## Notes
- Prefer product plus version, or an exact CPE, to reduce false matches.

## Related Knowledge
- [knowledge/tools/cve_lookup.md](../../../knowledge/tools/cve_lookup.md)
