"""工具二进制可用性检查。

启动时检查 Kali/安全工具是否存在；即使缺失也继续暴露 MCP tool，
让调用方能看到明确的运行时错误或安装缺口。
"""

import logging
import shutil
from pathlib import Path
from typing import Any


TOOL_BINARY_MAP: dict[str, Any] = {
    "nmap_scan": "nmap",
    "nikto_scan": "nikto",
    "gobuster_dir": "gobuster",
    "sqlmap_scan": "sqlmap",
    "hydra_attack": "hydra",
    "enum4linux_scan": "enum4linux",
    "wfuzz_scan": "wfuzz",
    "netcat_connect": "nc",
    "searchsploit_query": "searchsploit",
    "hashcat_crack": "hashcat",
    "john_crack": "john",
    "dirb_scan": "dirb",
    "whatweb_scan": "whatweb",
    "whois_lookup": "whois",
    "dig_lookup": "dig",
    "shell_command": None,         # always available
    "auto_recon": "nmap",          # needs at least nmap
    "get_scan_history": None,      # no binary needed
    "generate_report": None,       # no binary needed

    "msf_console": "msfconsole",
    "msfvenom": "msfvenom",
    "metasploit_resource": "msfconsole",
    "bettercap_scan": "bettercap",
    "responder_poison": "responder",
    "crackmapexec": "crackmapexec",
    "impacket_scripts": "/usr/share/doc/python3-impacket/examples/psexec.py",
    "bloodhound_enum": "bloodhound-python",
    "wpscan": "wpscan",
    "joomscan": "joomscan",
    "zap_scan": "zaproxy",
    "medusa_bruteforce": "medusa",
    "ncrack_bruteforce": "ncrack",
    "setoolkit": "setoolkit",
    "beef_start": "beef-xss",
    "tcpdump_capture": "tcpdump",
    "ettercap_mitm": "ettercap",
    "aircrack_suite": "aircrack-ng",
    "wifite_audit": "wifite",
    "crunch_gen": "crunch",
    "cewl_gen": "cewl",
    "masscan_scan": "masscan",
    "feroxbuster_scan": "feroxbuster",
    "dirsearch_scan": "dirsearch",
    "ffuf_fuzz": "ffuf",
    "nuclei_scan": "nuclei",
    "subfinder_recon": "subfinder",
    "naabu_scan": "naabu",
    "pd_httpx_probe": "pd-httpx",
    "katana_crawl": "katana",
    "netexec": "netexec",
    "evil_winrm_shell": "evil-winrm",
    "certipy_ad": "certipy-ad",
    "kerbrute_enum": "kerbrute",
    "enum4linux_ng_scan": "enum4linux-ng",
    "theharvester_recon": "theHarvester",
    "cve_lookup": None,
}


def _binary_exists(binary: Any) -> bool:
    if binary is None:
        return True
    if isinstance(binary, (list, tuple, set)):
        return any(_binary_exists(candidate) for candidate in binary)

    binary_str = str(binary)
    if "/" in binary_str:
        return Path(binary_str).exists()
    return shutil.which(binary_str) is not None


def _binary_label(binary: Any) -> str:
    if isinstance(binary, (list, tuple, set)):
        return " | ".join(str(candidate) for candidate in binary)
    return str(binary)


def check_available_binaries(logger: logging.Logger) -> dict[str, bool]:
    """Check which tool binaries are available on the system."""
    available: dict[str, bool] = {}
    for tool_name, binary in TOOL_BINARY_MAP.items():
        found = _binary_exists(binary)
        available[tool_name] = found
        if not found:
            logger.warning("Binary '%s' not found for tool '%s'. Tool remains exposed.", _binary_label(binary), tool_name)
        else:
            logger.info("Binary '%s' found for tool '%s'.", _binary_label(binary), tool_name)
    return available
