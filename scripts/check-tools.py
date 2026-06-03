#!/usr/bin/env python3
"""Smoke-check the running kail-mcp container and its exposed MCP tools.

Default mode:
  - asks the MCP server for tools/list via stdio
  - checks each required binary/path inside the container
  - runs a lightweight version/help command for each unique binary

Optional functional mode starts a tiny temporary HTTP server bound to an IP
address and calls a small set of MCP tools against that IP URL. It does not add
authorization/scope policy; that belongs elsewhere in the stack.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import ipaddress
import json
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTAINER_APP_DIR = "/opt/kail-mcp"

TOOL_BINARY_MAP: dict[str, str | None] = {
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
    "shell_command": None,
    "auto_recon": "nmap",
    "get_scan_history": None,
    "generate_report": None,
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

VERSION_COMMANDS: dict[str, list[str]] = {
    "nmap": ["nmap", "--version"],
    "nikto": ["nikto", "-Version"],
    "gobuster": ["gobuster", "version"],
    "sqlmap": ["sqlmap", "--version"],
    "hydra": ["hydra", "-h"],
    "enum4linux": ["enum4linux", "-h"],
    "wfuzz": ["wfuzz", "--version"],
    "nc": ["nc", "-h"],
    "searchsploit": ["searchsploit", "--version"],
    "hashcat": ["hashcat", "--version"],
    "john": ["john", "--list=build-info"],
    "dirb": ["dirb"],
    "whatweb": ["whatweb", "--version"],
    "whois": ["whois", "--version"],
    "dig": ["dig", "-v"],
    "msfconsole": ["msfconsole", "-v"],
    "msfvenom": ["msfvenom", "--help"],
    "bettercap": ["bettercap", "-version"],
    "responder": ["responder", "-h"],
    "crackmapexec": ["crackmapexec", "--version"],
    "bloodhound-python": ["bloodhound-python", "--version"],
    "wpscan": ["wpscan", "--version"],
    "joomscan": ["joomscan", "--version"],
    "zaproxy": ["zaproxy", "-version"],
    "medusa": ["medusa", "-h"],
    "ncrack": ["ncrack", "--version"],
    "setoolkit": ["setoolkit", "--help"],
    "beef-xss": ["beef-xss", "--help"],
    "tcpdump": ["tcpdump", "--version"],
    "ettercap": ["ettercap", "--version"],
    "aircrack-ng": ["aircrack-ng", "--help"],
    "wifite": ["wifite", "--help"],
    "crunch": ["crunch", "--version"],
    "cewl": ["cewl", "--help"],
    "masscan": ["masscan", "--version"],
    "feroxbuster": ["feroxbuster", "--version"],
    "dirsearch": ["dirsearch", "--version"],
    "ffuf": ["ffuf", "-V"],
    "nuclei": ["nuclei", "-version"],
    "subfinder": ["subfinder", "-version"],
    "naabu": ["naabu", "-version"],
    "pd-httpx": ["pd-httpx", "-version"],
    "katana": ["katana", "-version"],
    # netexec may emit first-run setup text before version output; command
    # existence is the stable headless smoke check.
    "netexec": ["sh", "-lc", "command -v netexec"],
    # evil-winrm is primarily interactive and may not print help reliably in
    # headless package builds; command existence is the meaningful smoke check.
    "evil-winrm": ["sh", "-lc", "command -v evil-winrm"],
    "certipy-ad": ["certipy-ad", "-h"],
    "kerbrute": ["kerbrute", "version"],
    "enum4linux-ng": ["enum4linux-ng", "-h"],
    "theHarvester": ["theHarvester", "--version"],
}

VERSION_TIMEOUTS: dict[str, int] = {
    "msfconsole": 60,
    "msfvenom": 60,
    "zaproxy": 60,
    "setoolkit": 45,
    "beef-xss": 45,
    "netexec": 45,
    "evil-winrm": 45,
    "certipy-ad": 45,
}


def emit_progress(enabled: bool, message: str) -> None:
    if enabled:
        print(f"[check-tools] {message}", file=sys.stderr, flush=True)


@dataclass
class ToolCheck:
    name: str
    requirement: str
    exposed: bool
    exists: bool
    version_ok: bool | None
    version_line: str


@dataclass
class FunctionalCheck:
    tool: str
    ok: bool
    target: str
    detail: str


def run(cmd: list[str], *, timeout: int = 20, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=check,
    )


def docker_base(container: str, use_sudo: bool, *, interactive: bool = False) -> list[str]:
    base = ["docker"]
    if use_sudo:
        base.insert(0, "sudo")
    cmd = base + ["exec"]
    if interactive:
        cmd.append("-i")
    return cmd + [container]


def docker_exec(container: str, args: list[str], *, use_sudo: bool, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return run(docker_base(container, use_sudo) + args, timeout=timeout)


def detect_sudo(progress_enabled: bool) -> bool:
    if shutil.which("docker") is None:
        raise SystemExit("docker command not found")

    emit_progress(progress_enabled, "checking Docker access")
    direct = run(["docker", "ps"], timeout=5)
    if direct.returncode == 0:
        emit_progress(progress_enabled, "using docker directly")
        return False

    if shutil.which("sudo") is None:
        emit_progress(progress_enabled, "docker direct access failed; sudo not found")
        return False

    emit_progress(progress_enabled, "docker direct access failed; trying sudo -n docker")
    sudo = run(["sudo", "-n", "docker", "ps"], timeout=5)
    if sudo.returncode == 0:
        emit_progress(progress_enabled, "using sudo docker")
    return sudo.returncode == 0


def get_mcp_tools(container: str, use_sudo: bool, progress_enabled: bool) -> set[str]:
    emit_progress(progress_enabled, f"querying MCP tools/list from container {container!r}")
    messages = "\n".join(
        [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "check-tools", "version": "1.0"},
                    },
                }
            ),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            "",
        ]
    )

    proc = subprocess.run(
        docker_base(container, use_sudo, interactive=True) + ["python3", f"{CONTAINER_APP_DIR}/mcp_server.py"],
        cwd=PROJECT_ROOT,
        input=messages,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"MCP tools/list failed:\n{proc.stderr or proc.stdout}")

    tools: set[str] = set()
    for line in proc.stdout.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("id") == 2:
            tools = {tool["name"] for tool in payload.get("result", {}).get("tools", [])}
            break

    if not tools:
        raise RuntimeError(f"No tools/list response found. stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}")
    emit_progress(progress_enabled, f"MCP tools/list returned {len(tools)} tools")
    return tools


def call_mcp_tool(
    container: str,
    use_sudo: bool,
    tool_name: str,
    arguments: dict,
    timeout: int = 90,
) -> dict:
    messages = "\n".join(
        [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "check-tools", "version": "1.0"},
                    },
                }
            ),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                }
            ),
            "",
        ]
    )
    proc = subprocess.run(
        docker_base(container, use_sudo, interactive=True) + ["python3", f"{CONTAINER_APP_DIR}/mcp_server.py"],
        cwd=PROJECT_ROOT,
        input=messages,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if proc.returncode != 0:
        return {"isError": True, "content": [{"type": "text", "text": proc.stderr or proc.stdout}]}

    for line in proc.stdout.splitlines():
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if payload.get("id") == 2:
            if "error" in payload:
                return {"isError": True, "content": [{"type": "text", "text": str(payload["error"])}]}
            return payload.get("result", {})
    return {"isError": True, "content": [{"type": "text", "text": "missing tools/call response"}]}


def mcp_text(result: dict) -> str:
    chunks = result.get("content", [])
    return "\n".join(str(chunk.get("text", "")) for chunk in chunks if isinstance(chunk, dict)).strip()


def check_requirement(container: str, requirement: str | None, use_sudo: bool) -> tuple[bool, str]:
    if requirement is None:
        return True, "(server-only)"

    if "/" in requirement:
        try:
            proc = docker_exec(container, ["test", "-e", requirement], use_sudo=use_sudo, timeout=5)
        except subprocess.TimeoutExpired:
            return False, requirement
        return proc.returncode == 0, requirement

    try:
        proc = docker_exec(container, ["sh", "-lc", f"command -v {requirement}"], use_sudo=use_sudo, timeout=5)
    except subprocess.TimeoutExpired:
        return False, requirement
    path = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else requirement
    return proc.returncode == 0, path


def check_version(container: str, binary: str | None, use_sudo: bool) -> tuple[bool | None, str]:
    if binary is None or "/" in binary:
        return None, ""

    cmd = VERSION_COMMANDS.get(binary, [binary, "--version"])
    try:
        proc = docker_exec(container, cmd, use_sudo=use_sudo, timeout=VERSION_TIMEOUTS.get(binary, 20))
    except subprocess.TimeoutExpired:
        return False, "timed out starting version/help command"
    text = (proc.stdout + "\n" + proc.stderr).strip()
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")

    # Some CLI tools print help to stderr and exit non-zero for -h/no-arg; that still
    # proves the executable can start.
    if proc.returncode == 0:
        return True, first_line
    if text and any(token.lower() in text.lower() for token in (binary, "usage", "version")):
        return True, first_line
    return False, first_line or f"exit {proc.returncode}"


def collect_checks(container: str, use_sudo: bool, progress_enabled: bool) -> list[ToolCheck]:
    exposed = get_mcp_tools(container, use_sudo, progress_enabled)
    version_cache: dict[str | None, tuple[bool | None, str]] = {}
    checks: list[ToolCheck] = []
    total = len(TOOL_BINARY_MAP)

    for index, (tool_name, requirement) in enumerate(TOOL_BINARY_MAP.items(), start=1):
        requirement_label = requirement or "server-only"
        emit_progress(
            progress_enabled,
            f"[{index}/{total}] {tool_name}: checking {requirement_label}",
        )
        exists, label = check_requirement(container, requirement, use_sudo)
        if requirement not in version_cache and exists:
            if requirement is None:
                emit_progress(progress_enabled, f"[{index}/{total}] {tool_name}: server-only check")
            elif "/" in requirement:
                emit_progress(progress_enabled, f"[{index}/{total}] {tool_name}: path exists")
            else:
                emit_progress(
                    progress_enabled,
                    f"[{index}/{total}] {tool_name}: running {requirement} version/help",
                )
            version_cache[requirement] = check_version(container, requirement, use_sudo)
        version_ok, version_line = version_cache.get(requirement, (None, ""))
        check = ToolCheck(
            name=tool_name,
            requirement=label if exists else str(requirement or "(server-only)"),
            exposed=tool_name in exposed,
            exists=exists,
            version_ok=version_ok,
            version_line=version_line,
        )
        checks.append(check)
        emit_progress(progress_enabled, f"[{index}/{total}] {tool_name}: {status(check)}")

    extra_exposed = sorted(exposed - set(TOOL_BINARY_MAP))
    for tool_name in extra_exposed:
        emit_progress(progress_enabled, f"extra exposed tool not in script map: {tool_name}")
        checks.append(ToolCheck(tool_name, "(not in script map)", True, False, None, ""))

    return checks


def validate_ipv4(value: str) -> str:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not an IP address") from exc
    if ip.version != 4:
        raise argparse.ArgumentTypeError("functional checks currently require an IPv4 address")
    return str(ip)


def default_target_ip() -> str:
    docker0 = run(["ip", "-4", "-o", "addr", "show", "dev", "docker0"], timeout=5)
    if docker0.returncode == 0:
        for part in docker0.stdout.split():
            if "/" in part:
                try:
                    return str(ipaddress.ip_interface(part).ip)
                except ValueError:
                    pass

    all_addrs = run(["ip", "-4", "-o", "addr", "show", "scope", "global"], timeout=5)
    if all_addrs.returncode == 0:
        for part in all_addrs.stdout.split():
            if "/" in part:
                try:
                    return str(ipaddress.ip_interface(part).ip)
                except ValueError:
                    pass

    return "127.0.0.1"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def write_container_wordlist(container: str, use_sudo: bool) -> str:
    path = "/tmp/check-tools-wordlist.txt"
    proc = docker_exec(
        container,
        ["sh", "-lc", "printf 'admin\nindex.html\nmissing\n' > /tmp/check-tools-wordlist.txt"],
        use_sudo=use_sudo,
        timeout=5,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"failed to create container wordlist: {proc.stderr or proc.stdout}")
    return path


def run_one_functional(
    container: str,
    use_sudo: bool,
    tool: str,
    target: str,
    arguments: dict,
    timeout: int = 90,
) -> FunctionalCheck:
    try:
        result = call_mcp_tool(container, use_sudo, tool, arguments, timeout=timeout)
        text = mcp_text(result)
        ok = not bool(result.get("isError"))
        if ok and text.lower().startswith("error"):
            ok = False
        detail = next((line.strip() for line in text.splitlines() if line.strip()), "")
        return FunctionalCheck(tool, ok, target, detail[:140])
    except subprocess.TimeoutExpired:
        return FunctionalCheck(tool, False, target, "timed out")
    except Exception as exc:
        return FunctionalCheck(tool, False, target, str(exc))


def run_functional_checks(
    container: str,
    use_sudo: bool,
    target_ip: str | None,
    progress_enabled: bool,
) -> list[FunctionalCheck]:
    bind_ip = validate_ipv4(target_ip) if target_ip else default_target_ip()
    emit_progress(progress_enabled, f"functional checks will use IP target {bind_ip}")
    emit_progress(progress_enabled, "writing temporary wordlist inside container")
    wordlist = write_container_wordlist(container, use_sudo)

    with tempfile.TemporaryDirectory(prefix="kail-mcp-check-") as tmp:
        root = Path(tmp)
        (root / "index.html").write_text(
            "kail mcp smoke check\nadmin portal marker\n",
            encoding="utf-8",
        )
        (root / "admin").mkdir()
        (root / "admin" / "index.html").write_text("admin smoke\n", encoding="utf-8")

        handler = functools.partial(QuietHandler, directory=str(root))
        try:
            server = http.server.ThreadingHTTPServer((bind_ip, 0), handler)
        except OSError as exc:
            raise RuntimeError(f"cannot bind temporary HTTP server to {bind_ip}: {exc}") from exc

        port = int(server.server_address[1])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://{bind_ip}:{port}"
        emit_progress(progress_enabled, f"temporary HTTP target started at {base_url}")

        try:
            # Quick local TCP probe before involving MCP.
            with socket.create_connection((bind_ip, port), timeout=3):
                pass

            tests: list[tuple[str, dict, int]] = [
                (
                    "nmap_scan",
                    {"target": bind_ip, "scan_type": "quick", "ports": str(port), "timing": "T4"},
                    90,
                ),
                ("whatweb_scan", {"target_url": base_url}, 60),
                (
                    "gobuster_dir",
                    {"target_url": base_url, "wordlist": wordlist, "threads": 1, "status_codes": "200,301,302"},
                    90,
                ),
                (
                    "feroxbuster_scan",
                    {
                        "target_url": base_url,
                        "wordlist": wordlist,
                        "threads": 1,
                        "depth": 1,
                        "filter_codes": "404",
                        "extra_args": "--silent --time-limit 20s",
                    },
                    90,
                ),
                (
                    "dirsearch_scan",
                    {
                        "target_url": base_url,
                        "wordlist": wordlist,
                        "threads": 1,
                        "exclude_status": "404",
                        "extra_args": "--max-time 20 --quiet-mode",
                    },
                    90,
                ),
                (
                    "ffuf_fuzz",
                    {"url": f"{base_url}/FUZZ", "wordlist": wordlist, "threads": 1, "filter_codes": "404"},
                    90,
                ),
                (
                    "wfuzz_scan",
                    {"target_url": f"{base_url}/FUZZ", "wordlist": wordlist, "hide_codes": "404"},
                    90,
                ),
                ("dirb_scan", {"target_url": base_url, "wordlist": wordlist}, 90),
                (
                    "pd_httpx_probe",
                    {
                        "target": base_url,
                        "title": True,
                        "tech_detect": False,
                        "status_code": True,
                        "extra_args": "-duc",
                    },
                    90,
                ),
                (
                    "katana_crawl",
                    {"target_url": base_url, "depth": 1, "js_crawl": False, "extra_args": "-duc"},
                    90,
                ),
                (
                    "naabu_scan",
                    {"target": bind_ip, "ports": str(port), "rate": 100, "extra_args": "-duc"},
                    90,
                ),
                ("cewl_gen", {"target_url": base_url, "depth": 1, "min_word_length": 4}, 90),
                ("netcat_connect", {"target": bind_ip, "port": port, "extra_args": "-w 2"}, 45),
            ]

            checks: list[FunctionalCheck] = []
            total = len(tests)
            for index, (tool, arguments, timeout) in enumerate(tests, start=1):
                emit_progress(
                    progress_enabled,
                    f"[functional {index}/{total}] {tool}: calling MCP against {base_url}",
                )
                check = run_one_functional(container, use_sudo, tool, base_url, arguments, timeout)
                checks.append(check)
                emit_progress(
                    progress_enabled,
                    f"[functional {index}/{total}] {tool}: {'OK' if check.ok else 'FAIL'}",
                )
            return checks
        finally:
            emit_progress(progress_enabled, "stopping temporary HTTP target")
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def status(check: ToolCheck) -> str:
    if check.exposed and check.exists and check.version_ok is not False:
        return "OK"
    if check.exposed and check.exists and check.version_ok is False:
        return "WARN"
    return "FAIL"


def print_table(checks: list[ToolCheck]) -> None:
    headers = ("status", "tool", "requirement", "exposed", "starts", "version/help")
    rows = []
    for check in checks:
        starts = "n/a" if check.version_ok is None else ("yes" if check.version_ok else "no")
        rows.append(
            (
                status(check),
                check.name,
                check.requirement,
                "yes" if check.exposed else "no",
                starts,
                check.version_line[:90],
            )
        )

    widths = [
        max(len(str(row[i])) for row in [headers, *rows])
        for i in range(len(headers))
    ]
    print("  ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print("  ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))))


def print_functional_table(checks: list[FunctionalCheck]) -> None:
    if not checks:
        return

    headers = ("status", "tool", "target", "detail")
    rows = [
        ("OK" if check.ok else "FAIL", check.tool, check.target, check.detail)
        for check in checks
    ]
    widths = [
        max(len(str(row[i])) for row in [headers, *rows])
        for i in range(len(headers))
    ]
    print("  ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print("  ".join(str(row[i]).ljust(widths[i]) for i in range(len(row))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--container", default="kail-mcp", help="Container name to check.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    parser.add_argument("--quiet", action="store_true", help="Do not print progress to stderr.")
    parser.add_argument(
        "--functional",
        action="store_true",
        help="Run IP-only MCP calls against a temporary HTTP server.",
    )
    parser.add_argument(
        "--target-ip",
        type=validate_ipv4,
        help="IPv4 address to bind and access in --functional mode. Defaults to docker0/global IP.",
    )
    args = parser.parse_args()

    progress_enabled = not args.quiet
    use_sudo = detect_sudo(progress_enabled)
    checks = collect_checks(args.container, use_sudo, progress_enabled)
    functional_checks: list[FunctionalCheck] = []
    if args.functional:
        functional_checks = run_functional_checks(
            args.container,
            use_sudo,
            args.target_ip,
            progress_enabled,
        )

    summary = {
        "total": len(checks),
        "ok": sum(status(check) == "OK" for check in checks),
        "warn": sum(status(check) == "WARN" for check in checks),
        "fail": sum(status(check) == "FAIL" for check in checks),
    }
    functional_summary = {
        "total": len(functional_checks),
        "ok": sum(check.ok for check in functional_checks),
        "fail": sum(not check.ok for check in functional_checks),
    }

    if args.json:
        print(
            json.dumps(
                {
                    "summary": summary,
                    "functional_summary": functional_summary,
                    "checks": [check.__dict__ for check in checks],
                    "functional_checks": [check.__dict__ for check in functional_checks],
                },
                indent=2,
            )
        )
    else:
        print_table(checks)
        print()
        print(
            f"Summary: {summary['ok']}/{summary['total']} OK, "
            f"{summary['warn']} warnings, {summary['fail']} failures"
        )
        if functional_checks:
            print()
            print_functional_table(functional_checks)
            print()
            print(
                f"Functional summary: {functional_summary['ok']}/{functional_summary['total']} OK, "
                f"{functional_summary['fail']} failures"
            )

    return 1 if summary["fail"] or functional_summary["fail"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as exc:
        print(f"Timed out running: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(124)
