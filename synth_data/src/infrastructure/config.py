"""Database factory and environment configuration."""

from __future__ import annotations

import os

from dotenv import load_dotenv

from src.adapters.database.bigquery import BigQueryDB
from src.adapters.database.teradata import TeradataDB
from src.adapters.generator.faker import FakerAdapter
from src.domain.matching import set_generator
from src.domain.ports import Database


class ConfigError(Exception): ...


load_dotenv()

# Plug in the default Faker generator at import time.
# Swap this with your own DataGenerator implementation to use LLMs or other sources.
set_generator(FakerAdapter(locale="zu_ZA"))


def get_db(engine: str, project: str | None, host: str | None, user: str | None) -> Database:
    if engine == "bigquery":
        project = project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        if not project:
            raise ConfigError(
                "project is required for BigQuery. Pass --project or set GOOGLE_CLOUD_PROJECT."
            )
        return BigQueryDB(project=project)
    if engine == "teradata":
        host = host or os.environ.get("TERADATA_HOST", "")
        user = user or os.environ.get("TERADATA_USER", "")
        password = os.environ.get("TERADATA_PASSWORD", "")
        if not all([host, user, password]):
            raise ConfigError("host, user, and password are required for Teradata.")
        return TeradataDB(host=host, user=user, password=password)
    raise ConfigError(f"Unknown engine: {engine}")
