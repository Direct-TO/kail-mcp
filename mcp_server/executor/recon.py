"""侦察与资产发现工具实现。"""

import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..input_sanitizer import InputSanitizer
from ..parsers import OutputParsers


class ReconToolsMixin:
    async def _tool_nmap_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        scan_type = args.get("scan_type", "quick")
        timing = args.get("timing", "T3")
        ports = args.get("ports", "")
        scripts = args.get("scripts", "")
        extra = args.get("extra_args", "")

        scan_flags = {
            "quick":     ["-sS", "-sV", "--top-ports", "1000"],
            "full":      ["-sS", "-sV", "-sC", "-p-"],
            "stealth":   ["-sS", "-sV"],
            "vuln":      ["-sS", "-sV", "--script", "vuln"],
            "scripts":   ["-sS", "-sV", "-sC"],
            "discovery": ["-sn"],
            "udp":       ["-sU", "--top-ports", "50"],
        }.get(scan_type, ["-sS", "-sV"])

        # Bug 3: if ports is specified (or extra_args contains -p), strip conflicting
        # scan_type flags (-p- and --top-ports N) so nmap doesn't get two -p options.
        flags = list(scan_flags)
        has_port_conflict = bool(ports) or bool(extra and re.search(r'(?<!\w)-p[ \-]', extra))
        if has_port_conflict:
            clean: list[str] = []
            skip_next = False
            for f in flags:
                if skip_next:
                    skip_next = False
                    continue
                if f == "-p-":
                    continue
                if f == "--top-ports":
                    skip_next = True
                    continue
                clean.append(f)
            flags = clean

        cmd: list[str] = ["nmap"] + flags + [f"-{timing}"]

        # discovery mode: no ports, no scripts
        if scan_type != "discovery":
            if ports:
                cmd += ["-p", InputSanitizer.sanitize_generic(ports)]
            if scripts and scan_type not in ("vuln",):
                cmd += ["--script", InputSanitizer.sanitize_generic(scripts)]

        if extra:
            try:  # Bug 4: shlex.split raises ValueError on unbalanced quotes
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        cmd += [target, "-oX", "-"]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("nmap"))

        parsed = OutputParsers.parse_nmap_xml(stdout)
        if parsed:
            return self._ok(json.dumps(parsed, indent=2))

        # Bug 5: surface stderr when nmap exits non-zero so the LLM sees the real error
        if rc != 0:
            return self._ok(f"[NMAP ERROR rc={rc}]:\n{stderr}\n{stdout}".strip())
        return self._ok(stdout if stdout else stderr)

    async def _tool_whois_lookup(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        cmd = ["whois", target]
        stdout, stderr, rc = await self._run_subprocess(cmd, self._default_timeout)
        return self._ok(stdout if stdout else stderr)

    async def _tool_dig_lookup(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        record_type = args.get("record_type", "A")
        server = args.get("server", "")

        cmd = ["dig", target, record_type]
        if server:
            cmd.append(f"@{InputSanitizer.sanitize_target(server)}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._default_timeout)
        return self._ok(stdout if stdout else stderr)

    async def _tool_auto_recon(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)

        ports = args.get("ports", "")
        web_ports_str = args.get("web_ports", "80,443,8080,8443")
        wordlist = args.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        web_ports = [int(p.strip()) for p in web_ports_str.split(",") if p.strip().isdigit()]

        recon_report: dict[str, Any] = {
            "target": target,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phases": {},
        }

        # Phase 1: WHOIS
        self._log.info("[auto_recon] Phase 1: WHOIS for %s", target)
        try:
            whois_result = await self._tool_whois_lookup({"target": target})
            recon_report["phases"]["whois"] = whois_result["content"][0]["text"][:2000]
        except Exception as exc:
            recon_report["phases"]["whois"] = f"Error: {exc}"

        # Phase 2: DNS
        self._log.info("[auto_recon] Phase 2: DNS for %s", target)
        try:
            dig_result = await self._tool_dig_lookup({"target": target, "record_type": "A"})
            recon_report["phases"]["dns_A"] = dig_result["content"][0]["text"][:1000]
        except Exception as exc:
            recon_report["phases"]["dns_A"] = f"Error: {exc}"

        # Phase 3: Nmap scan
        self._log.info("[auto_recon] Phase 3: Nmap for %s", target)
        try:
            nmap_args = {"target": target, "scan_type": "quick", "timing": "T4"}
            if ports:
                nmap_args["ports"] = ports
            nmap_result = await self._tool_nmap_scan(nmap_args)
            nmap_output = nmap_result["content"][0]["text"]
            recon_report["phases"]["nmap"] = nmap_output[:5000]

            # Detect web ports from nmap results
            open_web_ports = []
            try:
                nmap_data = json.loads(nmap_output)
                for host in nmap_data.get("hosts", []):
                    for port_info in host.get("ports", []):
                        if port_info.get("state") == "open":
                            port_num = int(port_info["port"])
                            svc = port_info.get("service", "")
                            if port_num in web_ports or svc in ("http", "https", "http-proxy", "http-alt"):
                                scheme = "https" if port_num == 443 or "ssl" in svc or "https" in svc else "http"
                                open_web_ports.append((scheme, port_num))
            except (json.JSONDecodeError, KeyError, ValueError):
                # Fallback: assume 80 and 443 might be open
                open_web_ports = [("http", 80), ("https", 443)]

        except Exception as exc:
            recon_report["phases"]["nmap"] = f"Error: {exc}"
            open_web_ports = []

        # Phase 4: WhatWeb on discovered web ports
        if open_web_ports:
            self._log.info("[auto_recon] Phase 4: WhatWeb on %d web ports", len(open_web_ports))
            for scheme, port in open_web_ports[:3]:  # max 3 ports
                url = f"{scheme}://{target}:{port}" if port not in (80, 443) else f"{scheme}://{target}"
                try:
                    ww_result = await self._tool_whatweb_scan({"target_url": url, "aggression": "1"})
                    recon_report["phases"][f"whatweb_{port}"] = ww_result["content"][0]["text"][:2000]
                except Exception as exc:
                    recon_report["phases"][f"whatweb_{port}"] = f"Error: {exc}"

            # Phase 5: Gobuster on first web port
            self._log.info("[auto_recon] Phase 5: Gobuster")
            scheme, port = open_web_ports[0]
            url = f"{scheme}://{target}:{port}" if port not in (80, 443) else f"{scheme}://{target}"
            try:
                gb_result = await self._tool_gobuster_dir({
                    "target_url": url,
                    "wordlist": wordlist,
                    "threads": 10,
                })
                recon_report["phases"]["gobuster"] = gb_result["content"][0]["text"][:5000]
            except Exception as exc:
                recon_report["phases"]["gobuster"] = f"Error: {exc}"
        else:
            recon_report["phases"]["web_scan"] = "No web ports detected - skipping whatweb and gobuster."

        return self._ok(json.dumps(recon_report, indent=2))

    async def _tool_masscan_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        ports = InputSanitizer.sanitize_generic(args.get("ports", "1-1000"))
        rate = int(args.get("rate", 1000))
        extra = args.get("extra_args", "")

        cmd = ["masscan", target, "-p", ports, "--rate", str(rate), "--open"]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("masscan"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_subfinder_recon(self, args: dict) -> dict:
        domain = InputSanitizer.sanitize_target(args["domain"])
        sources = args.get("sources", "")
        extra = args.get("extra_args", "")

        cmd = ["subfinder", "-d", domain]
        if args.get("silent", True):
            cmd.append("-silent")
        if sources:
            cmd += ["-s", InputSanitizer.sanitize_generic(sources)]
        if args.get("all_sources", False):
            cmd.append("-all")
        if args.get("recursive", False):
            cmd.append("-recursive")
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("subfinder"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_naabu_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_target(args["target"])
        self._scope_check(target)
        ports = args.get("ports", "")
        top_ports = args.get("top_ports", "")
        rate = int(args.get("rate", 1000))
        exclude_ports = args.get("exclude_ports", "")
        extra = args.get("extra_args", "")

        cmd = ["naabu", "-host", target, "-rate", str(rate), "-silent"]
        if ports:
            cmd += ["-p", InputSanitizer.sanitize_generic(ports)]
        if top_ports:
            cmd += ["-top-ports", InputSanitizer.sanitize_generic(top_ports)]
        if exclude_ports:
            cmd += ["-exclude-ports", InputSanitizer.sanitize_generic(exclude_ports)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("naabu"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_pd_httpx_probe(self, args: dict) -> dict:
        target = args.get("target", "").strip()
        input_file = args.get("input_file", "").strip()
        if not target and not input_file:
            return self._error("Provide target or input_file.")

        cmd = ["pd-httpx", "-silent"]
        if target:
            cmd += ["-u", InputSanitizer.sanitize_target(target)]
        if input_file:
            cmd += ["-l", InputSanitizer.sanitize_path(input_file)]
        if args.get("ports"):
            cmd += ["-p", InputSanitizer.sanitize_generic(args["ports"])]
        if args.get("title", True):
            cmd.append("-title")
        if args.get("tech_detect", True):
            cmd.append("-tech-detect")
        if args.get("status_code", True):
            cmd.append("-sc")
        if args.get("follow_redirects", False):
            cmd.append("-fr")
        if args.get("json_output", False):
            cmd.append("-j")
        if args.get("extra_args"):
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(args["extra_args"]))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("pd_httpx"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_katana_crawl(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        depth = int(args.get("depth", 2))
        known_files = args.get("known_files", "")
        proxy = args.get("proxy", "")
        extra = args.get("extra_args", "")

        cmd = ["katana", "-u", url, "-d", str(depth), "-silent"]
        if args.get("js_crawl", True):
            cmd.append("-jc")
        if args.get("headless", False):
            cmd.append("-hl")
        if known_files:
            cmd += ["-kf", InputSanitizer.sanitize_generic(known_files)]
        if proxy:
            cmd += ["-proxy", InputSanitizer.sanitize_url(proxy)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("katana"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_theharvester_recon(self, args: dict) -> dict:
        domain = InputSanitizer.sanitize_target(args["domain"])
        sources = InputSanitizer.sanitize_generic(args.get("sources", "google,bing,crtsh"))
        limit = int(args.get("limit", 100))
        dns_brute = args.get("dns_brute", False)

        cmd = ["theHarvester", "-d", domain, "-b", sources, "-l", str(limit)]
        if dns_brute:
            cmd += ["-c"]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("theharvester"))
        return self._ok(stdout if stdout else stderr)
