"""
日志系统（基于 loguru）
"""

import sys
from pathlib import Path
from loguru import logger as _logger

from app.core.config import settings

log_dir = settings.ROOT_DIR / (settings.get("log.file", "logs/agent.log")).rsplit("/", 1)[0]
log_dir.mkdir(parents=True, exist_ok=True)

log_path = log_dir / "agent.log"

_logger.remove()
_logger.add(sys.stdout, level=getattr(settings, "LOG_LEVEL", "INFO"), format="<g>{time:HH:mm:ss}</g> | <lvl>{level:<5}</lvl> | {message}")
_logger.add(str(log_path), level="DEBUG", rotation="10 MB", retention=5, encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level:<5} | {message}")

logger = _logger
