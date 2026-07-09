"""Per-operation file logging.

Each CLI invocation creates a timestamped log file under ``logs/`` so that
FK discovery, topo-sort order, and per-table seed results are captured even
when the console output is terse.

Log files are auto-created and gitignored.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_file_log(operation: str, engine: str, database: str) -> logging.Logger:
    """Create a timestamped log file and return a logger that writes to it.

    The file is named ``logs/{operation}_{engine}_{database}_{timestamp}.log``.
    """
    LOG_DIR.mkdir(exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{operation}_{engine}_{database}_{ts}.log"
    filepath = LOG_DIR / filename

    logger = logging.getLogger(f"synth_data.{operation}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(fh)

    logger.info("Log file: %s", filepath)
    return logger
