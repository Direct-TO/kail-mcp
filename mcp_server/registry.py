"""MCP 工具目录。

这里集中保存 tools/list 返回的 JSON Schema。拆分时保持原 schema 文本
不变，避免影响外部客户端和已有提示词。
"""

from typing import Any, Optional


class ToolRegistry:
    """Stores JSON Schema definitions for all MCP tools."""

    def __init__(self, available_binaries: Optional[dict[str, bool]] = None) -> None:
        self._tools: list[dict[str, Any]] = []
        self._available = available_binaries or {}
        self._build()

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._tools

    def get(self, name: str) -> Optional[dict]:
        for t in self._tools:
            if t["name"] == name:
                return t
        return None

    def _add(self, name: str, description: str, schema: dict) -> None:
        self._tools.append({
            "name": name,
            "description": description,
            "inputSchema": {"type": "object", **schema},
        })

    def _build(self) -> None:
        self._add("nmap_scan", "Run an Nmap scan against a target host or network.", {
            "properties": {
                "target": {"type": "string", "description": "IP, CIDR, or hostname to scan."},
                "scan_type": {
                    "type": "string",
                    "enum": ["quick", "full", "stealth", "vuln", "scripts", "discovery", "udp"],
                    "description": (
                        "Scan profile: "
                        "quick=-sS -sV --top-ports 1000; "
                        "full=-sS -sV -sC -p-; "
                        "stealth=-sS -sV (SYN only); "
                        "vuln=-sS -sV --script vuln; "
                        "scripts=-sS -sV -sC; "
                        "discovery=-sn (host-only, NO port scan — use for subnets); "
                        "udp=-sU --top-ports 50."
                    ),
                    "default": "quick",
                },
                "ports": {"type": "string", "description": "Port specification (e.g. '80,443' or '1-1024')."},
                "timing": {
                    "type": "string",
                    "enum": ["T0", "T1", "T2", "T3", "T4", "T5"],
                    "description": "Nmap timing template.",
                    "default": "T3",
                },
                "scripts": {"type": "string", "description": "NSE scripts to run (comma-separated)."},
                "extra_args": {"type": "string", "description": "Additional Nmap arguments."},
            },
            "required": ["target"],
        })

        self._add("nikto_scan", "Run Nikto web-server vulnerability scanner.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL (http/https)."},
                "tuning": {"type": "string", "description": "Nikto tuning options."},
                "max_time": {"type": "integer", "description": "Max scan time in seconds."},
                "extra_args": {"type": "string", "description": "Additional Nikto arguments."},
            },
            "required": ["target_url"],
        })

        self._add("gobuster_dir", "Brute-force directories and files on a web server using Gobuster.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL."},
                "wordlist": {
                    "type": "string",
                    "description": (
                        "Path to wordlist file. Useful local choices include "
                        "/usr/share/wordlists/dirb/common.txt and SecLists under "
                        "/usr/share/seclists/Discovery/Web-Content/."
                    ),
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "extensions": {"type": "string", "description": "File extensions to search (e.g. 'php,html,txt')."},
                "threads": {"type": "integer", "description": "Number of concurrent threads.", "default": 10},
                "status_codes": {"type": "string", "description": "Positive status codes (e.g. '200,204,301')."},
                "proxy": {"type": "string", "description": "HTTP proxy URL (e.g. 'http://host.docker.internal:8080' to route through Burp Suite)."},
            },
            "required": ["target_url"],
        })

        self._add("sqlmap_scan", "Automated SQL injection detection and exploitation with sqlmap. [HIGH RISK]", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL with parameter (e.g. 'http://target/page?id=1')."},
                "data": {"type": "string", "description": "POST data string."},
                "method": {"type": "string", "enum": ["GET", "POST"], "description": "HTTP method.", "default": "GET"},
                "level": {"type": "integer", "description": "Test level (1-5).", "default": 1, "minimum": 1, "maximum": 5},
                "risk": {"type": "integer", "description": "Risk level (1-3).", "default": 1, "minimum": 1, "maximum": 3},
                "tamper": {
                    "type": "string",
                    "description": (
                        "Tamper script(s). Use sqlmap built-in tamper scripts; "
                        "SecLists payloads are available under /usr/share/seclists/Fuzzing/ "
                        "for manual payload selection before escalating to sqlmap."
                    ),
                },
                "extra_args": {"type": "string", "description": "Additional sqlmap arguments."},
            },
            "required": ["target_url"],
        })

        self._add("hydra_attack", "Online password brute-force with Hydra. [HIGH RISK]", {
            "properties": {
                "target": {"type": "string", "description": "Target IP or hostname."},
                "service": {
                    "type": "string",
                    "enum": ["ssh", "ftp", "http-get", "http-post", "http-post-form",
                             "smb", "rdp", "mysql", "mssql", "postgres", "vnc",
                             "telnet", "smtp", "pop3", "imap"],
                    "description": "Service to attack.",
                },
                "port": {"type": "integer", "description": "Target port (overrides service default)."},
                "username": {"type": "string", "description": "Single username."},
                "username_list": {"type": "string", "description": "Path to username list file."},
                "password_list": {"type": "string", "description": "Path to password list file."},
                "threads": {"type": "integer", "description": "Parallel tasks.", "default": 4},
                "extra_args": {"type": "string", "description": "Additional Hydra arguments."},
            },
            "required": ["target", "service", "password_list"],
        })

        self._add("enum4linux_scan", "Enumerate information from Windows/Samba systems.", {
            "properties": {
                "target": {"type": "string", "description": "Target IP or hostname."},
                "options": {
                    "type": "string",
                    "enum": ["all", "users", "shares", "policies", "groups"],
                    "description": "Enumeration category.",
                    "default": "all",
                },
            },
            "required": ["target"],
        })

        self._add("wfuzz_scan", "Web application fuzzer.", {
            "properties": {
                "target_url": {"type": "string", "description": "URL containing FUZZ keyword."},
                "wordlist": {
                    "type": "string",
                    "description": (
                        "Path to wordlist. Useful local choices include "
                        "/usr/share/wordlists/dirb/common.txt and SecLists under "
                        "/usr/share/seclists/Discovery/Web-Content/ or /usr/share/seclists/Fuzzing/."
                    ),
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "hide_codes": {"type": "string", "description": "Response codes to hide (e.g. '404,302')."},
                "hide_chars": {"type": "string", "description": "Hide responses with this character count."},
                "extra_args": {"type": "string", "description": "Additional wfuzz arguments."},
            },
            "required": ["target_url", "wordlist"],
        })

        self._add("netcat_connect", "TCP connection / listener using Netcat.", {
            "properties": {
                "target": {"type": "string", "description": "Target host (for connect mode)."},
                "port": {"type": "integer", "description": "Port number."},
                "mode": {
                    "type": "string",
                    "enum": ["connect", "listen"],
                    "description": "Connection mode.",
                    "default": "connect",
                },
                "extra_args": {"type": "string", "description": "Additional Netcat flags."},
            },
            "required": ["port"],
        })

        self._add("searchsploit_query", "Search Exploit-DB for known exploits via searchsploit.", {
            "properties": {
                "query": {"type": "string", "description": "Search term(s)."},
                "exact": {"type": "boolean", "description": "Exact match.", "default": False},
                "json_output": {"type": "boolean", "description": "Return JSON output.", "default": True},
            },
            "required": ["query"],
        })

        self._add(
            "cve_lookup",
            "Query the NVD (National Vulnerability Database) CVE 2.0 API. "
            "Supports exact CVE ID lookup, keyword search by product/version, CPE-based lookup, "
            "CVSS severity filtering, and date-range filtering. "
            "Returns CVSS score, severity, description, SERVICE BINDING (from CPE), and references.",
            {
                "properties": {
                    "cve_id": {
                        "type": "string",
                        "description": "Exact CVE identifier (e.g. 'CVE-2021-44228'). "
                                       "Mutually exclusive with keyword, cpe_name, and virtual_match_string.",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Keyword search against CVE descriptions and titles. "
                                       "Best practice: use 'product version' (e.g. 'OpenSSH 7.9', 'Apache httpd 2.4.38'). "
                                       "Mutually exclusive with cve_id.",
                    },
                    "exact_match": {
                        "type": "boolean",
                        "description": "When true, keyword must appear as a whole word (keywordExactMatch). "
                                       "Only valid with keyword.",
                        "default": False,
                    },
                    "cpe_name": {
                        "type": "string",
                        "description": "Filter CVEs by a specific CPE 2.3 name "
                                       "(e.g. 'cpe:2.3:a:openbsd:openssh:7.9:*:*:*:*:*:*:*'). "
                                       "Mutually exclusive with cve_id.",
                    },
                    "virtual_match_string": {
                        "type": "string",
                        "description": "CPE match string pattern to filter CVEs "
                                       "(e.g. 'cpe:2.3:a:apache:http_server:2.4.*'). "
                                       "Mutually exclusive with cve_id.",
                    },
                    "cvss_severity": {
                        "type": "string",
                        "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                        "description": "Filter results to a specific CVSSv3 severity band. "
                                       "Can be combined with keyword or CPE filters.",
                    },
                    "pub_start_date": {
                        "type": "string",
                        "description": "Return CVEs published on or after this date (YYYY-MM-DD). "
                                       "Can be combined with keyword or severity filters.",
                    },
                    "pub_end_date": {
                        "type": "string",
                        "description": "Return CVEs published on or before this date (YYYY-MM-DD).",
                    },
                    "last_mod_start_date": {
                        "type": "string",
                        "description": "Return CVEs last modified on or after this date (YYYY-MM-DD).",
                    },
                    "last_mod_end_date": {
                        "type": "string",
                        "description": "Return CVEs last modified on or before this date (YYYY-MM-DD).",
                    },
                    "no_rejected": {
                        "type": "boolean",
                        "description": "When true, exclude CVEs with REJECT/Rejected status from results.",
                        "default": False,
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-20, default 5). "
                                       "Not applicable when cve_id is provided.",
                        "default": 5,
                    },
                },
                "required": [],
            },
        )

        self._add("hashcat_crack", "GPU/CPU password cracking with Hashcat. [HIGH RISK]", {
            "properties": {
                "hash_file": {"type": "string", "description": "Path to file containing hashes."},
                "hash_type": {"type": "integer", "description": "Hashcat hash-type code (e.g. 0 for MD5)."},
                "wordlist": {"type": "string", "description": "Path to wordlist."},
                "rules": {"type": "string", "description": "Path to rules file."},
                "extra_args": {"type": "string", "description": "Additional Hashcat arguments."},
            },
            "required": ["hash_file", "hash_type", "wordlist"],
        })

        self._add("john_crack", "CPU password cracking with John the Ripper. [HIGH RISK]", {
            "properties": {
                "hash_file": {"type": "string", "description": "Path to file containing hashes."},
                "wordlist": {"type": "string", "description": "Path to wordlist."},
                "format": {"type": "string", "description": "Hash format (e.g. 'raw-md5', 'bcrypt')."},
                "extra_args": {"type": "string", "description": "Additional John arguments."},
            },
            "required": ["hash_file"],
        })

        self._add("dirb_scan", "Web content scanner using DIRB.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL."},
                "wordlist": {
                    "type": "string",
                    "description": "Wordlist path.",
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "extra_args": {"type": "string", "description": "Additional DIRB arguments."},
            },
            "required": ["target_url"],
        })

        self._add("whatweb_scan", "Web technology fingerprinting with WhatWeb.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL."},
                "aggression": {
                    "type": "string",
                    "enum": ["1", "3", "4"],
                    "description": "Aggression level: 1=stealthy, 3=aggressive, 4=heavy.",
                    "default": "1",
                },
                "extra_args": {"type": "string", "description": "Additional WhatWeb arguments."},
            },
            "required": ["target_url"],
        })

        self._add("whois_lookup", "WHOIS domain/IP lookup.", {
            "properties": {
                "target": {"type": "string", "description": "Domain or IP to look up."},
            },
            "required": ["target"],
        })

        self._add("dig_lookup", "DNS lookup using dig.", {
            "properties": {
                "target": {"type": "string", "description": "Domain name to query."},
                "record_type": {
                    "type": "string",
                    "enum": ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME", "ANY"],
                    "description": "DNS record type.",
                    "default": "A",
                },
                "server": {"type": "string", "description": "DNS server to query (e.g. 8.8.8.8)."},
            },
            "required": ["target"],
        })

        self._add("shell_command", "Execute an unrestricted shell command.", {
            "properties": {
                "command": {"type": "string", "description": "The command to execute."},
            },
            "required": ["command"],
        })

        # [MEJORA 7] Auto-recon workflow
        self._add("auto_recon", "Automated reconnaissance: runs whois + dig + nmap + whatweb + gobuster on a target.", {
            "properties": {
                "target": {"type": "string", "description": "Target IP or hostname."},
                "ports": {"type": "string", "description": "Specific ports to scan (default: top 1000)."},
                "web_ports": {"type": "string", "description": "Ports to check for web services (default: '80,443,8080,8443')."},
                "wordlist": {"type": "string", "description": "Wordlist for gobuster.", "default": "/usr/share/wordlists/dirb/common.txt"},
            },
            "required": ["target"],
        })

        # [MEJORA 6] Scan history query
        self._add("get_scan_history", "Query previous scan results from the database.", {
            "properties": {
                "tool": {"type": "string", "description": "Filter by tool name (optional)."},
                "target": {"type": "string", "description": "Filter by target (partial match, optional)."},
                "limit": {"type": "integer", "description": "Max results to return.", "default": 20},
            },
            "required": [],
        })

        # [MEJORA 8] Report generation
        self._add("generate_report", "Generate a markdown report from scan history.", {
            "properties": {
                "target": {"type": "string", "description": "Filter report to a specific target (optional)."},
            },
            "required": [],
        })

        # ========= NUEVAS HERRAMIENTAS DE METASPLOIT =========
        
        self._add("msf_console", "Ejecutar comandos en Metasploit Framework. [ALTO RIESGO]", {
            "type": "object",
            "properties": {
                "resource_script": {"type": "string", "description": "Ruta al archivo de recurso .rc de Metasploit"},
                "commands": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de comandos de Metasploit a ejecutar"
                },
                "workspace": {"type": "string", "description": "Workspace de Metasploit a usar", "default": "default"},
                "background": {"type": "boolean", "description": "Ejecutar en segundo plano", "default": False},
            },
            "required": [],
            "additionalProperties": False,
        })
        
        self._add("msfvenom", "Generar payloads con MSFVenom para explotación. [ALTO RIESGO]", {
            "properties": {
                "payload": {"type": "string", "description": "Payload a generar (ej. windows/meterpreter/reverse_tcp)"},
                "lhost": {"type": "string", "description": "IP del listener"},
                "lport": {"type": "integer", "description": "Puerto del listener"},
                "format": {
                    "type": "string", 
                    "enum": ["exe", "elf", "raw", "python", "c", "powershell", "java", "php", "asp", "aspx", "war"],
                    "description": "Formato de salida",
                    "default": "exe"
                },
                "output_file": {"type": "string", "description": "Archivo de salida"},
                "encoder": {"type": "string", "description": "Encoder a usar (ej. x86/shikata_ga_nai)"},
                "iterations": {"type": "integer", "description": "Número de iteraciones de encoding", "default": 1},
                "platform": {"type": "string", "description": "Plataforma objetivo", "default": "windows"},
                "arch": {"type": "string", "enum": ["x86", "x64"], "description": "Arquitectura", "default": "x86"},
                "badchars": {"type": "string", "description": "Caracteres a evitar (ej. '\\x00\\x0a')"},
                "extra_args": {"type": "string", "description": "Argumentos adicionales"},
            },
            "required": ["payload", "lhost", "lport", "format"],
        })
        
        self._add("metasploit_resource", "Crear y ejecutar scripts resource (.rc) de Metasploit. [ALTO RIESGO]", {
            "properties": {
                "name": {"type": "string", "description": "Nombre del script resource"},
                "commands": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Comandos de Metasploit a incluir"
                },
                "exploit_module": {"type": "string", "description": "Módulo de exploit a usar"},
                "payload": {"type": "string", "description": "Payload a usar"},
                "options": {
                    "type": "object",
                    "description": "Opciones para el módulo (RHOSTS, LHOST, etc.)"
                },
                "run": {"type": "boolean", "description": "Ejecutar inmediatamente", "default": True},
            },
            "required": ["name"],
        })
        
        # ========= HERRAMIENTAS DE ATAQUE DE RED/MITM =========
        
        self._add("bettercap_scan", "Escaneo y ataques MITM con BetterCAP. [ALTO RIESGO]", {
            "properties": {
                "target": {"type": "string", "description": "IP o rango objetivo"},
                "gateway": {"type": "string", "description": "IP del gateway para ARP spoofing"},
                "module": {
                    "type": "string",
                    "enum": ["arp.spoof", "dns.spoof", "http.proxy", "https.proxy", "net.sniff", "tcp.proxy"],
                    "description": "Módulo de BetterCAP a usar",
                    "default": "arp.spoof"
                },
                "action": {
                    "type": "string",
                    "enum": ["scan", "spoof", "sniff", "proxy"],
                    "description": "Acción a realizar"
                },
                "interface": {"type": "string", "description": "Interfaz de red a usar"},
                "script": {"type": "string", "description": "Script de BetterCAP a ejecutar"},
                "commands": {"type": "array", "items": {"type": "string"}, "description": "Comandos interactivos"},
            },
            "required": ["target"],
        })
        
        self._add("responder_poison", "Envenenamiento LLMNR/NBT-NS con Responder. [ALTO RIESGO]", {
            "properties": {
                "interface": {"type": "string", "description": "Interfaz de red", "default": "eth0"},
                "mode": {
                    "type": "string",
                    "enum": ["analyze", "poison"],
                    "description": "Modo: analyze (solo análisis) o poison (envenenamiento)",
                    "default": "poison"
                },
                "services": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["HTTP", "SMB", "SQL", "FTP", "POP3", "SMTP", "IMAP"]},
                    "description": "Servicios a activar"
                },
                "wpad": {"type": "boolean", "description": "Activar WPAD rogue server", "default": True},
                "fingerprint": {"type": "boolean", "description": "Activar fingerprinting", "default": True},
            },
            "required": ["interface"],
        })
        
        # ========= HERRAMIENTAS DE EXPLOTACIÓN WINDOWS =========
        
        self._add("crackmapexec", "Ejecución de CME para explotación de redes Windows. [ALTO RIESGO]", {
            "properties": {
                "target": {"type": "string", "description": "IP, rango o archivo con objetivos"},
                "protocol": {
                    "type": "string",
                    "enum": ["smb", "ssh", "winrm", "mssql", "ldap", "ftp"],
                    "description": "Protocolo a usar",
                    "default": "smb"
                },
                "username": {"type": "string", "description": "Usuario o archivo de usuarios"},
                "password": {"type": "string", "description": "Password o archivo de passwords"},
                "hash": {"type": "string", "description": "NTLM hash para pass-the-hash"},
                "module": {"type": "string", "description": "Módulo de CME a ejecutar"},
                "command": {"type": "string", "description": "Comando a ejecutar"},
                "exec_method": {
                    "type": "string",
                    "enum": ["wmiexec", "smbexec", "atexec", "psexec"],
                    "description": "Método de ejecución"
                },
                "port": {"type": "integer", "description": "Puerto específico"},
            },
            "required": ["target"],
        })
        
        self._add("impacket_scripts", "Ejecutar scripts de Impacket. [ALTO RIESGO]", {
            "properties": {
                "script": {
                    "type": "string",
                    "enum": ["psexec.py", "wmiexec.py", "smbexec.py", "secretsdump.py", 
                            "GetUserSPNs.py", "GetNPUsers.py", "ticketer.py", "raiseChild.py"],
                    "description": "Script de Impacket a ejecutar"
                },
                "target": {"type": "string", "description": "IP o hostname objetivo"},
                "username": {"type": "string", "description": "Usuario"},
                "password": {"type": "string", "description": "Password"},
                "hash": {"type": "string", "description": "NTLM hash"},
                "domain": {"type": "string", "description": "Dominio"},
                "command": {"type": "string", "description": "Comando a ejecutar"},
                "port": {"type": "integer", "description": "Puerto"},
                "extra_args": {"type": "string", "description": "Argumentos adicionales"},
            },
            "required": ["script", "target"],
        })
        
        self._add("bloodhound_enum", "Enumeración de Active Directory con BloodHound. [ALTO RIESGO]", {
            "properties": {
                "target": {"type": "string", "description": "IP o dominio objetivo"},
                "username": {"type": "string", "description": "Usuario del dominio"},
                "password": {"type": "string", "description": "Password"},
                "domain": {"type": "string", "description": "Dominio"},
                "collector": {
                    "type": "string",
                    "enum": ["BloodHound.py"],
                    "description": "Colector Python soportado en el contenedor Linux",
                    "default": "BloodHound.py"
                },
                "collection_methods": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["All", "Group", "LocalAdmin", "RDP", "DCOM", "PSRemote"]},
                    "description": "Métodos de colección"
                },
                "zip_filename": {"type": "string", "description": "Nombre del archivo ZIP de salida"},
            },
            "required": ["target", "username", "password", "domain"],
        })

        # ========= HERRAMIENTAS DE AUDITORÍA WEB =========
        
        self._add("wpscan", "Escaneo de vulnerabilidades en WordPress. [ALTO RIESGO]", {
            "properties": {
                "target_url": {"type": "string", "description": "URL del WordPress a escanear"},
                "enumerate": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["vp", "ap", "vt", "at", "u", "tt"]},
                    "description": "Componentes a enumerar (vp=plugins vuln, ap=todos plugins, etc.)"
                },
                "username": {"type": "string", "description": "Usuario para ataque de fuerza bruta"},
                "password_list": {"type": "string", "description": "Lista de passwords"},
                "api_token": {"type": "string", "description": "Token de API de WPVulnDB"},
                "plugins_version": {"type": "boolean", "description": "Detectar versiones de plugins", "default": True},
                "random_agent": {"type": "boolean", "description": "Usar user-agent aleatorio", "default": True},
                "stealthy": {"type": "boolean", "description": "Modo sigiloso (menos peticiones)", "default": False},
            },
            "required": ["target_url"],
        })
        
        self._add("joomscan", "Escáner de vulnerabilidades para Joomla.", {
            "properties": {
                "target_url": {"type": "string", "description": "URL del Joomla a escanear"},
                "enumerate": {
                    "type": "string",
                    "enum": ["components", "vuln", "all"],
                    "description": "Tipo de enumeración",
                    "default": "all"
                },
                "cookie": {"type": "string", "description": "Cookie de sesión"},
                "user_agent": {"type": "string", "description": "User-Agent personalizado"},
                "proxy": {"type": "string", "description": "Proxy a usar (ej. http://127.0.0.1:8080)"},
            },
            "required": ["target_url"],
        })
        
        self._add("zap_scan", "Escaneo con OWASP ZAP. [ALTO RIESGO]", {
            "properties": {
                "target_url": {"type": "string", "description": "URL objetivo"},
                "scan_type": {
                    "type": "string",
                    "enum": ["spider", "active", "passive", "full"],
                    "description": "Tipo de escaneo",
                    "default": "full"
                },
                "api_key": {"type": "string", "description": "API key de ZAP"},
                "port": {"type": "integer", "description": "Puerto de la API de ZAP", "default": 8080},
                "context_name": {"type": "string", "description": "Nombre del contexto"},
                "include_patterns": {"type": "array", "items": {"type": "string"}, "description": "Patrones URL a incluir"},
                "exclude_patterns": {"type": "array", "items": {"type": "string"}, "description": "Patrones URL a excluir"},
                "max_children": {"type": "integer", "description": "Máximo hijos para spider", "default": 5},
            },
            "required": ["target_url"],
        })
        
        # ========= HERRAMIENTAS DE FUERZA BRUTA AVANZADA =========
        
        self._add("medusa_bruteforce", "Ataque de fuerza bruta con Medusa. [ALTO RIESGO]", {
            "properties": {
                "target": {"type": "string", "description": "IP o hostname objetivo"},
                "service": {
                    "type": "string",
                    "enum": ["ssh", "ftp", "telnet", "http", "pop3", "imap", "smb", "mysql", "mssql", "postgres"],
                    "description": "Servicio a atacar"
                },
                "username": {"type": "string", "description": "Usuario único"},
                "user_list": {"type": "string", "description": "Archivo de usuarios"},
                "password_list": {"type": "string", "description": "Archivo de passwords"},
                "port": {"type": "integer", "description": "Puerto específico"},
                "threads": {"type": "integer", "description": "Hilos paralelos", "default": 5},
                "timeout": {"type": "integer", "description": "Timeout en segundos", "default": 10},
                "verbose": {"type": "boolean", "description": "Modo verbose", "default": False},
            },
            "required": ["target", "service", "password_list"],
        })
        
        self._add("ncrack_bruteforce", "Ataque de fuerza bruta de alta velocidad con Ncrack. [ALTO RIESGO]", {
            "properties": {
                "target": {"type": "string", "description": "IP:puerto o rango (ej. 192.168.1.1:22)"},
                "service": {
                    "type": "string",
                    "enum": ["ssh", "rdp", "ftp", "telnet", "http", "https", "smb", "mysql", "vnc"],
                    "description": "Servicio a atacar"
                },
                "user_list": {"type": "string", "description": "Archivo de usuarios"},
                "pass_list": {"type": "string", "description": "Archivo de passwords"},
                "timing": {
                    "type": "string",
                    "enum": ["T0", "T1", "T2", "T3", "T4", "T5"],
                    "description": "Timing template",
                    "default": "T3"
                },
                "port": {"type": "integer", "description": "Puerto"},
                "connections": {"type": "integer", "description": "Conexiones paralelas", "default": 5},
                "save": {"type": "string", "description": "Archivo para guardar resultados"},
            },
            "required": ["target", "service", "user_list", "pass_list"],
        })
        
        # ========= HERRAMIENTAS DE INGENIERÍA SOCIAL =========
        
        self._add("setoolkit", "Social Engineering Toolkit. [ALTO RIESGO]", {
            "properties": {
                "attack_vector": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4, 5],
                    "description": "Vector de ataque: 1=Spear-Phishing, 2=Web Attack, 3=Infectious Media, 4=Create Payload, 5=Mass Mailer"
                },
                "web_attack_type": {
                    "type": "integer",
                    "enum": [1, 2, 3, 4],
                    "description": "Tipo de ataque web: 1=Java Applet, 2=Metasploit, 3=Credential Harvester, 4=Tabnabbing"
                },
                "clone_url": {"type": "string", "description": "URL a clonar para Credential Harvester"},
                "payload": {"type": "string", "description": "Payload a generar"},
                "lhost": {"type": "string", "description": "IP del listener"},
                "lport": {"type": "integer", "description": "Puerto del listener"},
                "email_template": {"type": "string", "description": "Plantilla de email"},
                "target_email": {"type": "string", "description": "Email objetivo"},
            },
            "required": ["attack_vector"],
        })
        
        self._add("beef_start", "Iniciar y controlar BeEF (Browser Exploitation Framework). [ALTO RIESGO]", {
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["start", "stop", "status", "hook", "command"],
                    "description": "Acción a realizar",
                    "default": "start"
                },
                "port": {"type": "integer", "description": "Puerto de la interfaz web", "default": 3000},
                "target_url": {"type": "string", "description": "URL para inyectar hook (para acción 'hook')"},
                "command_module": {"type": "string", "description": "Módulo de comando a ejecutar"},
                "hook_id": {"type": "string", "description": "ID del browser hookeado"},
                "options": {"type": "object", "description": "Opciones para el módulo de comando"},
            },
        })
        
        # ========= HERRAMIENTAS DE ANÁLISIS DE RED =========
        
        self._add("tcpdump_capture", "Capturar tráfico de red con tcpdump.", {
            "properties": {
                "interface": {"type": "string", "description": "Interfaz de red", "default": "eth0"},
                "filter": {"type": "string", "description": "Filtro BPF (ej. 'port 80')"},
                "count": {"type": "integer", "description": "Número de paquetes a capturar", "default": 100},
                "output_file": {"type": "string", "description": "Archivo de salida (.pcap)"},
                "verbose": {"type": "boolean", "description": "Salida detallada", "default": False},
                "duration": {"type": "integer", "description": "Duración de captura en segundos"},
            },
            "required": ["interface"],
        })
        
        self._add("ettercap_mitm", "Ataques MITM con Ettercap. [ALTO RIESGO]", {
            "properties": {
                "target1": {"type": "string", "description": "IP objetivo 1 (víctima)"},
                "target2": {"type": "string", "description": "IP objetivo 2 (gateway)"},
                "interface": {"type": "string", "description": "Interfaz de red", "default": "eth0"},
                "attack_type": {
                    "type": "string",
                    "enum": ["arp", "dhcp", "port", "icmp"],
                    "description": "Tipo de ataque",
                    "default": "arp"
                },
                "filters": {"type": "array", "items": {"type": "string"}, "description": "Filtros a aplicar"},
                "plugins": {"type": "array", "items": {"type": "string"}, "description": "Plugins a cargar"},
                "mode": {
                    "type": "string",
                    "enum": ["text", "curses", "daemon"],
                    "description": "Modo de interfaz",
                    "default": "text"
                },
            },
            "required": ["target1", "target2"],
        })
        
        # ========= HERRAMIENTAS DE AUDITORÍA WIFI =========
        
        self._add("aircrack_suite", "Suite Aircrack-ng para auditoría WiFi. [ALTO RIESGO]", {
            "properties": {
                "command": {
                    "type": "string",
                    "enum": ["airodump", "aireplay", "aircrack", "airmon", "packetforge"],
                    "description": "Comando de aircrack-ng a ejecutar"
                },
                "interface": {"type": "string", "description": "Interfaz WiFi"},
                "bssid": {"type": "string", "description": "BSSID del objetivo"},
                "channel": {"type": "integer", "description": "Canal"},
                "essid": {"type": "string", "description": "ESSID del objetivo"},
                "capture_file": {"type": "string", "description": "Archivo de captura"},
                "wordlist": {"type": "string", "description": "Wordlist para crackear"},
                "attack_type": {
                    "type": "string",
                    "enum": ["deauth", "arp", "fragment", "cafe"],
                    "description": "Tipo de ataque (para aireplay)"
                },
                "client": {"type": "string", "description": "MAC del cliente asociado"},
                "output_prefix": {"type": "string", "description": "Prefijo para archivos de salida"},
            },
            "required": ["command"],
        })
        
        self._add("wifite_audit", "Auditoría automatizada de WiFi con Wifite. [ALTO RIESGO]", {
            "properties": {
                "interface": {"type": "string", "description": "Interfaz WiFi", "default": "wlan0"},
                "target_bssid": {"type": "string", "description": "BSSID específico a atacar"},
                "target_channel": {"type": "integer", "description": "Canal específico"},
                "attack": {
                    "type": "string",
                    "enum": ["wep", "wpa", "wps"],
                    "description": "Tipo de ataque",
                    "default": "wpa"
                },
                "wordlist": {"type": "string", "description": "Wordlist para WPA handshake"},
                "wps_pin": {"type": "boolean", "description": "Intentar ataque WPS PIN", "default": True},
                "no_wps": {"type": "boolean", "description": "No usar ataques WPS", "default": False},
                "power": {"type": "integer", "description": "Señal mínima (-dB)", "default": -80},
                "clients": {"type": "boolean", "description": "Mostrar clientes conectados", "default": True},
                "wep_attack": {
                    "type": "string",
                    "enum": ["arp", "chopchop", "fragment"],
                    "description": "Ataque WEP específico"
                },
            },
            "required": ["interface"],
        })
        
        # ========= HERRAMIENTAS DE GENERACIÓN DE WORDLISTS =========
        
        self._add("crunch_gen", "Generar wordlists personalizadas con Crunch.", {
            "properties": {
                "min_length": {"type": "integer", "description": "Longitud mínima", "minimum": 1},
                "max_length": {"type": "integer", "description": "Longitud máxima"},
                "charset": {"type": "string", "description": "Conjunto de caracteres (ej. '0123456789')"},
                "pattern": {"type": "string", "description": "Patrón (ej. @@@%%% para 3 letras + 3 números)"},
                "output_file": {"type": "string", "description": "Archivo de salida"},
                "start_string": {"type": "string", "description": "String de inicio"},
                "stop_string": {"type": "string", "description": "String de parada"},
                "compress": {"type": "boolean", "description": "Comprimir salida", "default": False},
            },
            "required": ["min_length", "max_length"],
        })
        
        self._add("cewl_gen", "Generar wordlists personalizadas desde URLs con CeWL.", {
            "properties": {
                "target_url": {"type": "string", "description": "URL objetivo"},
                "depth": {"type": "integer", "description": "Profundidad de spider", "default": 2},
                "min_word_length": {"type": "integer", "description": "Longitud mínima de palabra", "default": 3},
                "max_word_length": {"type": "integer", "description": "Longitud máxima de palabra", "default": 20},
                "output_file": {"type": "string", "description": "Archivo de salida"},
                "with_numbers": {"type": "boolean", "description": "Incluir números", "default": False},
                "email_addresses": {"type": "boolean", "description": "Extraer emails", "default": False},
                "meta_data": {"type": "boolean", "description": "Extraer metadata", "default": False},
                "user_agent": {"type": "string", "description": "User-Agent personalizado"},
                "proxy": {"type": "string", "description": "Proxy a usar"},
            },
            "required": ["target_url"],
        })

        # ========= v3.7 TOOLS =========

        self._add("masscan_scan", "High-speed TCP port scanner. Much faster than nmap for large ranges.", {
            "properties": {
                "target": {"type": "string", "description": "IP, CIDR range, or hostname to scan."},
                "ports": {
                    "type": "string",
                    "description": "Port range to scan (e.g. '1-65535', '80,443,8080', '0-1000').",
                    "default": "1-1000",
                },
                "rate": {
                    "type": "integer",
                    "description": "Packets per second. Higher = faster but noisier. Max ~1000000.",
                    "default": 1000,
                },
                "extra_args": {"type": "string", "description": "Additional masscan arguments."},
            },
            "required": ["target"],
        })

        self._add("feroxbuster_scan", "Fast recursive web content discovery with feroxbuster.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL."},
                "wordlist": {
                    "type": "string",
                    "description": "Wordlist path. SecLists web content lists are in /usr/share/seclists/Discovery/Web-Content/.",
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "extensions": {"type": "string", "description": "Comma-separated extensions to append (e.g. 'php,html,txt')."},
                "threads": {"type": "integer", "description": "Number of concurrent threads.", "default": 50},
                "depth": {"type": "integer", "description": "Maximum recursion depth.", "default": 2},
                "status_codes": {"type": "string", "description": "HTTP status codes to include (e.g. '200,204,301,302,403')."},
                "filter_codes": {"type": "string", "description": "HTTP status codes to filter out (e.g. '404,400')."},
                "proxy": {"type": "string", "description": "HTTP proxy URL."},
                "extra_args": {"type": "string", "description": "Additional feroxbuster arguments."},
            },
            "required": ["target_url"],
        })

        self._add("dirsearch_scan", "Web path discovery with dirsearch.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL."},
                "wordlist": {
                    "type": "string",
                    "description": "Wordlist path. SecLists web content lists are in /usr/share/seclists/Discovery/Web-Content/.",
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "extensions": {"type": "string", "description": "Comma-separated extensions (e.g. 'php,html,txt')."},
                "threads": {"type": "integer", "description": "Number of threads.", "default": 30},
                "recursive": {"type": "boolean", "description": "Enable recursive discovery.", "default": False},
                "status_codes": {"type": "string", "description": "HTTP status codes to include."},
                "exclude_status": {"type": "string", "description": "HTTP status codes to exclude.", "default": "404"},
                "proxy": {"type": "string", "description": "Proxy URL."},
                "extra_args": {"type": "string", "description": "Additional dirsearch arguments."},
            },
            "required": ["target_url"],
        })

        self._add("ffuf_fuzz", "Fast web fuzzer for directory, file, parameter, and vhost discovery.", {
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target URL with FUZZ keyword placeholder (e.g. 'http://host/FUZZ').",
                },
                "wordlist": {
                    "type": "string",
                    "description": (
                        "Path to wordlist. SecLists is available under "
                        "/usr/share/seclists/Discovery/Web-Content/, /usr/share/seclists/Usernames/, "
                        "/usr/share/seclists/Passwords/, and /usr/share/seclists/Fuzzing/."
                    ),
                    "default": "/usr/share/seclists/Discovery/Web-Content/common.txt",
                },
                "mode": {
                    "type": "string",
                    "enum": ["dir", "vhost", "param"],
                    "description": "Fuzzing mode: dir=path fuzzing, vhost=virtual host discovery, param=GET param fuzzing.",
                    "default": "dir",
                },
                "extensions": {"type": "string", "description": "File extensions to append (e.g. 'php,html')."},
                "threads": {"type": "integer", "description": "Number of concurrent threads.", "default": 40},
                "filter_codes": {
                    "type": "string",
                    "description": "HTTP status codes to filter OUT (e.g. '404,403').",
                    "default": "404",
                },
                "match_codes": {"type": "string", "description": "HTTP status codes to match (e.g. '200,301')."},
                "proxy": {"type": "string", "description": "HTTP proxy (e.g. 'http://host.docker.internal:8080')."},
                "extra_args": {"type": "string", "description": "Additional ffuf arguments."},
            },
            "required": ["url"],
        })

        self._add("nuclei_scan", "Vulnerability scanner using community templates. Fast and accurate.", {
            "properties": {
                "target": {"type": "string", "description": "Target URL or IP to scan."},
                "templates": {
                    "type": "string",
                    "description": (
                        "Template tags or paths to use. The pinned community template resource is "
                        "installed at /usr/share/nuclei-templates (e.g. /usr/share/nuclei-templates/http/cves/)."
                    ),
                    "default": "/usr/share/nuclei-templates",
                },
                "severity": {
                    "type": "string",
                    "enum": ["info", "low", "medium", "high", "critical"],
                    "description": "Minimum severity level to report.",
                },
                "rate_limit": {
                    "type": "integer",
                    "description": "Max requests per second.",
                    "default": 150,
                },
                "proxy": {"type": "string", "description": "HTTP proxy URL."},
                "extra_args": {"type": "string", "description": "Additional nuclei arguments."},
            },
            "required": ["target"],
        })

        self._add("subfinder_recon", "Passive subdomain discovery with ProjectDiscovery subfinder.", {
            "properties": {
                "domain": {"type": "string", "description": "Domain to enumerate."},
                "sources": {"type": "string", "description": "Comma-separated sources to use."},
                "all_sources": {"type": "boolean", "description": "Use all available sources.", "default": False},
                "recursive": {"type": "boolean", "description": "Use recursive sources only.", "default": False},
                "silent": {"type": "boolean", "description": "Print only discovered subdomains.", "default": True},
                "extra_args": {"type": "string", "description": "Additional subfinder arguments."},
            },
            "required": ["domain"],
        })

        self._add("naabu_scan", "Fast host port discovery with ProjectDiscovery naabu.", {
            "properties": {
                "target": {"type": "string", "description": "Host, domain, IP, CIDR, or input file target."},
                "ports": {"type": "string", "description": "Ports to scan (e.g. '80,443,8080')."},
                "top_ports": {"type": "string", "description": "Top ports preset/count supported by naabu (e.g. '1000')."},
                "rate": {"type": "integer", "description": "Packet rate.", "default": 1000},
                "exclude_ports": {"type": "string", "description": "Ports to exclude."},
                "extra_args": {"type": "string", "description": "Additional naabu arguments."},
            },
            "required": ["target"],
        })

        self._add("pd_httpx_probe", "ProjectDiscovery httpx web service probe, installed as pd-httpx to avoid command conflicts.", {
            "properties": {
                "target": {"type": "string", "description": "Single URL, host, or IP to probe."},
                "input_file": {"type": "string", "description": "File containing hosts/URLs to probe."},
                "ports": {"type": "string", "description": "Ports to probe (e.g. '80,443,8080,8443')."},
                "title": {"type": "boolean", "description": "Extract page title.", "default": True},
                "tech_detect": {"type": "boolean", "description": "Detect technologies.", "default": True},
                "status_code": {"type": "boolean", "description": "Include HTTP status code.", "default": True},
                "follow_redirects": {"type": "boolean", "description": "Follow redirects.", "default": False},
                "json_output": {"type": "boolean", "description": "Emit JSON lines.", "default": False},
                "extra_args": {"type": "string", "description": "Additional pd-httpx arguments."},
            },
            "required": [],
        })

        self._add("katana_crawl", "Headless-friendly web crawler with ProjectDiscovery katana.", {
            "properties": {
                "target_url": {"type": "string", "description": "Target URL to crawl."},
                "depth": {"type": "integer", "description": "Crawl depth.", "default": 2},
                "js_crawl": {"type": "boolean", "description": "Parse JavaScript files for endpoints.", "default": True},
                "headless": {"type": "boolean", "description": "Use browser-based crawling.", "default": False},
                "known_files": {"type": "string", "description": "Known files mode value accepted by katana (e.g. 'all')."},
                "proxy": {"type": "string", "description": "Proxy URL."},
                "extra_args": {"type": "string", "description": "Additional katana arguments."},
            },
            "required": ["target_url"],
        })

        self._add("netexec", "NetExec for Windows/AD enumeration and credential validation. [HIGH RISK]", {
            "properties": {
                "target": {"type": "string", "description": "IP, CIDR, hostname, or file with targets."},
                "protocol": {
                    "type": "string",
                    "enum": ["smb", "ssh", "winrm", "mssql", "ldap", "ftp", "rdp", "vnc"],
                    "description": "Protocol to use.",
                    "default": "smb",
                },
                "username": {"type": "string", "description": "Username or username file."},
                "password": {"type": "string", "description": "Password or password file."},
                "hash": {"type": "string", "description": "NTLM hash for pass-the-hash."},
                "module": {"type": "string", "description": "NetExec module to run."},
                "command": {"type": "string", "description": "Command to execute."},
                "port": {"type": "integer", "description": "Override target port."},
                "extra_args": {"type": "string", "description": "Additional netexec arguments."},
            },
            "required": ["target"],
        })

        self._add("evil_winrm_shell", "Run a non-interactive Evil-WinRM PowerShell command. [HIGH RISK]", {
            "properties": {
                "target": {"type": "string", "description": "Target host/IP."},
                "username": {"type": "string", "description": "Username."},
                "password": {"type": "string", "description": "Password."},
                "hash": {"type": "string", "description": "NTLM hash."},
                "domain": {"type": "string", "description": "Domain."},
                "command": {"type": "string", "description": "PowerShell command to run non-interactively."},
                "scripts_path": {"type": "string", "description": "Local scripts path to expose to Evil-WinRM."},
                "extra_args": {"type": "string", "description": "Additional evil-winrm arguments."},
            },
            "required": ["target", "username", "command"],
        })

        self._add("certipy_ad", "Certipy AD CS enumeration and abuse helper. [HIGH RISK]", {
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["find", "req", "auth", "account", "ca", "cert", "parse", "forge", "relay", "shadow", "template"],
                    "description": "Certipy action.",
                    "default": "find",
                },
                "target": {"type": "string", "description": "Target host, domain, or identity target depending on action."},
                "username": {"type": "string", "description": "Username."},
                "password": {"type": "string", "description": "Password."},
                "hash": {"type": "string", "description": "NTLM hash."},
                "domain": {"type": "string", "description": "Domain."},
                "dc_ip": {"type": "string", "description": "Domain controller IP."},
                "ca": {"type": "string", "description": "Certificate authority name."},
                "template": {"type": "string", "description": "Certificate template name."},
                "extra_args": {"type": "string", "description": "Additional certipy-ad arguments."},
            },
            "required": ["action"],
        })

        self._add("kerbrute_enum", "Kerberos username/password discovery with kerbrute. [HIGH RISK]", {
            "properties": {
                "domain": {"type": "string", "description": "AD/Kerberos domain."},
                "dc": {"type": "string", "description": "Domain controller host/IP."},
                "user_list": {
                    "type": "string",
                    "description": "User list path. SecLists usernames are in /usr/share/seclists/Usernames/.",
                },
                "mode": {
                    "type": "string",
                    "enum": ["userenum", "passwordspray", "bruteuser", "bruteforce"],
                    "description": "Kerbrute mode.",
                    "default": "userenum",
                },
                "threads": {"type": "integer", "description": "Thread count.", "default": 10},
                "extra_args": {"type": "string", "description": "Additional kerbrute arguments."},
            },
            "required": ["domain", "user_list"],
        })

        self._add("enum4linux_ng_scan", "Next-generation SMB/Windows enumeration with JSON output support.", {
            "properties": {
                "target": {"type": "string", "description": "Target IP or hostname."},
                "options": {
                    "type": "string",
                    "enum": ["all", "users", "groups", "shares", "policy", "os", "listeners"],
                    "description": "Enumeration category.",
                    "default": "all",
                },
                "username": {"type": "string", "description": "Username."},
                "password": {"type": "string", "description": "Password."},
                "domain": {"type": "string", "description": "Domain/workgroup."},
                "json_output": {"type": "boolean", "description": "Emit JSON output.", "default": True},
                "extra_args": {"type": "string", "description": "Additional enum4linux-ng arguments."},
            },
            "required": ["target"],
        })

        self._add("theharvester_recon", "OSINT tool for email, subdomain, host, and employee name harvesting.", {
            "properties": {
                "domain": {"type": "string", "description": "Domain to gather information about."},
                "sources": {
                    "type": "string",
                    "description": "Data sources to query (e.g. 'google,bing,linkedin,shodan'). Use 'all' for all sources.",
                    "default": "google,bing,crtsh",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to retrieve.",
                    "default": 100,
                },
                "dns_brute": {
                    "type": "boolean",
                    "description": "Perform DNS brute force on the domain.",
                    "default": False,
                },
            },
            "required": ["domain"],
        })
