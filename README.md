# kail-mcp Server

kail-mcp (Model Context Protocol) server that wraps Kali Linux penetration testing tools for authorized security assessments. Designed to be driven by a local LLM via LM Studio.

> **For AUTHORIZED penetration testing, CTF competitions, and security research ONLY.**

---

## Quick Start (Docker)

```bash
git clone <repo-url> kail-mcp
cd kail-mcp
docker compose up
```

That's it. No manual dependency installation required.

---

## Architecture

```
┌─────────────┐     JSON-RPC       ┌──────────────────┐      exec      ┌────────────┐
│  LM Studio  │ ◄──── stdin/out ──►│  MCP Server      │ ◄────────────► │ Kali Tools │
│  (local LLM)│                    │  (Python 3)      │                │ MCP tools  │
└─────────────┘                    │                  │                │ nmap, msf, │
                                   │  knowledge/      │                │ bettercap..│
                                   │  (tactical KB)   │                └────────────┘
                                   └───────┬──────────┘
                                           │
                                    ┌──────▼──────┐
                                    │  SQLite DB  │
                                    │  + Reports  │
                                    └─────────────┘
```

---

## Docker Setup

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2+
- 8 GB RAM minimum (Metasploit alone needs ~2 GB)

### Build & Run

```bash
# Build and start
docker compose up

# Build and start in background
docker compose up -d

# Rebuild after code changes
docker compose up -d --build --force-recreate

# View logs
docker compose logs -f

# Open a shell inside the container (for debugging)
docker compose exec mcp-server zsh

# Stop
docker compose down
```

### Faster Rebuilds & Migration

The full image installs a large Kali toolchain, so the first build, or any change to the tool install layers, can take a long time. Normal MCP code changes are in the final application layer and Docker should reuse the heavy cached layers.

For repeated code-only rebuilds, keep a separate tool baseline image:

```bash
# Build the heavy tool baseline once
sh scripts/build-tools-base.sh

# Rebuild only the MCP application layer from that baseline
docker compose -f docker-compose.yml -f docker-compose.fast.yml up -d --build --force-recreate
```

For another computer, export/import the image instead of downloading all tools again:

```bash
# Source machine
sh scripts/export-image.sh kail-mcp-images.tar.gz

# Target machine
sh scripts/import-image.sh kail-mcp-images.tar.gz
docker compose up -d
```

If you built only `kail-mcp:latest` and want to use it as the fast-rebuild baseline:

```bash
sh scripts/promote-tools-base.sh
```

### Environment Variables

Override any setting without modifying `config.yaml`:

| Variable | Default | Description |
|---|---|---|
| `MCP_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MCP_DATABASE` | `/opt/kail-mcp/data/scan_results.db` | SQLite database path |
| `MCP_AUDIT_LOG` | `/opt/kail-mcp/data/audit.log` | Audit trail file path |
| `MCP_REPORT_DIR` | `/opt/kail-mcp/reports` | Directory for generated reports |
| `MCP_CONFIG_PATH` | `/opt/kail-mcp/config.yaml` | Path to YAML config file |

Example with overrides:

```bash
MCP_LOG_LEVEL=DEBUG docker compose up
```

Or add to a `.env` file in the project root:

```env
MCP_LOG_LEVEL=DEBUG
```

### Persistent Data

Two Docker volumes keep data across container restarts:

| Volume | Container Path | Contents |
|---|---|---|
| `mcp-data` | `/opt/kail-mcp/data/` | SQLite scan database, audit log |
| `mcp-reports` | `/opt/kail-mcp/reports/` | Generated markdown reports |

To back up your data:

```bash
# Copy database out of the container
docker compose cp mcp-server:/opt/kail-mcp/data/scan_results.db ./backup.db

# Copy reports
docker compose cp mcp-server:/opt/kail-mcp/reports/ ./reports-backup/
```

To wipe all data and start fresh:

```bash
docker compose down -v
```

### Configuration

The `config.yaml` file is bind-mounted read-only into the container. Edit it on your host and restart:

```bash
# Edit config
vim config.yaml

# Restart to pick up changes
docker compose restart
```

Key config sections:

```yaml
security:
  allowed_scope:          # CIDR ranges the server is allowed to scan
    - "192.168.0.0/16"
    - "10.0.0.0/8"
    - "172.16.0.0/12"
  require_scope_check: true

rate_limit:
  global_max_concurrent: 3
  per_tool_max_concurrent: 1
```

### Networking

By default the container runs with `network_mode: host` so it can scan your local network. If you only scan remote targets or want isolation, change to bridge mode in `docker-compose.yml`:

```yaml
services:
  mcp-server:
    # network_mode: host    # comment out
    ports:
      - "8080:8080"         # if you add an HTTP transport later
```

### Metasploit Database (Optional)

Metasploit works out of the box with its built-in database. For a dedicated PostgreSQL instance, uncomment the `msf-db` service in `docker-compose.yml`:

```bash
# Edit docker-compose.yml — uncomment the msf-db service and depends_on
vim docker-compose.yml
docker compose up
```

---

## Installed MCP Tools (45 exposed)

The container includes these Kali tools (auto-detected at startup):

| Category | Tools |
|---|---|
| **Recon** | nmap, masscan, whatweb, whois, dig, theHarvester, searchsploit |
| **CVE Intelligence** | cve_lookup (NVD 2.0 API — exact CVE ID, keyword+exact_match, cpe_name, virtual_match_string, cvss_severity filter, publication and modification date ranges, no_rejected flag; returns CVSS, SERVICE BINDING annotation, CPEs, references) |
| **Web Scanning** | gobuster, ffuf, nuclei, nikto, dirb, wfuzz, wpscan, joomscan, zaproxy |
| **Exploitation** | sqlmap, metasploit (msfconsole, msfvenom) |
| **Credential Attacks** | hydra, medusa, ncrack, hashcat, john, crunch, cewl |
| **SMB / AD** | enum4linux, smbclient, smbmap, crackmapexec, bloodhound-python, impacket example scripts |
| **MITM** | bettercap, ettercap, responder |
| **Wireless** | aircrack-ng, wifite |
| **C2 / Social Engineering** | beef-xss, setoolkit |
| **Proxy Routing** | proxychains4 (Burp profile `/etc/proxychains4.conf` + Tor profile `/etc/proxychains4-tor.conf`) |
| **Network** | tcpdump, netcat, socat |
| **Wordlists** | rockyou.txt, dirb lists |

Tools not installed are automatically hidden from the MCP tool list.

### Tools Not Available in Docker

The following tools from the registry **cannot run** in a Docker container and are auto-hidden:

| Tool | Reason |
|---|---|
| `mimikatz` | Windows-only binary |
| `cobaltstrike` | Commercial license required |
| `burpsuite` | Runs on the Windows host separately; its MCP server is added as an independent server in the host UI — not part of kail-mcp |
| `powersploit` | PowerShell modules, not a Linux binary |
| `empire` | Deprecated / complex install |
| `shellter` | Windows PE injector (Wine-dependent) |
| `xhydra` | GTK GUI, useless headless |
| `pyrit`, `ewsa` | Deprecated / unavailable in repos |
| `zap-cli`, `evil-winrm`, `patator`, `mitmproxy`, `ngrep`, `hping3`, `fragrouter`, `macchanger`, `veil`, `kismet`, `reaver`, `bully`, `pixiewps`, `cowpatty`, `wireshark-common`, `seclists` | Not exposed by this MCP server, too heavy for the default image, GUI-dependent, or unsuitable for portable Docker use |
| `wifiphisher`, `fluxion`, `airgeddon`, `wifi-honey`, `ghost-phisher`, `fern-wifi-cracker` | Not in Kali repos or require GUI |

### Shell Environment

The container runs **zsh** as the default shell with:

- **`zsh-syntax-highlighting`**: commands turn green when valid, red when invalid — real-time feedback before you press Enter
- **`zsh-autosuggestions`**: suggests commands from history; press Tab or → to accept

When the host UI's Docker Terminal opens a session it detects the shell in order: **zsh → bash → sh**.

```bash
# Open an interactive zsh session
docker exec -it kail-mcp zsh
```

### Proxy Routing (proxychains4)

Two ready-made profiles are installed for routing tool traffic without modifying tool configuration:

| Profile | Path | Target |
|---------|------|--------|
| Burp | `/etc/proxychains4.conf` | `127.0.0.1:8080` (Windows host Burp proxy) |
| Tor | `/etc/proxychains4-tor.conf` | `127.0.0.1:9050` (Tor SOCKS in container) |

**Usage:**

```bash
# Route through Burp for traffic analysis
proxychains nmap -sV 10.10.10.1

# Route through Tor for anonymity
proxychains -f /etc/proxychains4-tor.conf curl https://example.com

# Chain tool → Burp → Tor (configure Burp SOCKS upstream first)
# In Burp: Settings → Network → Connections → SOCKS proxy → 127.0.0.1:9050
proxychains nmap -sV 10.10.10.1
```

The `gobuster_dir` MCP tool accepts a `proxy` parameter to route directory bruteforce through a proxy directly (e.g., `http://127.0.0.1:8080` for Burp or `socks5://127.0.0.1:9050` for Tor) — no proxychains required for that tool.

Because the container uses `network_mode: host`, `127.0.0.1` inside the container resolves to the Windows/Linux host, so Burp running on the host is reachable at `127.0.0.1:8080`.

### Wireless Tools Caveat

Wireless tools (aircrack-ng, reaver, wifite, etc.) are **installed** but require USB WiFi adapter passthrough to function. Uncomment the following in `docker-compose.yml`:

```yaml
privileged: true
devices:
  - /dev/bus/usb:/dev/bus/usb
```

Without a physical adapter passed through, wireless tools will start but have no interfaces to work with.

---

## Knowledge Base

The `knowledge/` directory contains a tactical reasoning system for the LLM:

```
knowledge/
  core_principles.md      — Decision axioms
  engagement_rules.md     — Scope & risk rules
  pivot_map.md            — "If X found → do Y" decision trees
  tools/*.md              — Per-tool tactical memory
  interpretation/*.md     — Result parsing guides
  tactics/*.md            — Phase-by-phase methodology
```

The `tools/cve_lookup.md` file provides the LLM with NVD 2.0 query strategy, all supported parameters with examples, CVSS severity bands, the CVE Query Lock decision sequence (extract product → extract version → build query), SERVICE BINDING rules (bind CVE only to matching detected service), evidence rules, and chaining workflows (nmap version → cve_lookup → searchsploit).

See `knowledge/README.md` for the full structure and integration guide.

---

## LM Studio Integration

1. Start LM Studio and load a model (e.g., Qwen 2.5 7B, Mistral 7B)
2. Enable the MCP server in LM Studio's tool settings
3. Point it to the MCP server's stdin/stdout interface
4. The LLM can now call penetration testing tools via the MCP protocol

---

## Project Structure

```
kail-mcp/
├── Dockerfile              ← Kali-based container image (60+ tools)
├── docker-compose.yml      ← One-command startup + optional PostgreSQL
├── docker-entrypoint.sh    ← Startup checks & tool verification
├── .dockerignore           ← Build context exclusions
├── config.yaml             ← Server configuration
├── requirements.txt        ← Python dependencies
├── mcp_server.py           ← MCP server (2900+ lines, 45 registered tools)
├── knowledge/              ← Tactical knowledge base (27 files)
│   ├── core_principles.md
│   ├── pivot_map.md
│   ├── tools/
│   ├── interpretation/
│   └── tactics/
└── README.md               ← This file
```

---

## Security

- **Scope enforcement**: Every tool call is checked against `allowed_scope` in config
- **Hostname resolution**: Domains are resolved to IPs before scope check (prevents bypass)
- **Input sanitization**: Shell metacharacters are stripped from all inputs
- **Rate limiting**: Concurrent tool execution is capped (global + per-tool)
- **Audit logging**: Every tool invocation is recorded with timestamp and arguments
- **Risk levels**: High-risk tools (hydra, sqlmap, metasploit, bettercap, etc.) emit warnings via stderr
- **Binary availability**: Only tools actually installed in the container are exposed via MCP
