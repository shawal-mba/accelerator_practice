"""Infrastructure configuration — re-exports for convenience."""

from __future__ import annotations

from src.infrastructure.settings import settings

__all__ = ["ConfigError", "settings"]


class ConfigError(Exception): ...
