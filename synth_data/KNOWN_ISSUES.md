# synth-data Known Issues & Concerns

## Referential integrity

### Individual `seed` command breaks FKs

Running `just seed-td DB test_orders 5` generates random `customer_id` values
that won't match any real `customer_id` in `test_customers`. The CLI now
warns when this happens, but the user must still choose to use `seed-test`.

Always use `seed-test` for tables with FK relationships:
```bash
just seed-test-td DB_DEMO_FOR_SYNTHETIC
```

### Seed order matters

The `SEED_ORDER` list in `lib/test_schema.py` must have parents before children.
If you add new tables with FKs, you must update this list or
`seed_with_relations()` will fail to find parent values.

---

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
