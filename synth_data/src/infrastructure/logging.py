"""Per-operation file logging."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


def setup_file_log(operation: str, engine: str, database: str) -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filepath = LOG_DIR / f"{operation}_{engine}_{database}_{ts}.log"
    logger = logging.getLogger(f"synth_data.{operation}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(fh)
    logger.info("Log file: %s", filepath)
    return logger
