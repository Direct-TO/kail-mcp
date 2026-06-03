"""审计日志。

每次 MCP tool 调用都会写入 append-only 日志，便于测试阶段回看
工具参数和返回摘要。
"""

import json
from datetime import datetime, timezone


class AuditLogger:
    """Append-only audit trail for every tool invocation."""

    def __init__(self, path: str = "audit.log") -> None:
        self._path = path

    def log(self, tool: str, arguments: dict, result_summary: str, success: bool) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "arguments": arguments,
            "success": success,
            "result_summary": result_summary[:500],
        }
        try:
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except OSError:
            pass
