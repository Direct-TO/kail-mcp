"""MCP JSON-RPC 协议入口。

该模块处理 stdin/stdout 上的 JSON-RPC 消息，调用工具注册表、执行器、
Evidence Gate 和知识库注入。对外协议字段保持原样。
"""

import asyncio
import json
import logging
import sys
from typing import Any, Optional

from .audit import AuditLogger
from .binaries import check_available_binaries
from .config import load_config, setup_logging
from .evidence import EvidenceValidator
from .executor import ToolExecutor
from .knowledge import KnowledgeLoader
from .lmstudio import LMStudioClient
from .registry import ToolRegistry
from .storage import ScanDatabase


class MCPServer:
    """
    Model Context Protocol server that exposes Kali Linux tools over JSON-RPC
    via stdin/stdout for consumption by AI assistants (e.g. LM Studio).
    """

    PROTOCOL_VERSION = "2024-11-05"
    SERVER_NAME = "kail-mcp"
    SERVER_VERSION = "3.3"

    def __init__(self) -> None:
        self._config = load_config()
        self._logger = setup_logging(self._config)
        self._audit = AuditLogger(
            self._config.get("security", {}).get("audit_log", "audit.log")
        )

        # [MEJORA 4] Check which binaries are available
        self._available_binaries = check_available_binaries(self._logger)

        # [MEJORA 6] Initialize scan database
        db_path = self._config.get("server", {}).get("database", "scan_results.db")
        self._scan_db = ScanDatabase(db_path)

        self._registry = ToolRegistry(self._available_binaries)
        self._executor = ToolExecutor(self._config, self._logger, self._audit, self._scan_db)
        self._evidence_validator = EvidenceValidator()
        self._knowledge = KnowledgeLoader(self._logger)
        self._lm_client = LMStudioClient(self._config)

        srv = self._config.get("server", {})
        self.SERVER_NAME = srv.get("name", self.SERVER_NAME)
        self.SERVER_VERSION = srv.get("version", self.SERVER_VERSION)

        available_count = len(self._registry.tools)
        total_count = len(self._available_binaries)

        self._logger.info(
            "MCP Server initialized: %s v%s (%d/%d MCP tools exposed)",
            self.SERVER_NAME, self.SERVER_VERSION, available_count, total_count,
        )

    async def handle_message(self, message: dict) -> Optional[dict]:
        """Route an incoming JSON-RPC message and return the response."""
        method = message.get("method", "")
        msg_id = message.get("id")
        params = message.get("params", {})

        self._logger.debug("Received method=%s id=%s", method, msg_id)

        if msg_id is None:
            if method == "notifications/initialized":
                self._logger.info("Client initialized notification received.")
            return None

        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_tools_list()
            elif method == "tools/call":
                result = await self._handle_tools_call(params)
            else:
                return self._jsonrpc_error(msg_id, -32601, f"Method not found: {method}")
        except Exception as exc:
            self._logger.exception("Internal error handling %s", method)
            return self._jsonrpc_error(msg_id, -32603, f"Internal error: {exc}")

        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def _handle_initialize(self, params: dict) -> dict:
        self._logger.info(
            "Initialize request from client: %s",
            params.get("clientInfo", {}).get("name", "unknown"),
        )
        return {
            "protocolVersion": self.PROTOCOL_VERSION,
            "capabilities": {
                "tools": {"listChanged": False},
            },
            "serverInfo": {
                "name": self.SERVER_NAME,
                "version": self.SERVER_VERSION,
            },
        }

    def _handle_tools_list(self) -> dict:
        return {"tools": self._registry.tools}

    async def _handle_tools_call(self, params: dict) -> dict:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if not self._registry.get(tool_name):
            return {
                "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                "isError": True,
            }

        self._logger.info("Calling tool: %s with args: %s", tool_name, json.dumps(arguments)[:200])

        # Collect artifact paths from arguments (tools that write output files)
        artifact_paths: list[str] = []
        for key in ("output_file", "output_prefix", "output"):
            if key in arguments and isinstance(arguments[key], str):
                artifact_paths.append(arguments[key])

        result = await self._executor.execute(tool_name, arguments)

        # === EVIDENCE GATE ===
        verdict = self._evidence_validator.validate(
            tool_name, result, artifact_paths=artifact_paths or None,
        )

        # Persist verdict (linked to the most recent scan_id for this tool)
        try:
            last_scan = self._scan_db.get_history(tool=tool_name, limit=1)
            scan_id = last_scan[0]["id"] if last_scan else None
        except Exception:
            scan_id = None
        self._scan_db.save_verdict(tool_name, verdict, scan_id=scan_id)

        # Prepend the machine-readable evidence header
        if result.get("content"):
            result["content"].insert(0, {
                "type": "text",
                "text": verdict.to_header(),
            })

        # Only inject tactical knowledge if there are actual findings
        if not verdict.no_findings and not result.get("isError", False) and result.get("content"):
            # Raw tool output is the last content block
            tool_output = result["content"][-1].get("text", "")
            tactical_ctx = self._knowledge.get_context(tool_name, scan_results=tool_output)
            if tactical_ctx:
                # Insert knowledge AFTER the evidence gate, BEFORE raw output
                result["content"].insert(1, {
                    "type": "text",
                    "text": tactical_ctx,
                })

        return result

    @staticmethod
    def _jsonrpc_error(msg_id: Any, code: int, message: str) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": code, "message": message},
        }

    async def run(self) -> None:
        """Read JSON-RPC messages from stdin line by line, process, and write responses to stdout."""
        self._logger.info("MCP Server starting – reading from stdin...")

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin.buffer)

        w_transport, w_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout.buffer
        )
        writer = asyncio.StreamWriter(w_transport, w_protocol, reader, asyncio.get_event_loop())

        while True:
            try:
                line = await reader.readline()
                if not line:
                    self._logger.info("stdin closed – shutting down.")
                    break

                line_str = line.decode("utf-8", errors="replace").strip()
                if not line_str:
                    continue

                try:
                    message = json.loads(line_str)
                except json.JSONDecodeError as exc:
                    self._logger.warning("Invalid JSON: %s", exc)
                    err = self._jsonrpc_error(None, -32700, f"Parse error: {exc}")
                    writer.write((json.dumps(err) + "\n").encode("utf-8"))
                    await writer.drain()
                    continue

                response = await self.handle_message(message)
                if response is not None:
                    out = json.dumps(response) + "\n"
                    writer.write(out.encode("utf-8"))
                    await writer.drain()

            except asyncio.CancelledError:
                self._logger.info("Server cancelled.")
                break
            except Exception as exc:
                self._logger.exception("Unexpected error in main loop: %s", exc)
