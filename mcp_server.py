#!/usr/bin/env python3
"""兼容入口。

真正实现已拆分到 `mcp_server/` 包；保留该文件是为了继续支持
Docker、脚本和旧文档中的 `python3 mcp_server.py` 启动方式。
"""

from mcp_server.cli import main


if __name__ == "__main__":
    main()
