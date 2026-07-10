"""Tests for the CLI app."""

from __future__ import annotations

import os

import pytest
import typer
from typer.testing import CliRunner

from src.main import CliContext, _get_db, app

runner = CliRunner()


class TestApp:
    def test_app_is_typer(self):
        assert isinstance(app, typer.Typer)

    def test_help_output(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        cmds = (
            "analyse",
            "analyse-all",
            "seed",
            "read",
            "create-schema",
            "drop-schema",
            "seed-test",
            "verify",
            "purge-data",
        )
        for cmd in cmds:
            assert cmd in result.stdout

    def test_invalid_engine(self):
        result = runner.invoke(app, ["--engine", "invalid", "analyse"])
        assert result.exit_code == 2
        assert "invalid" in result.stdout.lower() or "invalid" in result.stderr.lower()

    def test_no_engine_shows_error(self):
        result = runner.invoke(app, ["analyse"])
        assert result.exit_code == 2


class TestCliContext:
    def test_require_database_from_arg(self):
        c = CliContext(engine="bigquery", project="p", host=None, user=None, default_database=None)
        assert c.require_database("mydb") == "mydb"

    def test_require_database_from_default(self):
        ctx = CliContext(
            engine="bigquery", project="p", host=None, user=None, default_database="defdb"
        )
        assert ctx.require_database(None) == "defdb"

    def test_require_database_raises_when_missing(self):
        c = CliContext(engine="bigquery", project="p", host=None, user=None, default_database=None)
        with pytest.raises(typer.BadParameter, match="DATABASE"):
            c.require_database(None)

    def test_kind_key_bigquery(self):
        c = CliContext(engine="bigquery", project="p", host=None, user=None, default_database=None)
        assert c.kind_key() == "table_type"

    def test_kind_key_teradata(self):
        c = CliContext(engine="teradata", project=None, host="h", user="u", default_database=None)
        assert c.kind_key() == "table_kind"

    def test_table_type_bigquery(self):
        c = CliContext(engine="bigquery", project="p", host=None, user=None, default_database=None)
        assert c.table_type() == "TABLE"

    def test_table_type_teradata(self):
        c = CliContext(engine="teradata", project=None, host="h", user="u", default_database=None)
        assert c.table_type() == "T"


class TestGetDb:
    def test_bigquery_no_project_raises(self):
        if "GOOGLE_CLOUD_PROJECT" in os.environ:
            del os.environ["GOOGLE_CLOUD_PROJECT"]
        with pytest.raises(Exception, match="project"):
            _get_db("bigquery", project=None, host=None, user=None)

    def test_teradata_no_host_raises(self):
        for env_var in ("TERADATA_HOST", "TERADATA_USER", "TERADATA_PASSWORD"):
            os.environ.pop(env_var, None)
        with pytest.raises(Exception, match="host"):
            _get_db("teradata", project=None, host=None, user=None)

    def test_invalid_engine_raises(self):
        with pytest.raises(Exception, match="engine"):
            _get_db("invalid", project=None, host=None, user=None)
