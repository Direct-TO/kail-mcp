"""配置与日志初始化。

本模块集中处理 config.yaml、环境变量覆盖和日志对象，其他模块只消费
已经加载好的配置，避免到处读文件。
"""

import logging
import os
import sys
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = Path(os.environ.get("MCP_CONFIG_PATH", BASE_DIR / "config.yaml"))


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    """Load YAML configuration from *path*, returning defaults on failure."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        logging.warning("Config file %s not found, using defaults.", path)
        cfg = {}
    except yaml.YAMLError as exc:
        logging.warning("Invalid YAML in %s: %s – using defaults.", path, exc)
        cfg = {}

    # ── Environment variable overrides ────────────────────────────────────
    if os.environ.get("MCP_LOG_LEVEL"):
        cfg.setdefault("server", {})["log_level"] = os.environ["MCP_LOG_LEVEL"]
    if os.environ.get("MCP_DATABASE"):
        cfg.setdefault("server", {})["database"] = os.environ["MCP_DATABASE"]
    if os.environ.get("MCP_AUDIT_LOG"):
        cfg.setdefault("security", {})["audit_log"] = os.environ["MCP_AUDIT_LOG"]
    if os.environ.get("MCP_REPORT_DIR"):
        cfg.setdefault("server", {})["report_dir"] = os.environ["MCP_REPORT_DIR"]

    return cfg


def setup_logging(config: dict) -> logging.Logger:
    """Configure and return the application logger."""
    server_cfg = config.get("server", {})
    log_file = server_cfg.get("log_file", "mcp_server.log")
    log_level = getattr(logging, server_cfg.get("log_level", "INFO").upper(), logging.INFO)

    logger = logging.getLogger("mcp_server")
    logger.setLevel(log_level)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(log_level)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(log_level)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    return logger
