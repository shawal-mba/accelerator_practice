# synth-data Known Issues & Concerns

## Critical: Referential Integrity

### 1. Individual `seed` command breaks FKs

When running `just seed-td DB test_orders 5`, the `customer_id` values are randomly
generated and **won't match** any real `customer_id` in `test_customers`. This creates
orphan rows that violate foreign key constraints.

**Example:**
```bash
# This will insert orders with random customer_ids that don't exist
just seed-td DB_DEMO_FOR_SYNTHETIC test_orders 5
```

**Mitigation:** Always use `seed-test` for tables with FK relationships:
```bash
just seed-test-td DB_DEMO_FOR_SYNTHETIC
```

### 2. No FK validation on insert

The code doesn't check if FK values actually exist in parent tables. Teradata will
reject inserts if FK constraints are defined, but the error handling just logs a
warning and continues.

**Impact:** Partial inserts may occur - some rows succeed, others fail silently.

### 3. Seed order matters

The `SEED_ORDER` list in `lib/test_schema.py` must have parents before children.
If you add new tables with FKs, you must update this list or `seed_with_relations()`
will fail to find parent values.

**Current order:**
1. `test_types_*` (no FKs)
2. `test_products` (parent)
3. `test_customers` (parent)
4. `test_orders` (FK → customers)
5. `test_order_items` (FK → orders, FK → products)

---

## Type Handling Issues

### 4. Timestamp format mismatch

Faker generates ISO strings with microseconds: `2024-01-15T10:30:00.123456`

Teradata `TIMESTAMP(0)` expects: `2024-01-15 10:30:00`

**Current fix:** Code strips microseconds and converts `T` to space. This is fragile
and may break with edge cases (timezone offsets, midnight rollover).

### 5. DATE type requires inline SQL

`datetime.date` objects from faker need explicit conversion to `DATE 'YYYY-MM-DD'`
syntax for Teradata, not parameterized queries. Added `DA` to `INLINE_TYPES`.

### 6. TIME type precision

Faker generates `time` objects with microsecond precision. Teradata `TIME(0)` expects
no fractional seconds. Code strips microseconds via `.replace(microsecond=0)`.

---

## Engine-Specific Limitations

### 7. BigQuery-only tables

These tables exist in BigQuery but not Teradata:
- `test_types_repeated` (REPEATED/array columns)
- `test_types_struct` (RECORD/struct columns)
- `test_types_geography` (GEOGRAPHY type)

When seeding on Teradata, these will show "no columns found" and be skipped.

### 8. Teradata-only types

These Teradata types have no BigQuery equivalent:
- `INTERVAL` types (YEAR, MONTH, DAY, HOUR, MINUTE, SECOND)
- `PERIOD` types (DATE, TIMESTAMP)
- `CLOB`, `BLOB`
- `JSON` (Teradata JSON vs BigQuery JSON)

### 9. Teradata CREATE DATABASE

The `create-schema` command for Teradata attempts to create the database:
```sql
CREATE DATABASE {db} AS PERMANENT = 1e8, SPOOL = 1e8
```

This may fail if:
- User doesn't have CREATE DATABASE privileges
- Database already exists (handled gracefully)
- Insufficient disk space

---

## Authentication

### 10. BigQuery requires active gcloud auth

Error: `Reauthentication is needed. Please run 'gcloud auth application-default login'`

**Fix:** Run `gcloud auth application-default login` before using BigQuery commands.

### 11. Teradata credentials from .env

The justfile uses `set dotenv-load` to load `TERADATA_HOST`, `TERADATA_USER`,
`TERADATA_PASSWORD` from `.env`. Ensure these are set before running commands.

---

## Recommendations

1. **Always use `seed-test`** for tables with FK relationships
2. **Drop and recreate schema** before re-seeding to avoid duplicate key errors:
   ```bash
   just drop-schema-td DB_DEMO_FOR_SYNTHETIC
   just create-schema-td DB_DEMO_FOR_SYNTHETIC
   just seed-test-td DB_DEMO_FOR_SYNTHETIC
   ```
3. **Check parent tables first** - ensure parent tables have data before seeding children
4. **Use `--output` flag** to save seed reports for debugging:
   ```bash
   just seed-td DB test_customers 100 --output seed_report.txt
   ```
