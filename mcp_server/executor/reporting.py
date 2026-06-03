"""扫描历史查询和报告生成工具实现。"""

import json
from datetime import datetime, timezone
from pathlib import Path


class ReportingToolsMixin:
    async def _tool_get_scan_history(self, args: dict) -> dict:
        tool = args.get("tool")
        target = args.get("target")
        limit = args.get("limit", 20)
        history = self._db.get_history(tool=tool, target=target, limit=limit)

        if not history:
            return self._ok("No scan history found for the given filters.")

        # Return summary without full output (too long)
        summary = []
        for entry in history:
            summary.append({
                "id": entry["id"],
                "tool": entry["tool"],
                "target": entry["target"],
                "success": bool(entry["success"]),
                "timestamp": entry["timestamp"],
                "has_parsed_output": entry.get("output_parsed") is not None,
            })
        return self._ok(json.dumps(summary, indent=2))

    async def _tool_generate_report(self, args: dict) -> dict:
        target_filter = args.get("target")
        results = self._db.get_results_for_report(target=target_filter)

        if not results:
            return self._ok("No scan results found to generate a report.")

        # Load evidence verdicts keyed by scan_id
        verdicts = self._db.get_verdicts_for_report(target=target_filter)

        # Build markdown report
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        confirmed_count = sum(1 for v in verdicts.values() if v.get("has_findings"))
        unconfirmed_count = len(results) - confirmed_count

        report_lines = [
            "# Red Team Scan Report",
            f"**Generated:** {now}",
            f"**Filter:** {target_filter or 'All targets'}",
            f"**Total scans:** {len(results)}",
            f"**Confirmed findings:** {confirmed_count}",
            f"**Unconfirmed / Informational:** {unconfirmed_count}",
            "",
            "> **Evidence Policy:** Only scans with machine-verified evidence "
            "are marked CONFIRMED. All other results are UNCONFIRMED / Informational.",
            "",
            "---",
            "",
        ]

        # Group by target
        by_target: dict[str, list[dict]] = {}
        for r in results:
            by_target.setdefault(r["target"], []).append(r)

        for target, scans in by_target.items():
            report_lines.append(f"## Target: `{target}`")
            report_lines.append("")

            for scan in scans:
                scan_id = scan["id"]
                v = verdicts.get(scan_id)
                if v and v.get("has_findings"):
                    evidence_label = "CONFIRMED"
                    evidence_type = v.get("evidence_type", "unknown")
                    finding_count = v.get("finding_count", 0)
                    badge = f"**[{evidence_label}]** (evidence: {evidence_type}, count: {finding_count})"
                elif v and v.get("execution_status") in ("timeout", "error"):
                    badge = "**[INCOMPLETE]** Execution did not finish — no verifiable results"
                else:
                    badge = "**[UNCONFIRMED / Informational]** No machine-verified evidence"

                report_lines.append(f"### {scan['tool']} (ID: {scan_id})")
                report_lines.append(f"- **Time:** {scan['timestamp']}")
                report_lines.append(f"- **Status:** {'OK' if scan['success'] else 'FAILED'}")
                report_lines.append(f"- **Evidence:** {badge}")

                # Show verified fact summary from verdict
                if v and v.get("has_findings"):
                    summary_raw = v.get("finding_summary", "[]")
                    try:
                        summary_list = json.loads(summary_raw) if isinstance(summary_raw, str) else summary_raw
                    except (json.JSONDecodeError, TypeError):
                        summary_list = []
                    if summary_list:
                        report_lines.append("- **Verified facts:**")
                        for fact in summary_list[:15]:
                            report_lines.append(f"  - {fact}")

                report_lines.append("")

                # Use parsed output if available, otherwise truncate raw
                if scan.get("output_parsed"):
                    try:
                        parsed = json.loads(scan["output_parsed"])
                        report_lines.append("```json")
                        report_lines.append(json.dumps(parsed, indent=2)[:3000])
                        report_lines.append("```")
                    except json.JSONDecodeError:
                        report_lines.append("```")
                        report_lines.append(scan["output"][:2000])
                        report_lines.append("```")
                else:
                    output = scan["output"][:2000]
                    if output:
                        report_lines.append("```")
                        report_lines.append(output)
                        report_lines.append("```")

                report_lines.append("")

        report_lines.append("---")
        report_lines.append(
            "*Report generated by Red Team MCP Server v2.0 — "
            "Evidence validation layer active*"
        )

        report_text = "\n".join(report_lines)

        # Save to file
        report_dir = Path(self._config.get("server", {}).get("report_dir", "reports"))
        report_dir.mkdir(parents=True, exist_ok=True)
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = report_dir / filename
        report_path.write_text(report_text, encoding="utf-8")

        return self._ok(
            f"Report saved to: {report_path}\n\n{report_text}"
        )
