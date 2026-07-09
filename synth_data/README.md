# synth-data

Synthetic data generator for **Teradata** and **BigQuery**. Generates fake data with automatic referential integrity across foreign key relationships.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url> && cd synth_data
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

You can now run the `synth` command directly:

```bash
synth --help
```

If you prefer not to activate the venv, prefix commands with `uv run`:

```bash
uv run synth --help
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

The `.env` file is loaded automatically. **Never commit `.env`** — it is gitignored.

## Usage

### Analyse

```bash
# List all databases
synth --engine teradata analyse

# List tables in a database
synth --engine teradata analyse MY_DB

# List all tables across all databases
synth --engine teradata analyse all
```

### Seed

```bash
# Seed a single table with 100 rows (default)
synth --engine teradata seed MY_DB my_table --rows 100

# Seed ALL tables in a database (FK-aware: parents seeded first)
synth --engine teradata seed MY_DB --rows 100

# Seed the same table across ALL databases
synth --engine teradata seed all my_table --rows 100

# Seed ALL tables in ALL databases
synth --engine teradata seed all --rows 100

# Save a report to file
synth --engine teradata seed MY_DB --rows 100 --output report.txt
```

### Read

```bash
synth --engine teradata read MY_DB my_table --limit 20
```

### Test schema management

```bash
# Create the full set of test tables (covers 40+ column types)
synth --engine teradata create-schema MY_DB

# Drop all test tables
synth --engine teradata drop-schema MY_DB

# Seed with referential integrity (parents first, FKs resolved)
synth --engine teradata seed-test MY_DB

# Create/drop/seed across ALL databases
synth --engine teradata create-schema all
synth --engine teradata seed-test all
synth --engine teradata drop-schema all
```

### Verify referential integrity

```bash
# Check that all FK values in child tables exist in parent tables
synth --engine teradata verify MY_DB
synth --engine teradata verify all
```

### Purge data

```bash
# Delete all rows from every table (keeps schema)
synth --engine teradata purge-data MY_DB
synth --engine teradata purge-data all
```

### Typical reset workflow

```bash
synth --engine teradata purge-data MY_DB
synth --engine teradata create-schema MY_DB
synth --engine teradata seed-test MY_DB
synth --engine teradata verify MY_DB
```

## Development

```bash
just lint          # ruff check
just format        # ruff format
just typecheck     # pyright
just test          # pytest
just check         # lint + typecheck + test
just words         # line count stats
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
