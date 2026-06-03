"""CLI 输出解析器。

把部分工具的原始 stdout/stderr 转为结构化 JSON，方便 Evidence Gate
和报告生成消费。
"""

import re
import xml.etree.ElementTree as ET
from typing import Any, Optional


class OutputParsers:
    """Parse raw CLI output from tools into structured JSON."""

    @staticmethod
    def parse_nmap_xml(xml_str: str) -> Optional[dict]:
        """Parse Nmap XML output into structured JSON."""
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError:
            return None

        result: dict[str, Any] = {
            "scanner": root.get("scanner", "nmap"),
            "args": root.get("args", ""),
            "start_time": root.get("startstr", ""),
            "hosts": [],
        }
        for host_el in root.findall("host"):
            host_info: dict[str, Any] = {"status": "", "addresses": [], "hostnames": [], "ports": []}
            status = host_el.find("status")
            if status is not None:
                host_info["status"] = status.get("state", "")
            for addr in host_el.findall("address"):
                host_info["addresses"].append({"addr": addr.get("addr", ""), "type": addr.get("addrtype", "")})
            for hn in host_el.findall(".//hostname"):
                host_info["hostnames"].append(hn.get("name", ""))
            ports_el = host_el.find("ports")
            if ports_el is not None:
                for port_el in ports_el.findall("port"):
                    port_info: dict[str, Any] = {
                        "port": port_el.get("portid", ""),
                        "protocol": port_el.get("protocol", ""),
                    }
                    state = port_el.find("state")
                    if state is not None:
                        port_info["state"] = state.get("state", "")
                    service = port_el.find("service")
                    if service is not None:
                        port_info["service"] = service.get("name", "")
                        port_info["product"] = service.get("product", "")
                        port_info["version"] = service.get("version", "")
                    scripts_out = []
                    for script_el in port_el.findall("script"):
                        scripts_out.append({"id": script_el.get("id", ""), "output": script_el.get("output", "")})
                    if scripts_out:
                        port_info["scripts"] = scripts_out
                    host_info["ports"].append(port_info)
            result["hosts"].append(host_info)

        run_stats = root.find("runstats/finished")
        if run_stats is not None:
            result["summary"] = run_stats.get("summary", "")
            result["elapsed"] = run_stats.get("elapsed", "")
        return result

    @staticmethod
    def parse_gobuster(raw: str) -> Optional[dict]:
        """Parse Gobuster output into structured list of discovered paths."""
        lines = raw.strip().split("\n")
        findings = []
        for line in lines:
            # Gobuster format: /path (Status: 200) [Size: 1234]
            match = re.match(r"^(/\S+)\s+\(Status:\s*(\d+)\)\s*(?:\[Size:\s*(\d+)\])?", line)
            if match:
                findings.append({
                    "path": match.group(1),
                    "status": int(match.group(2)),
                    "size": int(match.group(3)) if match.group(3) else None,
                })
        if findings:
            return {"discovered_paths": findings, "total_found": len(findings)}
        return None

    @staticmethod
    def parse_nikto(raw: str) -> Optional[dict]:
        """Parse Nikto output into structured vulnerability list."""
        lines = raw.strip().split("\n")
        vulns = []
        server_info = {}
        for line in lines:
            line = line.strip()
            # Server header info
            if line.startswith("+ Server:"):
                server_info["server"] = line.replace("+ Server:", "").strip()
            elif line.startswith("+ Target IP:"):
                server_info["target_ip"] = line.replace("+ Target IP:", "").strip()
            elif line.startswith("+ Target Hostname:"):
                server_info["target_hostname"] = line.replace("+ Target Hostname:", "").strip()
            elif line.startswith("+ Target Port:"):
                server_info["target_port"] = line.replace("+ Target Port:", "").strip()
            # Vulnerability lines start with + and contain OSVDB or descriptive text
            elif line.startswith("+") and len(line) > 3 and not line.startswith("+ Start") and not line.startswith("+ End"):
                osvdb = ""
                match = re.search(r"OSVDB-(\d+)", line)
                if match:
                    osvdb = f"OSVDB-{match.group(1)}"
                vulns.append({
                    "finding": line.lstrip("+ ").strip(),
                    "osvdb": osvdb,
                })
        if vulns or server_info:
            return {"server_info": server_info, "findings": vulns, "total_findings": len(vulns)}
        return None

    @staticmethod
    def parse_hydra(raw: str) -> Optional[dict]:
        """Parse Hydra output to extract found credentials."""
        lines = raw.strip().split("\n")
        creds = []
        for line in lines:
            # Hydra format: [port][service] host:   login: user   password: pass
            match = re.search(r"login:\s*(\S+)\s+password:\s*(\S+)", line)
            if match:
                creds.append({
                    "username": match.group(1),
                    "password": match.group(2),
                })
        if creds:
            return {"credentials_found": creds, "total_found": len(creds)}
        return None

    @staticmethod
    def parse_whatweb(raw: str) -> Optional[dict]:
        """Parse WhatWeb output into technology list."""
        lines = raw.strip().split("\n")
        technologies = []
        for line in lines:
            if not line.strip():
                continue
            # WhatWeb outputs comma-separated plugins per line
            parts = re.findall(r"(\S+)\[([^\]]*)\]", line)
            for name, detail in parts:
                technologies.append({"technology": name, "detail": detail})
            # Also capture items without brackets
            simple = re.findall(r"(?:^|\s)([A-Za-z][\w.-]+)(?:\s|,|$)", line)
            for s in simple:
                if not any(t["technology"] == s for t in technologies):
                    technologies.append({"technology": s, "detail": ""})
        if technologies:
            return {"technologies": technologies, "total": len(technologies)}
        return None
