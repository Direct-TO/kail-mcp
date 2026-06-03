"""kail-mcp 服务包。

该包把原来的单文件 MCP server 拆成多个职责清晰的模块，
对外启动方式和 MCP 工具接口保持不变。
"""

from .protocol import MCPServer

__all__ = ["MCPServer"]
