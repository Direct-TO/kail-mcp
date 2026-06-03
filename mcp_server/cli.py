"""命令行启动入口。

保持 `python3 mcp_server.py` 的行为，同时也支持 `python3 -m mcp_server`。
"""

import asyncio
import signal
import sys

from .protocol import MCPServer


def main() -> None:
    """Start the MCP server."""
    print(
        "Red Team MCP Server v2.0 – For AUTHORIZED penetration testing only.\n"
        "Ensure you have written permission before testing any target.\n"
        "\n"
        "Improvements in v2.0:\n"
        "  - Test build with MCP-side security boundary restrictions disabled\n"
        "  - Structured output parsers (nmap, nikto, gobuster, hydra, whatweb)\n"
        "  - Binary availability check (tools remain exposed)\n"
        "  - SQLite scan history database\n"
        "  - auto_recon workflow tool\n"
        "  - generate_report tool\n"
        "  - Added 30+ penetration testing tools (Metasploit, BetterCAP, Impacket, etc.)\n",
        file=sys.stderr,
    )

    server = MCPServer()

    if sys.platform != "win32":
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, loop.stop)
        try:
            loop.run_until_complete(server.run())
        finally:
            loop.close()
    else:
        asyncio.run(server.run())
