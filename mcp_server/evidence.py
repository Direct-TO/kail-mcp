"""Evidence Gate：工具结果的可验证事实层。

该模块只根据结构化输出、确认字符串或产物文件判断“有无证据”，
用于约束 LLM 只能总结已验证事实。
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class EvidenceVerdict:
    """Machine-readable evidence assessment attached to every tool result."""

    tool: str
    has_findings: bool
    evidence_type: str  # "parsed_data" | "confirmation_string" | "artifact_file" | "none"
    finding_count: int
    finding_summary: list[str] = field(default_factory=list)
    raw_truncated: bool = False
    execution_status: str = "success"  # "success" | "timeout" | "error" | "empty"
    no_findings: bool = True

    _LANGUAGE_RULE = (
        "LANGUAGE RULE: Respond in the same language the user is writing in. "
        "If the user writes in Spanish, respond in Spanish. "
        "If in English, respond in English. "
        "Technical terms (tool names, CVEs, commands) stay in English."
    )

    def to_header(self) -> str:
        """Render as a structured block the LLM must treat as authoritative."""
        if self.no_findings:
            status_line = f"status: {self.execution_status}"
            if self.execution_status == "timeout":
                body = "Execution incomplete. No verifiable results."
            elif self.execution_status == "error":
                body = "Tool execution failed. No verifiable results."
            else:
                body = "No confirmed vulnerability. No verifiable evidence produced."
            return (
                f"[EVIDENCE GATE — {self.tool}]\n"
                f"{status_line}\n"
                f"NO_FINDINGS: true\n"
                f"{body}\n"
                f"{self._LANGUAGE_RULE}\n"
                f"[END EVIDENCE GATE]\n"
            )
        lines = [
            f"[EVIDENCE GATE — {self.tool}]",
            f"status: {self.execution_status}",
            f"has_findings: true",
            f"evidence_type: {self.evidence_type}",
            f"finding_count: {self.finding_count}",
            "verified_facts:",
        ]
        for s in self.finding_summary:
            lines.append(f"  - {s}")
        lines.append(
            "IMPORTANT: Only the facts listed above are confirmed. "
            "Do not infer additional vulnerabilities."
        )
        lines.append(self._LANGUAGE_RULE)
        lines.append("[END EVIDENCE GATE]")
        return "\n".join(lines) + "\n"

    def to_dict(self) -> dict:
        """Serialize for database storage."""
        return {
            "tool": self.tool,
            "has_findings": self.has_findings,
            "evidence_type": self.evidence_type,
            "finding_count": self.finding_count,
            "finding_summary": self.finding_summary,
            "execution_status": self.execution_status,
            "no_findings": self.no_findings,
        }


class EvidenceValidator:
    """
    Inspects raw tool results against strict evidence rules and produces a
    machine-readable EvidenceVerdict.  The verdict is prepended to every tool
    response so the LLM can only summarize verified structured facts.
    """

    # Regex patterns that constitute hard proof per tool
    CONFIRMATION_PATTERNS: dict[str, list[re.Pattern]] = {
        "sqlmap_scan": [
            re.compile(r"parameter ['\"].*?['\"] is (?:injectable|vulnerable)", re.I),
            re.compile(r"retrieved:\s+\S+", re.I),
            re.compile(r"dumped to", re.I),
            re.compile(r"Type:\s+\w+.*injection", re.I),
        ],
        "hashcat_crack": [
            re.compile(r"^[a-fA-F0-9\$\.\/]{10,}:.+", re.M),  # hash:plaintext
            re.compile(r"Recovered\.*:\s*(\d+)/", re.I),
        ],
        "john_crack": [
            re.compile(r"^(\S+)\s+\((.+?)\)\s*$", re.M),  # plaintext (username)
            re.compile(r"\d+ password hashes? cracked", re.I),
        ],
        "msf_console": [
            re.compile(r"Meterpreter session (\d+) opened", re.I),
            re.compile(r"Command shell session (\d+) opened", re.I),
            re.compile(r"session (\d+) opened", re.I),
        ],
        "crackmapexec": [
            re.compile(r"\[\+\]", re.I),  # CrackMapExec success marker
            re.compile(r"Pwn3d!", re.I),
        ],
        "responder_poison": [
            re.compile(r"\[HTTP\].*NTLMv\d", re.I),
            re.compile(r"Hash\s*:\s*\S+", re.I),
        ],
        "cve_lookup": [
            re.compile(r"CVE ID\s*:\s*(CVE-\d{4}-\d+)", re.I),
            re.compile(r"CVSSv[\d.]+\s*:\s*[\d.]+\s*\(\w+\)", re.I),
            re.compile(r"Status\s*:\s*\w+", re.I),
        ],
    }

    # Tools whose parsed "findings" are informational, not confirmed vulns
    _INFORMATIONAL_TOOLS: set[str] = {
        "nikto_scan", "whatweb_scan", "nmap_scan", "gobuster_dir",
        "wapiti_scan", "searchsploit",
    }

    def validate(
        self,
        tool_name: str,
        result: dict,
        artifact_paths: Optional[list[str]] = None,
    ) -> EvidenceVerdict:
        """Inspect a tool result dict and return a verdict."""

        # ── 1. Handle error / timeout ─────────────────────────────────────
        if result.get("isError"):
            text = result["content"][0].get("text", "") if result.get("content") else ""
            if "timed out" in text.lower():
                return EvidenceVerdict(
                    tool=tool_name, has_findings=False, evidence_type="none",
                    finding_count=0, execution_status="timeout", no_findings=True,
                )
            return EvidenceVerdict(
                tool=tool_name, has_findings=False, evidence_type="none",
                finding_count=0, execution_status="error", no_findings=True,
            )

        output_text = (
            result["content"][0].get("text", "") if result.get("content") else ""
        )

        # ── 2. Empty output ───────────────────────────────────────────────
        if not output_text.strip():
            return EvidenceVerdict(
                tool=tool_name, has_findings=False, evidence_type="none",
                finding_count=0, execution_status="empty", no_findings=True,
            )

        truncated = len(output_text) > 40_000

        # ── 3. Artifact file check ────────────────────────────────────────
        if artifact_paths:
            valid_artifacts = []
            for ap in artifact_paths:
                ok, size = self._check_artifact(ap)
                if ok:
                    valid_artifacts.append(f"artifact:{ap} ({size} bytes)")
            if valid_artifacts:
                return EvidenceVerdict(
                    tool=tool_name, has_findings=True,
                    evidence_type="artifact_file",
                    finding_count=len(valid_artifacts),
                    finding_summary=valid_artifacts,
                    raw_truncated=truncated,
                    execution_status="success", no_findings=False,
                )

        # ── 4. Structured JSON parsing ────────────────────────────────────
        parsed = self._try_parse_json(output_text)
        if parsed:
            count, summaries = self._extract_from_parsed(tool_name, parsed)
            if count > 0:
                return EvidenceVerdict(
                    tool=tool_name, has_findings=True,
                    evidence_type="parsed_data",
                    finding_count=count,
                    finding_summary=summaries,
                    raw_truncated=truncated,
                    execution_status="success", no_findings=False,
                )

        # ── 5. Confirmation string matching ───────────────────────────────
        patterns = self.CONFIRMATION_PATTERNS.get(tool_name, [])
        matches: list[str] = []
        for pat in patterns:
            for m in pat.finditer(output_text):
                matches.append(m.group(0).strip())
        if matches:
            # Deduplicate while preserving order
            seen: set[str] = set()
            unique: list[str] = []
            for m in matches:
                if m not in seen:
                    seen.add(m)
                    unique.append(m)
            return EvidenceVerdict(
                tool=tool_name, has_findings=True,
                evidence_type="confirmation_string",
                finding_count=len(unique),
                finding_summary=unique[:20],
                raw_truncated=truncated,
                execution_status="success", no_findings=False,
            )

        # ── 6. No evidence gate passed ────────────────────────────────────
        return EvidenceVerdict(
            tool=tool_name, has_findings=False, evidence_type="none",
            finding_count=0, raw_truncated=truncated,
            execution_status="success", no_findings=True,
        )

    # -- internal helpers ---------------------------------------------------

    @staticmethod
    def _try_parse_json(text: str) -> Optional[dict]:
        """Attempt to parse text as JSON; return None on failure."""
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    @staticmethod
    def _check_artifact(path: str) -> tuple[bool, int]:
        """Return (exists_and_nonempty, size_bytes)."""
        try:
            p = Path(path)
            if p.exists() and p.stat().st_size > 0:
                return True, p.stat().st_size
        except OSError:
            pass
        return False, 0

    def _extract_from_parsed(
        self, tool: str, data: dict
    ) -> tuple[int, list[str]]:
        """Return (count, summary_lines) from a parsed JSON result."""

        if tool == "nmap_scan":
            ports: list[str] = []
            for host in data.get("hosts", []):
                addr = ""
                addrs = host.get("addresses", [])
                if addrs:
                    addr = addrs[0].get("addr", "")
                for p in host.get("ports", []):
                    if p.get("state") == "open":
                        svc = p.get("service", "unknown")
                        ver = p.get("version", "")
                        label = f"{addr} {p['port']}/{p.get('protocol', 'tcp')} open {svc}"
                        if ver:
                            label += f" {ver}"
                        ports.append(label.strip())
            return len(ports), ports[:30]

        if tool == "gobuster_dir":
            paths = data.get("discovered_paths", [])
            return len(paths), [
                f"{p['path']} (HTTP {p['status']})" for p in paths[:20]
            ]

        if tool == "hydra_attack":
            creds = data.get("credentials_found", [])
            return len(creds), [
                f"{c['username']}:{c['password']}" for c in creds
            ]

        if tool == "nikto_scan":
            findings = data.get("findings", [])
            return len(findings), [
                f"[info] {f['finding'][:100]}" for f in findings[:20]
            ]

        if tool == "whatweb_scan":
            techs = data.get("technologies", [])
            return len(techs), [
                f"[tech] {t['technology']}" for t in techs[:20]
            ]

        if tool == "searchsploit":
            exploits = data.get("RESULTS_EXPLOIT", data.get("results", []))
            if isinstance(exploits, list):
                return len(exploits), [
                    f"[exploit] {e.get('Title', str(e))[:100]}" for e in exploits[:20]
                ]

        # Generic fallback: count items in the first list-valued key
        for key, val in data.items():
            if isinstance(val, list) and len(val) > 0:
                return len(val), [f"{key}: {len(val)} items found"]

        return 0, []
