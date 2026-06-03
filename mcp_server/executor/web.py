"""Web 扫描、漏洞查询与内容发现工具实现。"""

import asyncio
import json
import re
import shlex
import urllib.error
import urllib.parse
import urllib.request

from ..input_sanitizer import InputSanitizer
from ..parsers import OutputParsers


class WebToolsMixin:
    async def _tool_nikto_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        tuning = args.get("tuning", "")
        max_time = args.get("max_time", 0)
        extra = args.get("extra_args", "")

        cmd = ["nikto", "-h", url]
        if tuning:
            cmd += ["-Tuning", InputSanitizer.sanitize_generic(tuning)]
        if max_time and max_time > 0:
            cmd += ["-maxtime", str(int(max_time))]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        timeout = int(max_time) if max_time and max_time > 0 else self._timeout_for("nikto")
        stdout, stderr, rc = await self._run_subprocess(cmd, timeout)

        raw = stdout if stdout else stderr
        # [MEJORA 3] Parse nikto output
        parsed = OutputParsers.parse_nikto(raw)
        if parsed:
            return self._ok(json.dumps(parsed, indent=2))
        return self._ok(raw)

    async def _tool_gobuster_dir(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        wordlist = InputSanitizer.sanitize_path(args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        extensions = args.get("extensions", "")
        threads = args.get("threads", 10)
        status_codes = args.get("status_codes", "")

        proxy = args.get("proxy", "")
        cmd = ["gobuster", "dir", "-u", url, "-w", wordlist, "-t", str(int(threads))]
        if extensions:
            cmd += ["-x", InputSanitizer.sanitize_generic(extensions)]
        if status_codes:
            cmd += ["-s", InputSanitizer.sanitize_generic(status_codes)]
        if proxy:
            cmd += ["--proxy", InputSanitizer.sanitize_url(proxy)]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("gobuster"))

        raw = stdout if stdout else stderr
        # [MEJORA 3] Parse gobuster output
        parsed = OutputParsers.parse_gobuster(raw)
        if parsed:
            return self._ok(json.dumps(parsed, indent=2))
        return self._ok(raw)

    async def _tool_sqlmap_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        data = args.get("data", "")
        method = args.get("method", "GET")
        level = int(args.get("level", 1))
        risk = int(args.get("risk", 1))
        tamper = args.get("tamper", "")
        extra = args.get("extra_args", "")

        cmd = ["sqlmap", "-u", url, "--batch", f"--level={level}", f"--risk={risk}"]
        if method == "POST" and data:
            cmd += ["--data", InputSanitizer.sanitize_generic(data)]
        if tamper:
            cmd += ["--tamper", InputSanitizer.sanitize_generic(tamper)]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("sqlmap"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_wfuzz_scan(self, args: dict) -> dict:
        url = args["target_url"].strip()
        if "FUZZ" not in url:
            return self._error("target_url must contain the 'FUZZ' keyword.")
        wordlist = InputSanitizer.sanitize_path(args["wordlist"])
        hide_codes = args.get("hide_codes", "404")
        hide_chars = args.get("hide_chars", "")
        extra = args.get("extra_args", "")

        cmd = ["wfuzz", "-w", wordlist, "--hc", InputSanitizer.sanitize_generic(hide_codes)]
        if hide_chars:
            cmd += ["--hh", InputSanitizer.sanitize_generic(hide_chars)]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
        cmd.append(url)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("wfuzz"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_searchsploit_query(self, args: dict) -> dict:
        query = InputSanitizer.sanitize_generic(args["query"])
        exact = args.get("exact", False)
        json_output = args.get("json_output", True)

        cmd = ["searchsploit"]
        if exact:
            cmd.append("--exact")
        if json_output:
            cmd.append("--json")
        cmd += shlex.split(query)

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("searchsploit"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_cve_lookup(self, args: dict) -> dict:
        cve_id               = args.get("cve_id", "").strip()
        keyword              = args.get("keyword", "").strip()
        exact_match          = bool(args.get("exact_match", False))
        cpe_name             = args.get("cpe_name", "").strip()
        virtual_match_string = args.get("virtual_match_string", "").strip()
        cvss_severity        = args.get("cvss_severity", "").strip().upper()
        pub_start_date       = args.get("pub_start_date", "").strip()
        pub_end_date         = args.get("pub_end_date", "").strip()
        last_mod_start_date  = args.get("last_mod_start_date", "").strip()
        last_mod_end_date    = args.get("last_mod_end_date", "").strip()
        no_rejected          = bool(args.get("no_rejected", False))
        max_results          = int(args.get("max_results", 5))

        # ── Validation ────────────────────────────────────────────────────────
        search_inputs = [cve_id, keyword, cpe_name, virtual_match_string,
                         pub_start_date, last_mod_start_date]
        if not any(search_inputs):
            return self._error(
                "Provide at least one search input: cve_id, keyword, cpe_name, "
                "virtual_match_string, pub_start_date, or last_mod_start_date."
            )
        if cve_id and any([keyword, cpe_name, virtual_match_string]):
            return self._error(
                "cve_id is mutually exclusive with keyword, cpe_name, and virtual_match_string."
            )
        if exact_match and not keyword:
            return self._error("exact_match requires keyword.")
        if cvss_severity and cvss_severity not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            return self._error(
                f"Invalid cvss_severity '{cvss_severity}'. Must be: LOW, MEDIUM, HIGH, CRITICAL."
            )
        if cve_id and not re.match(r'^CVE-\d{4}-\d{4,}$', cve_id, re.IGNORECASE):
            return self._error(f"Invalid CVE ID format: '{cve_id}'. Expected CVE-YYYY-NNNNN.")

        # ── Build NVD 2.0 API params ──────────────────────────────────────────
        def _nvd_date(s: str) -> str:
            """Normalise YYYY-MM-DD → YYYY-MM-DDTHH:MM:SS.000 for the NVD 2.0 API."""
            return s if "T" in s else f"{s}T00:00:00.000"

        base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        params: dict[str, str] = {}

        if cve_id:
            params["cveId"] = cve_id.upper()
        else:
            if keyword:
                params["keywordSearch"] = keyword
                if exact_match:
                    params["keywordExactMatch"] = ""
            if cpe_name:
                params["cpeName"] = cpe_name
            if virtual_match_string:
                params["virtualMatchString"] = virtual_match_string
            if cvss_severity:
                params["cvssV3Severity"] = cvss_severity
            if pub_start_date:
                params["pubStartDate"] = _nvd_date(pub_start_date)
            if pub_end_date:
                params["pubEndDate"] = _nvd_date(pub_end_date)
            if last_mod_start_date:
                params["lastModStartDate"] = _nvd_date(last_mod_start_date)
            if last_mod_end_date:
                params["lastModEndDate"] = _nvd_date(last_mod_end_date)
            if no_rejected:
                params["noRejected"] = ""
            params["resultsPerPage"] = str(max_results)

        url = f"{base_url}?{urllib.parse.urlencode(params)}"

        def _fetch() -> str:
            req = urllib.request.Request(url, headers={"User-Agent": "the host UI-CVE-Lookup/1.0"})
            with urllib.request.urlopen(req) as resp:
                return resp.read().decode("utf-8")

        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, _fetch)
            data = json.loads(raw)
        except urllib.error.HTTPError as e:
            return self._error(f"NVD API HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            return self._error(f"NVD API connection error: {e.reason}")
        except Exception as e:
            return self._error(f"CVE lookup failed: {e}")

        total = data.get("totalResults", 0)
        items = data.get("vulnerabilities", [])

        if not items:
            # Build a human-readable label for the query that was run
            parts = []
            if cve_id:
                parts.append(cve_id)
            if keyword:
                parts.append(f"keyword='{keyword}'" + (" (exact)" if exact_match else ""))
            if cpe_name:
                parts.append(f"cpe='{cpe_name}'")
            if virtual_match_string:
                parts.append(f"match='{virtual_match_string}'")
            if cvss_severity:
                parts.append(f"severity={cvss_severity}")
            if pub_start_date or pub_end_date:
                parts.append(f"published={pub_start_date or ''}..{pub_end_date or ''}")
            if last_mod_start_date or last_mod_end_date:
                parts.append(f"modified={last_mod_start_date or ''}..{last_mod_end_date or ''}")
            query_label = ", ".join(parts) if parts else "the given query"
            return self._ok(f"No CVEs found for {query_label}.")

        lines: list[str] = []
        if not cve_id:
            # Build a compact query summary for the header
            summary_parts = []
            if keyword:
                summary_parts.append(f"keyword='{keyword}'" + (" (exact)" if exact_match else ""))
            if cpe_name:
                summary_parts.append(f"cpe='{cpe_name}'")
            if virtual_match_string:
                summary_parts.append(f"match='{virtual_match_string}'")
            if cvss_severity:
                summary_parts.append(f"severity={cvss_severity}")
            if pub_start_date or pub_end_date:
                summary_parts.append(f"published={pub_start_date or '*'}..{pub_end_date or '*'}")
            if last_mod_start_date or last_mod_end_date:
                summary_parts.append(f"modified={last_mod_start_date or '*'}..{last_mod_end_date or '*'}")
            query_summary = ", ".join(summary_parts) if summary_parts else "all"
            lines.append(
                f"NVD search [{query_summary}] — {total} total result(s), showing {len(items)}:\n"
            )

        for item in items:
            cve = item.get("cve", {})
            vid = cve.get("id", "N/A")
            published = cve.get("published", "")[:10]
            modified = cve.get("lastModified", "")[:10]
            status = cve.get("vulnStatus", "")

            # Description (English preferred)
            descs = cve.get("descriptions", [])
            description = next(
                (d["value"] for d in descs if d.get("lang") == "en"),
                descs[0]["value"] if descs else "No description available.",
            )

            # CVSS scores
            metrics = cve.get("metrics", {})
            cvss_info: list[str] = []
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                entries = metrics.get(key, [])
                if entries:
                    m = entries[0].get("cvssData", {})
                    version = m.get("version", key[-2:])
                    score = m.get("baseScore", "N/A")
                    severity = m.get("baseSeverity") or entries[0].get("baseSeverity", "")
                    vector = m.get("vectorString", "")
                    cvss_info.append(f"CVSSv{version}: {score} ({severity}) — {vector}")
                    break  # prefer the highest version available

            # CPEs / affected products
            configs = cve.get("configurations", [])
            affected_all: list[str] = []
            for cfg in configs:
                for node in cfg.get("nodes", []):
                    for cpe_match in node.get("cpeMatch", []):
                        if cpe_match.get("vulnerable"):
                            affected_all.append(cpe_match.get("criteria", ""))
            affected = affected_all[:10]  # cap to avoid huge output

            # Extract unique vendor:product pairs for SERVICE BINDING annotation
            bound_products: set[str] = set()
            for cpe in affected_all:
                cpe_parts = cpe.split(":")
                # cpe:2.3:part:vendor:product:version:...
                if len(cpe_parts) >= 5:
                    vendor = cpe_parts[3].replace("_", " ")
                    product = cpe_parts[4].replace("_", " ")
                    if vendor not in ("*", "") and product not in ("*", ""):
                        bound_products.add(f"{vendor} {product}".strip())

            # References
            refs = [r.get("url", "") for r in cve.get("references", [])[:5]]

            # Format entry
            lines.append(f"{'='*60}")
            lines.append(f"CVE ID   : {vid}")
            if bound_products:
                binding = ", ".join(sorted(bound_products))
                lines.append(
                    f"SERVICE BINDING: [{binding}] (derived from CPE data). "
                    "This CVE must only be associated with a detected service "
                    "that matches one of these products. Never reassign to an "
                    "unrelated service even if it runs on the same host."
                )
            else:
                lines.append(
                    "SERVICE BINDING: No CPE data available. "
                    "Bind this CVE only to the service explicitly named in the description below. "
                    "Do not associate with any other detected service."
                )
            lines.append(f"Status   : {status}")
            lines.append(f"Published: {published}  |  Modified: {modified}")
            if cvss_info:
                lines.append(f"CVSS     : {cvss_info[0]}")
            else:
                lines.append("CVSS     : Not available")
            lines.append(f"\nDescription:\n{description}")
            if affected:
                lines.append(f"\nAffected CPEs ({len(affected)}):")
                for cpe in affected:
                    lines.append(f"  {cpe}")
            if refs:
                lines.append(f"\nReferences:")
                for r in refs:
                    lines.append(f"  {r}")
            lines.append("")

        return self._ok("\n".join(lines))

    async def _tool_dirb_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        wordlist = InputSanitizer.sanitize_path(args.get("wordlist", "/usr/share/wordlists/dirb/common.txt"))
        extra = args.get("extra_args", "")

        cmd = ["dirb", url, wordlist]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("dirb"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_whatweb_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        aggression = args.get("aggression", "1")
        extra = args.get("extra_args", "")

        cmd = ["whatweb", "-a", str(aggression), url]
        if extra:
            cmd += shlex.split(InputSanitizer.sanitize_generic(extra))

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("whatweb"))

        raw = stdout if stdout else stderr
        # [MEJORA 3] Parse whatweb output
        parsed = OutputParsers.parse_whatweb(raw)
        if parsed:
            return self._ok(json.dumps(parsed, indent=2))
        return self._ok(raw)

    async def _tool_wpscan(self, args: dict) -> dict:
        """Escáner de WordPress"""
        url = InputSanitizer.sanitize_url(args["target_url"])

        cmd = ["wpscan", "--url", url, "--no-banner", "--format", "json"]

        if args.get("enumerate"):
            enumerate_str = ",".join(args["enumerate"])
            cmd += ["--enumerate", enumerate_str]
        if args.get("username") and args.get("password_list"):
            cmd += ["--usernames", args["username"], "--passwords", args["password_list"]]
        if args.get("api_token"):
            cmd += ["--api-token", args["api_token"]]
        if args.get("random_agent"):
            cmd += ["--random-user-agent"]
        if args.get("stealthy"):
            cmd += ["--stealthy"]
        if args.get("proxy"):
            cmd += ["--proxy", args["proxy"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("wpscan"))

        # Intentar parsear JSON
        try:
            data = json.loads(stdout)
            return self._ok(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            return self._ok(stdout if stdout else stderr)

    async def _tool_joomscan(self, args: dict) -> dict:
        """Escáner de Joomla"""
        url = InputSanitizer.sanitize_url(args["target_url"])

        cmd = ["joomscan", "--url", url]

        if args.get("enumerate"):
            cmd += ["--enumerate", args["enumerate"]]
        if args.get("cookie"):
            cmd += ["--cookie", args["cookie"]]
        if args.get("user_agent"):
            cmd += ["--user-agent", args["user_agent"]]
        if args.get("proxy"):
            cmd += ["--proxy", args["proxy"]]

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("joomscan"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_zap_scan(self, args: dict) -> dict:
        """Escaneo con OWASP ZAP"""
        url = InputSanitizer.sanitize_url(args["target_url"])
        scan_type = args.get("scan_type", "full")

        # Asumimos que ZAP está corriendo en modo daemon
        zap_api = f"http://localhost:{args.get('port', 8080)}"

        import aiohttp

        async with aiohttp.ClientSession() as session:
            if scan_type in ["spider", "full"]:
                # Iniciar spider
                spider_url = f"{zap_api}/JSON/spider/action/scan/"
                params = {"url": url, "apikey": args.get("api_key", "")}
                if args.get("max_children"):
                    params["maxChildren"] = args["max_children"]

                async with session.get(spider_url, params=params) as resp:
                    spider_data = await resp.json()

            if scan_type in ["active", "full"]:
                # Iniciar escaneo activo
                active_url = f"{zap_api}/JSON/ascanner/action/scan/"
                params = {"url": url, "apikey": args.get("api_key", "")}
                if args.get("context_name"):
                    params["contextName"] = args["context_name"]

                async with session.get(active_url, params=params) as resp:
                    active_data = await resp.json()

            # Obtener resultados
            results_url = f"{zap_api}/JSON/core/view/alerts/"
            params = {"baseurl": url, "apikey": args.get("api_key", "")}
            async with session.get(results_url, params=params) as resp:
                alerts = await resp.json()

        return self._ok(json.dumps(alerts, indent=2))

    async def _tool_feroxbuster_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        wordlist = InputSanitizer.sanitize_path(
            args.get("wordlist", "/usr/share/seclists/Discovery/Web-Content/common.txt")
        )
        threads = int(args.get("threads", 50))
        depth = int(args.get("depth", 2))
        extensions = args.get("extensions", "")
        status_codes = args.get("status_codes", "")
        filter_codes = args.get("filter_codes", "")
        proxy = args.get("proxy", "")
        extra = args.get("extra_args", "")

        cmd = [
            "feroxbuster", "--url", url, "--wordlist", wordlist,
            "--threads", str(threads), "--depth", str(depth), "--no-state",
        ]
        if extensions:
            cmd += ["--extensions", InputSanitizer.sanitize_generic(extensions)]
        if status_codes:
            cmd += ["--status-codes", InputSanitizer.sanitize_generic(status_codes)]
        if filter_codes:
            cmd += ["--filter-status", InputSanitizer.sanitize_generic(filter_codes)]
        if proxy:
            cmd += ["--proxy", InputSanitizer.sanitize_url(proxy)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("feroxbuster"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_dirsearch_scan(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["target_url"])
        wordlist = InputSanitizer.sanitize_path(
            args.get("wordlist", "/usr/share/seclists/Discovery/Web-Content/common.txt")
        )
        threads = int(args.get("threads", 30))
        extensions = args.get("extensions", "")
        status_codes = args.get("status_codes", "")
        exclude_status = args.get("exclude_status", "404")
        proxy = args.get("proxy", "")
        extra = args.get("extra_args", "")

        cmd = ["dirsearch", "-u", url, "-w", wordlist, "-t", str(threads), "--no-color"]
        if extensions:
            cmd += ["-e", InputSanitizer.sanitize_generic(extensions)]
        if args.get("recursive", False):
            cmd.append("-r")
        if status_codes:
            cmd += ["--include-status", InputSanitizer.sanitize_generic(status_codes)]
        if exclude_status:
            cmd += ["--exclude-status", InputSanitizer.sanitize_generic(exclude_status)]
        if proxy:
            cmd += ["--proxy", InputSanitizer.sanitize_url(proxy)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("dirsearch"))
        return self._ok(stdout if stdout else stderr)

    async def _tool_ffuf_fuzz(self, args: dict) -> dict:
        url = InputSanitizer.sanitize_url(args["url"])
        if "FUZZ" not in url:
            url = url.rstrip("/") + "/FUZZ"
        wordlist = InputSanitizer.sanitize_path(
            args.get("wordlist", "/usr/share/seclists/Discovery/Web-Content/common.txt")
        )
        mode = args.get("mode", "dir")
        threads = int(args.get("threads", 40))
        filter_codes = args.get("filter_codes", "404")
        match_codes = args.get("match_codes", "")
        extensions = args.get("extensions", "")
        proxy = args.get("proxy", "")
        extra = args.get("extra_args", "")

        cmd = ["ffuf", "-u", url, "-w", wordlist, "-t", str(threads), "-of", "json"]

        if mode == "vhost":
            cmd += ["-H", f"Host: FUZZ.{url.split('/')[2]}"]
        elif mode == "param":
            cmd += ["-X", "GET"]

        if extensions:
            cmd += ["-e", InputSanitizer.sanitize_generic(extensions)]
        if filter_codes:
            cmd += ["-fc", InputSanitizer.sanitize_generic(filter_codes)]
        if match_codes:
            cmd += ["-mc", InputSanitizer.sanitize_generic(match_codes)]
        if proxy:
            cmd += ["-x", InputSanitizer.sanitize_url(proxy)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("ffuf"))
        # ffuf outputs JSON — try to parse and summarise hits
        try:
            data = json.loads(stdout)
            results = data.get("results", [])
            if results:
                summary = [
                    f"{r['status']} {r['length']}B  {r['url']}"
                    for r in results
                ]
                return self._ok(f"ffuf found {len(results)} result(s):\n" + "\n".join(summary))
        except (json.JSONDecodeError, KeyError):
            pass
        return self._ok(stdout if stdout else stderr)

    async def _tool_nuclei_scan(self, args: dict) -> dict:
        target = InputSanitizer.sanitize_url(args["target"])
        templates = args.get("templates", "")
        severity = args.get("severity", "")
        rate_limit = int(args.get("rate_limit", 150))
        proxy = args.get("proxy", "")
        extra = args.get("extra_args", "")

        cmd = ["nuclei", "-u", target, "-rl", str(rate_limit), "-silent"]

        if templates:
            cmd += ["-t", InputSanitizer.sanitize_generic(templates)]
        if severity:
            cmd += ["-severity", InputSanitizer.sanitize_generic(severity)]
        if proxy:
            cmd += ["-proxy", InputSanitizer.sanitize_url(proxy)]
        if extra:
            try:
                cmd += shlex.split(InputSanitizer.sanitize_generic(extra))
            except ValueError as e:
                return self._error(f"Invalid extra_args: {e}")

        stdout, stderr, rc = await self._run_subprocess(cmd, self._timeout_for("nuclei"))
        return self._ok(stdout if stdout else stderr)
