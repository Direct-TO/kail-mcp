---
name: kail-mcp-tools
description: Use when choosing or calling the kail-mcp penetration testing tools; includes concise purposes, parameters, and examples.
---

# kail-mcp Tools

Use this skill when you need to choose, sequence, or call kail-mcp tools for security assessment, CTF, or lab work.

## How to use
1. Pick the tool from the catalog below.
2. Open the linked tool page for parameters and a minimal MCP call example.
3. Use `get_scan_history` when you need saved results; use `generate_report` when you need a Markdown report.

## Tool catalog

### Recon

| Tool | Purpose | Page |
|---|---|---|
| `auto_recon` | Run initial reconnaissance with whois, dig, nmap, whatweb, and gobuster. | [recon/auto_recon.md](recon/auto_recon.md) |
| `nmap_scan` | Scan host discovery, ports, services, and scripts with Nmap. | [recon/nmap_scan.md](recon/nmap_scan.md) |
| `masscan_scan` | Find open TCP ports quickly across large ranges. | [recon/masscan_scan.md](recon/masscan_scan.md) |
| `whois_lookup` | Look up domain or IP registration records. | [recon/whois_lookup.md](recon/whois_lookup.md) |
| `dig_lookup` | Query DNS records and resolvers. | [recon/dig_lookup.md](recon/dig_lookup.md) |
| `theharvester_recon` | Collect emails, subdomains, hosts, and employee names. | [recon/theharvester_recon.md](recon/theharvester_recon.md) |
| `whatweb_scan` | Fingerprint web technologies and application stacks. | [recon/whatweb_scan.md](recon/whatweb_scan.md) |
| `searchsploit_query` | Search the local Exploit-DB index for public exploit references. | [recon/searchsploit_query.md](recon/searchsploit_query.md) |
| `cve_lookup` | Query NVD CVE data by CVE ID, keyword, CPE, severity, or dates. | [recon/cve_lookup.md](recon/cve_lookup.md) |

### Web

| Tool | Purpose | Page |
|---|---|---|
| `nikto_scan` | Scan web servers for common findings and misconfigurations. | [web/nikto_scan.md](web/nikto_scan.md) |
| `gobuster_dir` | Discover web directories and files with wordlists. | [web/gobuster_dir.md](web/gobuster_dir.md) |
| `dirb_scan` | Discover web content with DIRB. | [web/dirb_scan.md](web/dirb_scan.md) |
| `wfuzz_scan` | Fuzz paths, parameters, virtual hosts, and other web inputs. | [web/wfuzz_scan.md](web/wfuzz_scan.md) |
| `ffuf_fuzz` | Run fast web fuzzing for directories, parameters, and virtual hosts. | [web/ffuf_fuzz.md](web/ffuf_fuzz.md) |
| `nuclei_scan` | Run template-based checks for CVEs, exposures, and misconfigurations. | [web/nuclei_scan.md](web/nuclei_scan.md) |
| `wpscan` | Scan WordPress core, plugins, themes, and users. | [web/wpscan.md](web/wpscan.md) |
| `joomscan` | Scan Joomla components and known findings. | [web/joomscan.md](web/joomscan.md) |
| `zap_scan` | Run OWASP ZAP spider, passive, active, or full web scans. | [web/zap_scan.md](web/zap_scan.md) |

### Exploitation

| Tool | Purpose | Page |
|---|---|---|
| `sqlmap_scan` | Detect and verify SQL injection with sqlmap. | [exploitation/sqlmap_scan.md](exploitation/sqlmap_scan.md) |
| `msf_console` | Run Metasploit console commands or resource scripts. | [exploitation/msf_console.md](exploitation/msf_console.md) |
| `msfvenom` | Generate Metasploit payloads with msfvenom. | [exploitation/msfvenom.md](exploitation/msfvenom.md) |
| `metasploit_resource` | Create or run Metasploit resource scripts. | [exploitation/metasploit_resource.md](exploitation/metasploit_resource.md) |

### Credentials

| Tool | Purpose | Page |
|---|---|---|
| `hydra_attack` | Run online password guessing or password spraying with Hydra. | [credentials/hydra_attack.md](credentials/hydra_attack.md) |
| `medusa_bruteforce` | Run parallel online password guessing with Medusa. | [credentials/medusa_bruteforce.md](credentials/medusa_bruteforce.md) |
| `ncrack_bruteforce` | Run high-speed network authentication cracking with Ncrack. | [credentials/ncrack_bruteforce.md](credentials/ncrack_bruteforce.md) |
| `hashcat_crack` | Crack password hashes offline with Hashcat. | [credentials/hashcat_crack.md](credentials/hashcat_crack.md) |
| `john_crack` | Crack password hashes offline and identify formats with John the Ripper. | [credentials/john_crack.md](credentials/john_crack.md) |

### SMB and AD

| Tool | Purpose | Page |
|---|---|---|
| `enum4linux_scan` | Enumerate SMB and NetBIOS users, shares, groups, and policies. | [smb-ad/enum4linux_scan.md](smb-ad/enum4linux_scan.md) |
| `crackmapexec` | Validate credentials, enumerate, and run modules across Windows or AD networks. | [smb-ad/crackmapexec.md](smb-ad/crackmapexec.md) |
| `impacket_scripts` | Run Impacket scripts for Windows or AD authentication, enumeration, and execution. | [smb-ad/impacket_scripts.md](smb-ad/impacket_scripts.md) |
| `bloodhound_enum` | Collect Active Directory relationship data for BloodHound analysis. | [smb-ad/bloodhound_enum.md](smb-ad/bloodhound_enum.md) |

### Network and MITM

| Tool | Purpose | Page |
|---|---|---|
| `netcat_connect` | Open TCP connections, listeners, and lightweight banner checks. | [network-mitm/netcat_connect.md](network-mitm/netcat_connect.md) |
| `tcpdump_capture` | Capture network traffic as text or pcap. | [network-mitm/tcpdump_capture.md](network-mitm/tcpdump_capture.md) |
| `bettercap_scan` | Run BetterCAP network discovery, sniffing, and MITM workflows. | [network-mitm/bettercap_scan.md](network-mitm/bettercap_scan.md) |
| `responder_poison` | Run Responder analysis or LLMNR, NBT-NS, and mDNS poisoning. | [network-mitm/responder_poison.md](network-mitm/responder_poison.md) |
| `ettercap_mitm` | Run Ettercap MITM attacks and plugins. | [network-mitm/ettercap_mitm.md](network-mitm/ettercap_mitm.md) |

### Wireless

| Tool | Purpose | Page |
|---|---|---|
| `aircrack_suite` | Run Aircrack-ng monitoring, capture, injection, and cracking workflows. | [wireless/aircrack_suite.md](wireless/aircrack_suite.md) |
| `wifite_audit` | Run automated WiFi auditing with Wifite. | [wireless/wifite_audit.md](wireless/wifite_audit.md) |

### Social and C2

| Tool | Purpose | Page |
|---|---|---|
| `setoolkit` | Run Social Engineering Toolkit workflows. | [social-c2/setoolkit.md](social-c2/setoolkit.md) |
| `beef_start` | Start or control the BeEF browser exploitation framework. | [social-c2/beef_start.md](social-c2/beef_start.md) |

### Utilities

| Tool | Purpose | Page |
|---|---|---|
| `shell_command` | Run simple shell commands through the MCP server. | [utilities/shell_command.md](utilities/shell_command.md) |
| `get_scan_history` | Query saved scan history from SQLite. | [utilities/get_scan_history.md](utilities/get_scan_history.md) |
| `generate_report` | Generate a Markdown report from scan history. | [utilities/generate_report.md](utilities/generate_report.md) |
| `crunch_gen` | Generate wordlists by length, charset, or pattern. | [utilities/crunch_gen.md](utilities/crunch_gen.md) |
| `cewl_gen` | Generate custom wordlists from target website content. | [utilities/cewl_gen.md](utilities/cewl_gen.md) |
