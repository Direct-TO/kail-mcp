"""扫描历史数据库。

SQLite 表结构保持与拆分前一致；这里只负责持久化，不参与工具执行逻辑。
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from .evidence import EvidenceVerdict


class ScanDatabase:
    """SQLite database to persist scan results across sessions."""

    def __init__(self, db_path: str = "scan_results.db") -> None:
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool TEXT NOT NULL,
                target TEXT NOT NULL,
                arguments TEXT NOT NULL,
                output TEXT NOT NULL,
                output_parsed TEXT,
                success INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS evidence_verdicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                tool TEXT NOT NULL,
                has_findings INTEGER NOT NULL DEFAULT 0,
                evidence_type TEXT NOT NULL DEFAULT 'none',
                finding_count INTEGER NOT NULL DEFAULT 0,
                finding_summary TEXT,
                execution_status TEXT NOT NULL DEFAULT 'success',
                no_findings INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scan_results(id)
            )
        """)
        self._conn.commit()

    def save_result(self, tool: str, target: str, arguments: dict,
                    output: str, output_parsed: Optional[str] = None,
                    success: bool = True) -> int:
        """Save a scan result and return its row id."""
        cursor = self._conn.execute(
            "INSERT INTO scan_results (tool, target, arguments, output, output_parsed, success, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (tool, target, json.dumps(arguments), output[:50000], output_parsed,
             1 if success else 0, datetime.now(timezone.utc).isoformat())
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_history(self, tool: Optional[str] = None, target: Optional[str] = None,
                    limit: int = 20) -> list[dict]:
        """Retrieve scan history, optionally filtered by tool and/or target."""
        query = "SELECT id, tool, target, arguments, output_parsed, success, timestamp FROM scan_results WHERE 1=1"
        params: list = []
        if tool:
            query += " AND tool = ?"
            params.append(tool)
        if target:
            query += " AND target LIKE ?"
            params.append(f"%{target}%")
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_all_targets(self) -> list[str]:
        """Return all unique targets from scan history."""
        rows = self._conn.execute(
            "SELECT DISTINCT target FROM scan_results ORDER BY target"
        ).fetchall()
        return [row["target"] for row in rows]

    def get_results_for_report(self, target: Optional[str] = None) -> list[dict]:
        """Get all results for report generation."""
        query = "SELECT id, tool, target, output, output_parsed, success, timestamp FROM scan_results WHERE 1=1"
        params: list = []
        if target:
            query += " AND target LIKE ?"
            params.append(f"%{target}%")
        query += " ORDER BY target, tool, timestamp"
        rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def save_verdict(self, tool: str, verdict: EvidenceVerdict,
                     scan_id: Optional[int] = None) -> int:
        """Persist an evidence verdict and return its row id."""
        cursor = self._conn.execute(
            "INSERT INTO evidence_verdicts "
            "(scan_id, tool, has_findings, evidence_type, finding_count, "
            " finding_summary, execution_status, no_findings, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                scan_id, tool,
                1 if verdict.has_findings else 0,
                verdict.evidence_type,
                verdict.finding_count,
                json.dumps(verdict.finding_summary),
                verdict.execution_status,
                1 if verdict.no_findings else 0,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_verdicts_for_report(self, target: Optional[str] = None) -> dict[int, dict]:
        """Return verdicts keyed by scan_id for report generation."""
        query = (
            "SELECT ev.scan_id, ev.has_findings, ev.evidence_type, "
            "ev.finding_count, ev.finding_summary, ev.execution_status, ev.no_findings "
            "FROM evidence_verdicts ev"
        )
        if target:
            query += (
                " JOIN scan_results sr ON ev.scan_id = sr.id"
                " WHERE sr.target LIKE ?"
            )
            rows = self._conn.execute(query, (f"%{target}%",)).fetchall()
        else:
            rows = self._conn.execute(query).fetchall()
        result: dict[int, dict] = {}
        for row in rows:
            r = dict(row)
            sid = r.pop("scan_id", None)
            if sid is not None:
                result[sid] = r
        return result
