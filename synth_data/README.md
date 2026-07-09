# synth-data

**Synthetic data generator for Teradata and BigQuery.**

Generates realistic fake data with automatic referential integrity — no schema knowledge required. The tool discovers columns, types, and foreign keys directly from the database metadata.

---

## Features

- **Zero-config seeding** — reads schema from the database, maps columns to faker generators automatically
- **Referential integrity** — discovers FK relationships and seeds parents before children
- **Cross-database** — seed a single table, all tables, or all databases in one command
- **18 BigQuery types** — STRING, BYTES, INTEGER, FLOAT, NUMERIC, BOOLEAN, DATE, DATETIME, TIMESTAMP, TIME, GEOGRAPHY, JSON, RECORD, STRUCT, and aliases
- **42 Teradata types** — CF, CV, CH, CHR, I, I1–I3, I8, I9, BT, SM, AT, D, F, N, BF, BO, DA, TS, OD, TD, TZ, all INTERVAL types, PERIOD types, CLOB, BLOB, JSON, XML, UUID
- **47 column-name patterns** — automatically matches names, emails, phones, addresses, companies, finance fields, dates, URLs, IPs, and more to appropriate faker generators
- **Rich CLI output** — panels, tables, and colour-coded results via Rich
- **Per-operation logging** — every command writes to a timestamped log file under `logs/`
- **Verify mode** — check referential integrity of seeded data

---

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url> && cd synth_data
uv sync
source .venv/bin/activate
```

Verify the installation:

```bash
synth --help
```

---

## Configuration

### BigQuery

```bash
gcloud auth application-default login
```

Set the project in `.env` or pass `--project`:

```bash
echo "GOOGLE_CLOUD_PROJECT=your-project-id" >> .env
```

### Teradata

```bash
cp .env.example .env
# fill in TERADATA_HOST, TERADATA_USER, TERADATA_PASSWORD
```

---

## Usage

### Analyse — discover what's in the database

```bash
synth --engine teradata analyse                     # list all databases
synth --engine teradata analyse MY_DB               # list tables in a database
synth --engine teradata analyse all                 # list tables in every database
synth --engine bigquery analyse MY_DATASET          # list tables in a dataset
```

### Seed — generate and insert fake data

```bash
# Single table
synth --engine teradata seed MY_DB my_table --rows 100

# All tables in a database (FK-aware: parents first)
synth --engine teradata seed MY_DB --rows 100

# All tables in ALL databases
synth --engine teradata seed all --rows 100

# Save a report
synth --engine teradata seed MY_DB --rows 100 --output report.txt
```

### Read — inspect data

```bash
synth --engine teradata read MY_DB my_table --limit 20
```

### Verify — check referential integrity

```bash
synth --engine teradata verify MY_DB
synth --engine bigquery verify MY_DATASET
```

### Purge — clear data (keeps schema)

```bash
synth --engine teradata purge-data MY_DB
synth --engine teradata purge-data all
```

### Test schema — create, seed, and drop predefined test tables

```bash
synth --engine teradata create-schema MY_DB
synth --engine teradata seed-test MY_DB
synth --engine teradata drop-schema MY_DB
```

### Typical workflow

```bash
synth --engine teradata purge-data MY_DB
synth --engine teradata create-schema MY_DB
synth --engine teradata seed MY_DB --rows 100
synth --engine teradata verify MY_DB
```

---

## Supported Data Types

### BigQuery (18 types)

| Type | Faker Generator |
|---|---|
| STRING | `word` |
| BYTES | `binary(10).hex()` |
| INTEGER / INT64 | `pyint(0–100k)` |
| FLOAT / FLOAT64 | `pyfloat(0–10k)` |
| NUMERIC / BIGNUMERIC | `pyfloat` as float |
| BOOLEAN / BOOL | `boolean` |
| DATE | `date_between(-5y, today)` |
| DATETIME / TIMESTAMP | `date_time_between(-5y)` |
| TIME | `time_object` |
| GEOGRAPHY | `POINT(longitude latitude)` |
| JSON | `json` |
| RECORD / STRUCT | `{}` |

### Teradata (42 types)

| Category | Types | Faker Generator |
|---|---|---|
| Character | CF, CV, CH, CHR | `word` |
| Integer | I, I1, I2, I3, I8, I9, BT, SM | `pyint` (range varies by type) |
| Decimal | D, F, N | `pyfloat(0–10k)` |
| Binary | BF, BO | `binary().hex()` |
| Date/Time | DA, TS, OD, TD, TZ, AT | `date_between`, `date_time_between`, `time_object` |
| Interval | YR, MO, DY, HR, MI, SC, DM, DV, FD, FS, FT, FY | `INTERVAL` literals |
| Period | PD, PS | 2-tuples of dates/timestamps |
| LOB | CO, LOB | `text(200)`, `binary(100).hex()` |
| Semi-structured | JN, XM, UT | `json`, `xml`, `uuid4` |

### Column-Name Auto-Matching (47 patterns)

| Category | Patterns | Faker Generator |
|---|---|---|
| Names | `first_name`, `last_name`, `full_name`, `customer_name`, `name` | `first_name`, `last_name`, `name` |
| Contact | `email`, `phone`, `mobile`, `cell` | `email`, `phone_number` (extensions stripped) |
| Location | `address`, `street`, `city`, `state`, `province`, `region`, `zip`, `postcode`, `country`, `country_code`, `latitude`, `longitude` | `street_address`, `city`, `province`, `postcode`, `country`, `latitude`, `longitude` |
| Company | `company`, `corp`, `organisation`, `job_title`, `title`, `role`, `position` | `company`, `job` |
| Finance | `price`, `amount`, `cost`, `salary`, `revenue`, `balance`, `credit_card`, `iban`, `currency_code` | `pyfloat`, `credit_card_number`, `iban`, `currency_code` |
| IDs | `ssn`, `uuid`, `isbn`, `mac_address` | `ssn`, `uuid4`, `isbn13`, `mac_address` |
| Dates | `created_at`, `updated_at`, `timestamp`, `datetime`, `date`, `dob`, `birth`, `year`, `month` | `date_time_between`, `date_between`, `year`, `month` |
| Internet | `url`, `domain`, `hostname`, `ip`, `slug`, `password`, `hash`, `sha`, `mime`, `file_ext`, `timezone` | `url`, `domain_name`, `ipv4`, `slug`, `password`, `sha256`, `mime_type`, `file_extension`, `timezone` |
| Text | `text`, `description`, `comment`, `note`, `summary` | `sentence` |
| Visual | `color`, `colour`, `hex_color`, `lorem` | `hex_color`, `paragraph` |

---

## Development

```bash
just lint          # ruff check
just format        # ruff format
just typecheck     # pyright
just test          # pytest
just check         # lint + typecheck + test
just all           # format + check
just words         # line count stats
```

---

## Architecture

```
src/
  main.py              CLI entry point (click + rich)
  protocol.py          Database protocol (typing.Protocol)
  bigquery.py          BigQuery backend
  teradata.py          Teradata backend
  matching.py          Column-to-faker mapping + SQL identifier validation
  fk.py                Shared foreign-key resolution + topological sort
  format.py            Rich console output (panels, tables)
  log.py               Per-operation file logging
  test_schema.py       Test table DDL definitions (BQ + TD)
tests/
  test_synth_data.py   Unit tests for matching, casting, and schema logic
```

Both `BigQueryDB` and `TeradataDB` implement the `Database` protocol, making it straightforward to add new backends.

---

## Known issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for documented limitations around engine-specific types and quirks.
