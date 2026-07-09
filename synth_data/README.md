# synth-data

Synthetic data generator for **Teradata** and **BigQuery**. Generates fake data with automatic referential integrity across foreign key relationships.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url> && cd synth_data
uv sync
```

## Configuration

### BigQuery

Authenticate with gcloud:

```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=your-project-id
```

Or pass `--project` on every command.

### Teradata

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
# edit .env with your Teradata host, user, and password
```

The `.env` file is loaded automatically by the justfile. **Never commit `.env`** — it is gitignored.

## Usage

All commands go through `just`. Run `just` with no args to see the full list.

### Analyse

```bash
# List all datasets (BigQuery) or databases (Teradata)
just analyze-bq
just analyze-td

# List tables in a dataset/database
just analyze-bq my_dataset
just analyze-td MY_DB
```

### Seed

```bash
# Seed a single table with 100 rows (default)
just seed-bq my_dataset my_table 100
just seed-td MY_DB my_table 50

# Seed ALL tables in a dataset
just seed-bq my_dataset

# Save a report
just seed-td MY_DB my_table 100 --output report.txt
```

### Read

```bash
just read-bq my_dataset my_table 20
just read-td MY_DB my_table 10
```

### Test schema management

```bash
# Create the full set of test tables (covers 40+ column types)
just create-schema-bq my_dataset
just create-schema-td MY_DB

# Drop all test tables
just drop-schema-bq my_dataset
just drop-schema-td MY_DB

# Seed with referential integrity (parents first, FKs resolved)
just seed-test-bq my_dataset
just seed-test-td MY_DB
```

### Quality checks

```bash
just lint          # ruff check
just format        # ruff format
just typecheck     # pyright
just test          # pytest
just check         # lint + typecheck + test
just all           # format + check
```

## Architecture

```
src/
  main.py              CLI entry point (click)
  protocol.py          Database protocol (typing.Protocol)
  bigquery.py          BigQuery backend
  teradata.py          Teradata backend
  matching.py          Column-to-faker mapping + SQL identifier validation
  fk.py                Shared foreign-key resolution logic
  format.py            Rich console output helpers
  log.py               Per-operation file logging
  test_schema.py       Test table DDL definitions (BQ + TD)
tests/
  test_synth_data.py   Unit tests for matching, casting, and schema logic
```

Both `BigQueryDB` and `TeradataDB` implement the `Database` protocol, making it straightforward to add new backends.

## Known issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for documented limitations around referential integrity, type handling, and engine-specific quirks.
