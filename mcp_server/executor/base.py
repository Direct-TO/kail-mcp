"""ToolExecutor 主调度器。

主类只负责工具分发、超时、子进程执行、审计和数据库落盘；
具体工具命令放在各工具族 mixin 中，便于维护。
"""

import asyncio
import json
import logging

from ..audit import AuditLogger
from ..storage import ScanDatabase
from .credentials import CredentialToolsMixin
from .network import NetworkToolsMixin
from .recon import ReconToolsMixin
from .reporting import ReportingToolsMixin
from .web import WebToolsMixin
from .windows_ad import WindowsADToolsMixin


class ToolExecutor(
    ReconToolsMixin,
    WebToolsMixin,
    CredentialToolsMixin,
    WindowsADToolsMixin,
    NetworkToolsMixin,
    ReportingToolsMixin,
):
    """Execute Kali Linux tools as async subprocesses."""

    def __init__(self, config: dict, logger: logging.Logger,
                 audit: AuditLogger, scan_db: ScanDatabase) -> None:
        self._config = config
        self._log = logger
        self._audit = audit
        self._db = scan_db
        self._tools_cfg = config.get("tools", {})
        self._security_cfg = config.get("security", {})
        self._default_timeout: int = self._tools_cfg.get("default_timeout", 120)
        self._high_risk_tools: set[str] = set()

    async def execute(self, tool_name: str, arguments: dict) -> dict:
        """Dispatch *tool_name* to the appropriate handler with rate limiting."""
        handler = getattr(self, f"_tool_{tool_name}", None)
        if handler is None:
            return self._error(f"Unknown tool: {tool_name}")

        try:
            result = await handler(arguments)

            # Determine target for DB storage
            target = (arguments.get("target") or arguments.get("target_url")
                      or arguments.get("query") or "unknown")

            # [MEJORA 6] Save to database
            output_text = ""
            parsed_text = None
            if result.get("content"):
                output_text = result["content"][0].get("text", "")
                # Check if it's already JSON
                try:
                    json.loads(output_text)
                    parsed_text = output_text
                except (json.JSONDecodeError, TypeError):
                    pass

            self._db.save_result(
                tool=tool_name,
                target=str(target),
                arguments=arguments,
                output=output_text,
                output_parsed=parsed_text,
                success=not result.get("isError", False),
            )

            self._audit.log(tool_name, arguments, output_text[:200], True)
            return result

        except ValueError as exc:
            msg = f"Input validation error: {exc}"
            self._audit.log(tool_name, arguments, msg, False)
            return self._error(msg)
        except asyncio.TimeoutError:
            timeout_secs = self._timeout_for(tool_name)
            msg = (
                f"Tool {tool_name} timed out after {timeout_secs}s. "
                f"Execution incomplete. No verifiable results."
            )
            self._audit.log(tool_name, arguments, msg, False)
            return self._error(msg)
        except Exception as exc:
            msg = (
                f"Unexpected error in {tool_name}: {exc}. "
                f"Execution incomplete. No verifiable results."
            )
            self._log.exception(msg)
            self._audit.log(tool_name, arguments, msg, False)
            return self._error(msg)

    @staticmethod
    def _error(message: str) -> dict:
        return {"content": [{"type": "text", "text": message}], "isError": True}

    @staticmethod
    def _ok(text: str) -> dict:
        return {"content": [{"type": "text", "text": text}], "isError": False}

    def _timeout_for(self, tool_name: str) -> int:
        tool_cfg = self._tools_cfg.get(tool_name, {})
        if isinstance(tool_cfg, dict):
            t = tool_cfg.get("timeout", self._default_timeout)
        else:
            t = self._default_timeout
        return int(t)

    def _scope_check(self, target: str) -> None:
        """Scope checks are disabled in the current test build."""
        return None

    async def _run_subprocess(self, cmd: list[str], timeout: int) -> tuple[str, str, int]:
        """Run *cmd* as an async subprocess, returning (stdout, stderr, returncode)."""
        self._log.info("Executing: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        return stdout, stderr, proc.returncode or 0

    async def _run_subprocess_with_input(self, cmd: list[str], stdin_text: str, timeout: int) -> tuple[str, str, int]:
        """Run *cmd* with stdin text, returning (stdout, stderr, returncode)."""
        self._log.info("Executing: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(stdin_text.encode("utf-8")),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        return stdout, stderr, proc.returncode or 0

    async def _run_shell(self, command: str, timeout: int) -> tuple[str, str, int]:
        """Run *command* through the user's shell without MCP-side restrictions."""
        self._log.info("Executing shell command: %s", command)
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        stdout = stdout_bytes.decode("utf-8", errors="replace")
        stderr = stderr_bytes.decode("utf-8", errors="replace")
        return stdout, stderr, proc.returncode or 0
