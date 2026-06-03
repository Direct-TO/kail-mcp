"""知识库按需注入。

根据当前工具和扫描结果加载 knowledge/ 下的战术上下文，并控制注入
长度，避免小模型上下文被知识库撑爆。
"""

import logging

from .config import BASE_DIR


class KnowledgeLoader:
    """
    Loads relevant knowledge markdown files on-demand based on the current
    tool call and scan results.  Keeps injected context under a token budget
    suitable for 7B models.

    Integration point: called by MCPServer before returning tool results so
    the LLM receives tactical guidance alongside raw output.
    """

    KNOWLEDGE_DIR = BASE_DIR / "knowledge"

    # Maps every MCP tool name → its primary knowledge file (relative to KNOWLEDGE_DIR)
    TOOL_KNOWLEDGE_MAP: dict[str, str] = {
        # Recon
        "nmap_scan":          "tools/nmap.md",
        "whatweb_scan":       "tools/whatweb.md",
        "whois_lookup":       "tools/whois.md",
        "dig_lookup":         "tools/dig.md",
        # Web
        "gobuster_dir":       "tools/gobuster.md",
        "nikto_scan":         "tools/nikto.md",
        "wfuzz_scan":         "tools/wfuzz.md",
        "dirb_scan":          "tools/dirb.md",
        "owasp_zap":          "tools/web_scanners.md",
        "burpsuite":          "tools/web_scanners.md",
        "wpscan":             "tools/web_scanners.md",
        "joomscan":           "tools/web_scanners.md",
        "drupwn":             "tools/web_scanners.md",
        "droopescan":         "tools/web_scanners.md",
        "feroxbuster_scan":   "tools/web_scanners.md",
        "dirsearch_scan":     "tools/web_scanners.md",
        "pd_httpx_probe":     "tools/web_scanners.md",
        "katana_crawl":       "tools/web_scanners.md",
        "subfinder_recon":    "tools/web_scanners.md",
        "naabu_scan":         "tools/web_scanners.md",
        # Exploitation
        "sqlmap_scan":        "tools/sqlmap.md",
        "searchsploit_query": "tools/searchsploit.md",
        "cve_lookup":         "tools/cve_lookup.md",
        "msf_console":        "tools/metasploit.md",
        "msfvenom":           "tools/metasploit.md",
        "msf_db":             "tools/metasploit.md",
        "metasploit_resource":"tools/metasploit.md",
        "msf_payload_generator": "tools/metasploit.md",
        # Credential Attacks
        "hydra_attack":       "tools/hydra.md",
        "medusa":             "tools/brute_alt.md",
        "ncrack":             "tools/brute_alt.md",
        "patator":            "tools/brute_alt.md",
        "xhydra":             "tools/brute_alt.md",
        "hashcat_crack":      "tools/hashcat.md",
        "john_crack":         "tools/john.md",
        "crunch":             "tools/wordlist_gen.md",
        "cewl":               "tools/wordlist_gen.md",
        # SMB/AD/Windows
        "enum4linux_scan":    "tools/enum4linux.md",
        "smbclient":          "tools/smbclient.md",
        "smbmap":             "tools/smb_advanced.md",
        "rpcclient":          "tools/smb_advanced.md",
        "bloodhound":         "tools/ad_tools.md",
        "crackmapexec":       "tools/ad_tools.md",
        "netexec":            "tools/ad_tools.md",
        "evil_winrm":         "tools/ad_tools.md",
        "evil_winrm_shell":   "tools/ad_tools.md",
        "certipy_ad":         "tools/ad_tools.md",
        "kerbrute_enum":      "tools/ad_tools.md",
        "enum4linux_ng_scan": "tools/ad_tools.md",
        "impacket":           "tools/ad_tools.md",
        "psexec":             "tools/ad_tools.md",
        "wmiexec":            "tools/ad_tools.md",
        "smbexec":            "tools/ad_tools.md",
        "secretsdump":        "tools/ad_tools.md",
        "pth_tools":          "tools/ad_tools.md",
        # Network
        "netcat_connect":     "tools/netcat.md",
        "bettercap":          "tools/mitm.md",
        "ettercap":           "tools/mitm.md",
        "responder":          "tools/mitm.md",
        "mitmproxy":          "tools/mitm.md",
        # Wireless
        "aircrack_ng":        "tools/wireless.md",
        "reaver":             "tools/wireless.md",
        "bully":              "tools/wireless.md",
        "wifite":             "tools/wireless.md",
        # Social Engineering & C2
        "setoolkit":          "tools/social_engineering.md",
        "beef_start":         "tools/social_engineering.md",
        "empire":             "tools/social_engineering.md",
        "cobaltstrike":       "tools/social_engineering.md",
        "veil":               "tools/social_engineering.md",
        "shellter":           "tools/social_engineering.md",
        "powersploit":        "tools/social_engineering.md",
    }

    # Tools that should also load interpretation/context files
    _WEB_TOOLS = frozenset([
        "whatweb_scan", "gobuster_dir", "nikto_scan", "wfuzz_scan", "dirb_scan",
        "owasp_zap", "burpsuite", "wpscan", "joomscan", "drupwn", "droopescan",
        "ffuf_fuzz", "nuclei_scan", "feroxbuster_scan", "dirsearch_scan",
        "pd_httpx_probe", "katana_crawl", "subfinder_recon", "naabu_scan",
    ])
    _SMB_TOOLS = frozenset([
        "enum4linux_scan", "enum4linux_ng_scan", "smbclient", "smbmap", "rpcclient",
        "crackmapexec", "netexec", "evil_winrm_shell", "certipy_ad", "kerbrute_enum",
    ])
    _BRUTE_TOOLS = frozenset([
        "hydra_attack", "medusa", "ncrack", "patator", "xhydra",
    ])
    _HASH_TOOLS = frozenset(["hashcat_crack", "john_crack"])

    # Approximate tokens per character (conservative for markdown)
    _CHARS_PER_TOKEN = 3.5
    _MAX_BUDGET_TOKENS = 2500
    _MAX_BUDGET_CHARS = int(_MAX_BUDGET_TOKENS * _CHARS_PER_TOKEN)  # ~8750 chars

    def __init__(self, logger: logging.Logger) -> None:
        self._log = logger
        # In-memory cache: relative_path → file content string
        self._cache: dict[str, str] = {}

    def _load_file(self, relative_path: str) -> str:
        """Load a single knowledge file, with caching. Returns '' on missing file."""
        if relative_path in self._cache:
            return self._cache[relative_path]

        full_path = self.KNOWLEDGE_DIR / relative_path
        try:
            content = full_path.read_text(encoding="utf-8")
            self._cache[relative_path] = content
            return content
        except FileNotFoundError:
            self._log.debug("Knowledge file not found: %s", full_path)
            self._cache[relative_path] = ""
            return ""
        except Exception as exc:
            self._log.warning("Failed to read knowledge file %s: %s", full_path, exc)
            return ""

    def _truncate_to_budget(self, sections: list[str]) -> str:
        """Join sections and truncate to token budget, cutting at last full line."""
        combined = "\n\n".join(s for s in sections if s)
        if len(combined) <= self._MAX_BUDGET_CHARS:
            return combined
        # Cut at budget, then back up to last newline for clean break
        truncated = combined[:self._MAX_BUDGET_CHARS]
        last_nl = truncated.rfind("\n")
        if last_nl > self._MAX_BUDGET_CHARS // 2:
            truncated = truncated[:last_nl]
        return truncated + "\n[...truncated to fit context budget]"

    def get_context(self, tool_name: str, scan_results: str = "") -> str:
        """
        Build tactical context for a tool call.  Returns a formatted string
        ready to prepend to the tool result, or '' if no knowledge applies.

        Layers:
          1. Tool-specific knowledge (tools/*.md)
          2. Context-aware interpretation files
          3. Result-based triggers (pattern matching on scan output)
        """
        sections: list[str] = []
        loaded_files: set[str] = set()  # deduplicate

        def _add(relative_path: str) -> None:
            if relative_path not in loaded_files:
                content = self._load_file(relative_path)
                if content:
                    loaded_files.add(relative_path)
                    sections.append(content)

        # --- Layer 1: tool-specific knowledge ---
        if tool_name in self.TOOL_KNOWLEDGE_MAP:
            _add(self.TOOL_KNOWLEDGE_MAP[tool_name])

        # --- Layer 2: context-aware interpretation ---
        if tool_name == "nmap_scan":
            _add("interpretation/ports.md")
            _add("pivot_map.md")
        elif tool_name in self._WEB_TOOLS:
            _add("interpretation/web.md")
            _add("pivot_map.md")
        elif tool_name in self._SMB_TOOLS:
            _add("pivot_map.md")
        elif tool_name in self._BRUTE_TOOLS:
            _add("interpretation/auth.md")
        elif tool_name in self._HASH_TOOLS:
            _add("interpretation/auth.md")

        # --- Layer 3: result-based triggers ---
        if scan_results:
            results_lower = scan_results[:5000].lower()  # only scan first 5k chars
            if "login" in results_lower or "auth" in results_lower:
                _add("interpretation/auth.md")
            if "version" in results_lower:
                _add("tools/searchsploit.md")

        if not sections:
            return ""

        context_body = self._truncate_to_budget(sections)
        est_tokens = len(context_body) // int(self._CHARS_PER_TOKEN)
        self._log.debug(
            "Knowledge injected for '%s': %d files, ~%d tokens",
            tool_name, len(loaded_files), est_tokens,
        )
        constraints = (
            "\n---\n"
            "CONSTRAINTS:\n"
            "- You may ONLY report findings listed in the "
            "[EVIDENCE GATE] block. Do not infer, extrapolate, or fabricate "
            "additional vulnerabilities beyond what is explicitly confirmed. "
            "If EVIDENCE GATE says NO_FINDINGS=true, state: "
            "'No confirmed vulnerability. No verifiable evidence produced.' "
            "Recommendations must use conditional language "
            "('could test', 'may attempt').\n"
            "- LANGUAGE: Always respond in the SAME language the user is "
            "writing in. If the user writes in Spanish, your entire response "
            "must be in Spanish. If in English, respond in English. "
            "Only technical terms (tool names, CVEs, parameters, commands) "
            "stay in English.\n"
        )
        return (
            f"[TACTICAL CONTEXT — {tool_name}]\n"
            f"{context_body}\n"
            f"{constraints}"
            f"[END TACTICAL CONTEXT]\n"
        )
