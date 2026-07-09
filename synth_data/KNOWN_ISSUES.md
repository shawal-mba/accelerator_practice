# synth-data Known Issues & Concerns

## Engine-specific limitations

### BigQuery-only tables

These tables exist in BigQuery but not Teradata:
- `test_types_repeated` (REPEATED/array columns)
- `test_types_struct` (RECORD/struct columns)
- `test_types_geography` (GEOGRAPHY type)

When seeding on Teradata, these show "no columns found" and are skipped.

### Teradata-only types

These Teradata types have no BigQuery equivalent:
- `INTERVAL` types (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
- `PERIOD` types (DATE, TIMESTAMP)
- `CLOB`, `BLOB`
- `JSON` (Teradata JSON vs BigQuery JSON)
