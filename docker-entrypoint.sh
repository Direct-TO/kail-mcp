#!/bin/bash
# ============================================================================
# Rami-Kali MCP Server — Docker Entrypoint
# ============================================================================
# Runs startup checks and launches the MCP server.
# ============================================================================

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║       Rami-Kali MCP Server v2.1 — Docker Edition      ║"
echo "║  For AUTHORIZED penetration testing & CTFs ONLY      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Ensure data directories exist ──────────────────────────────────────────
mkdir -p "$(dirname "${MCP_DATABASE:-/opt/kail-mcp/data/scan_results.db}")"
mkdir -p "${MCP_REPORT_DIR:-/opt/kail-mcp/reports}"

# ── Tool availability check ───────────────────────────────────────────────
echo -e "${BOLD}[*] Checking installed tools...${NC}"

MCP_TOOLS=(
    # Format: mcp_tool_name|required_command_or_absolute_path.
    # Blank requirements are metadata/server tools that are always exposed.
    "nmap_scan|nmap"
    "nikto_scan|nikto"
    "gobuster_dir|gobuster"
    "sqlmap_scan|sqlmap"
    "hydra_attack|hydra"
    "enum4linux_scan|enum4linux"
    "wfuzz_scan|wfuzz"
    "netcat_connect|nc"
    "searchsploit_query|searchsploit"
    "cve_lookup|"
    "hashcat_crack|hashcat"
    "john_crack|john"
    "dirb_scan|dirb"
    "whatweb_scan|whatweb"
    "whois_lookup|whois"
    "dig_lookup|dig"
    "shell_command|"
    "auto_recon|nmap"
    "get_scan_history|"
    "generate_report|"
    "msf_console|msfconsole"
    "msfvenom|msfvenom"
    "metasploit_resource|msfconsole"
    "bettercap_scan|bettercap"
    "responder_poison|responder"
    "crackmapexec|crackmapexec"
    "impacket_scripts|/usr/share/doc/python3-impacket/examples/psexec.py"
    "bloodhound_enum|bloodhound-python"
    "wpscan|wpscan"
    "joomscan|joomscan"
    "zap_scan|zaproxy"
    "medusa_bruteforce|medusa"
    "ncrack_bruteforce|ncrack"
    "setoolkit|setoolkit"
    "beef_start|beef-xss"
    "tcpdump_capture|tcpdump"
    "ettercap_mitm|ettercap"
    "aircrack_suite|aircrack-ng"
    "wifite_audit|wifite"
    "crunch_gen|crunch"
    "cewl_gen|cewl"
    "masscan_scan|masscan"
    "feroxbuster_scan|feroxbuster"
    "dirsearch_scan|dirsearch"
    "ffuf_fuzz|ffuf"
    "nuclei_scan|nuclei"
    "subfinder_recon|subfinder"
    "naabu_scan|naabu"
    "pd_httpx_probe|pd-httpx"
    "katana_crawl|katana"
    "netexec|netexec"
    "evil_winrm_shell|evil-winrm"
    "certipy_ad|certipy-ad"
    "kerbrute_enum|kerbrute"
    "enum4linux_ng_scan|enum4linux-ng"
    "theharvester_recon|theHarvester"
)

available=0
missing=0

for entry in "${MCP_TOOLS[@]}"; do
    tool="${entry%%|*}"
    probe="${entry#*|}"

    if [ -z "$probe" ]; then
        ((available++)) || true
    elif [[ "$probe" == */* ]] && [ -e "$probe" ]; then
        ((available++)) || true
    elif [[ "$probe" != */* ]] && command -v "$probe" &>/dev/null; then
        ((available++)) || true
    else
        echo -e "  ${YELLOW}[!] Not found: ${tool} requires ${probe}${NC}"
        ((missing++)) || true
    fi
done

total=$((available + missing))
echo -e "  ${GREEN}[+] MCP tool dependencies available: ${available}/${total}${NC}"

if [ "$missing" -gt 0 ]; then
    echo -e "  ${YELLOW}[!] Missing tools are reported only; MCP tools remain exposed in this test build.${NC}"
fi

echo ""
echo -e "${BOLD}[*] Checking tool resource packs...${NC}"
if [ -d /usr/share/seclists ]; then
    echo -e "  ${GREEN}[+] SecLists: /usr/share/seclists${NC}"
else
    echo -e "  ${YELLOW}[!] SecLists not found at /usr/share/seclists${NC}"
fi
if [ -d /usr/share/nuclei-templates ]; then
    echo -e "  ${GREEN}[+] Nuclei templates: /usr/share/nuclei-templates${NC}"
else
    echo -e "  ${YELLOW}[!] Nuclei templates not found at /usr/share/nuclei-templates${NC}"
fi

# ── Platform/commercial tools (never available in Docker) ──────────────────
echo ""
echo -e "  ${CYAN}[i] Not available in Docker (platform/commercial):${NC}"
echo -e "  ${CYAN}    mimikatz (Windows), cobaltstrike (commercial), burpsuite (GUI),${NC}"
echo -e "  ${CYAN}    powersploit (PowerShell), empire (deprecated), shellter (Windows),${NC}"
echo -e "  ${CYAN}    xhydra (GUI), pyrit/ewsa (deprecated)${NC}"

# ── Initialize Metasploit database if available ────────────────────────────
if command -v msfconsole &>/dev/null; then
    echo ""
    echo -e "${BOLD}[*] Initializing Metasploit database...${NC}"
    if service postgresql start 2>/dev/null; then
        msfdb init 2>/dev/null && \
            echo -e "  ${GREEN}[+] Metasploit database ready${NC}" || \
            echo -e "  ${YELLOW}[!] msfdb init failed — Metasploit will work without DB${NC}"
    else
        echo -e "  ${YELLOW}[!] PostgreSQL not running — Metasploit will work without DB${NC}"
    fi
fi

# ── Configuration summary ─────────────────────────────────────────────────
echo ""
echo -e "${BOLD}[*] Configuration:${NC}"
echo -e "  Config:    ${MCP_CONFIG_PATH:-/opt/kail-mcp/config.yaml}"
echo -e "  Database:  ${MCP_DATABASE:-/opt/kail-mcp/data/scan_results.db}"
echo -e "  Reports:   ${MCP_REPORT_DIR:-/opt/kail-mcp/reports}"
echo -e "  Log level: ${MCP_LOG_LEVEL:-INFO}"
echo ""

# ── Knowledge base check ──────────────────────────────────────────────────
KB_DIR="/opt/kail-mcp/knowledge"
if [ -d "$KB_DIR" ]; then
    kb_files=$(find "$KB_DIR" -name "*.md" | wc -l)
    echo -e "  ${GREEN}[+] Knowledge base: ${kb_files} files loaded${NC}"
else
    echo -e "  ${YELLOW}[!] Knowledge base not found at ${KB_DIR}${NC}"
fi

# ── Tor check ─────────────────────────────────────────────────────────────
if command -v tor &>/dev/null; then
    tor_ver=$(tor --version 2>/dev/null | head -1)
    echo -e "  ${GREEN}[+] Tor: ${tor_ver}${NC}"
    echo -e "  ${CYAN}[i] Transparent proxy ready (TransPort 9040, DNSPort 5353)${NC}"
else
    echo -e "  ${YELLOW}[!] Tor not found — transparent proxy unavailable${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}[*] Starting MCP server (stdin/stdout JSON-RPC)...${NC}"
echo -e "${BOLD}─────────────────────────────────────────────────────${NC}"
echo ""

# ── Launch the server ─────────────────────────────────────────────────────
exec python3 mcp_server.py "$@"
