"""Centralised application settings.

All configuration flows through this module. Values are resolved from
environment variables (or a .env file) with sensible defaults.

Usage::

    from src.infrastructure.settings import settings
    print(settings.td_host)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent

load_dotenv(_PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    # ── Teradata ──────────────────────────────────────────────
    td_host: str = field(default_factory=lambda: os.environ.get("TERADATA_HOST", ""))
    td_user: str = field(default_factory=lambda: os.environ.get("TERADATA_USER", ""))
    td_password: str = field(default_factory=lambda: os.environ.get("TERADATA_PASSWORD", ""))

    # ── BigQuery ──────────────────────────────────────────────
    bq_project: str = field(default_factory=lambda: os.environ.get("GOOGLE_CLOUD_PROJECT", ""))

    # ── Defaults ──────────────────────────────────────────────
    default_database: str = field(default_factory=lambda: os.environ.get("DATABASE", ""))
    default_schema_id: str = field(default_factory=lambda: os.environ.get("SCHEMA_ID", "1"))
    default_rows: int = field(default_factory=lambda: int(os.environ.get("DEFAULT_ROWS", "100")))

    # ── Generator ─────────────────────────────────────────────
    generator_locale: str = field(
        default_factory=lambda: os.environ.get("GENERATOR_LOCALE", "zu_ZA")
    )

    # ── Logging ───────────────────────────────────────────────
    log_dir: Path = field(
        default_factory=lambda: Path(os.environ.get("LOG_DIR", str(_PROJECT_ROOT / "logs")))
    )

    # ── Validation helpers ────────────────────────────────────
    def require_td_credentials(self) -> None:
        if not all([self.td_host, self.td_user, self.td_password]):
            raise ValueError(
                "Teradata credentials missing. "
                "Set TERADATA_HOST, TERADATA_USER, TERADATA_PASSWORD in .env or environment."
            )

    def require_bq_project(self) -> None:
        if not self.bq_project:
            raise ValueError(
                "BigQuery project missing. Set GOOGLE_CLOUD_PROJECT in .env or environment."
            )


settings = Settings()
