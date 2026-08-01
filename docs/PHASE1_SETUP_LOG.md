# Phase 1 Setup Log — Ingestion with dlt (Crypto Market Pipeline)

> Operational reference for Phase 1: commands, config templates, and fix history — not reasoning or lessons-learned (that lives in the working notes, not here). Mirrors the role `PHASE0_SETUP_LOG.md` plays for Phase 0. Meant to be committed to the actual repo at `docs/PHASE1_SETUP_LOG.md`, same as its Phase 0 counterpart — copy it over and commit when ready; this local copy doesn't sync automatically.
>
> Companion files: `Phase1_Step_By_Step_Guide.md` (narrative walkthrough), `Working_Notes.md` (decisions + session log), `PHASE0_SETUP_LOG.md` (environment/scaffold reference this builds on).

---

## 1. `coins_markets` resource — final config

`dlt/rest_api_pipeline.py`:

```python
import pendulum
import os
import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


@dlt.source
def coingecko_source(
    api_key=dlt.secrets.value,
    snapshot_date=None,
    simulate_new_field=False,
    simulate_type_drift=False,
):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.coingecko.com/api/v3/",
            "auth": {
                "type": "api_key",
                "name": "x-cg-demo-api-key",
                "api_key": api_key,
                "location": "header",
            },
        },
        "resources": [
            {
                "name": "coins_markets",
                "write_disposition": "merge",
                "primary_key": ["id", "snapshot_date"],
                "columns": {"roi": {"data_type": "json"}},
                "schema_contract": {
                    "tables": "evolve",
                    "columns": "evolve",
                    "data_type": "freeze",
                },
                "endpoint": {
                    "path": "coins/markets",
                    "params": {
                        "vs_currency": "usd",
                        "per_page": 250,
                        "page": 1,
                    },
                },
            }
        ],
    }

    if snapshot_date is None:
        snapshot_date = pendulum.today("UTC").to_date_string()

    def add_snapshot_date(row):
        row["snapshot_date"] = snapshot_date
        return row

    def add_test_field(row):
        row["test_field"] = "test_value"
        return row

    def corrupt_current_price(row):
        row["current_price"] = "not-a-number"
        return row

    for resource in rest_api_resources(config):
        if resource.name == "coins_markets":
            resource.add_map(add_snapshot_date)
            if simulate_new_field:
                resource.add_map(add_test_field)
            if simulate_type_drift:
                resource.add_map(corrupt_current_price)
        yield resource


def load_coingecko(
    snapshot_date: str | None = None,
    simulate_new_field: bool = False,
    simulate_type_drift: bool = False,
) -> None:
    duckdb_path = os.environ["CRYPTO_PIPELINE_DUCKDB_PATH_DEV"]
    os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)

    pipeline = dlt.pipeline(
        pipeline_name="crypto_market_pipeline",
        destination=dlt.destinations.duckdb(credentials=duckdb_path),
        dataset_name="raw",
    )
    load_info = pipeline.run(
        coingecko_source(
            snapshot_date=snapshot_date,
            simulate_new_field=simulate_new_field,
            simulate_type_drift=simulate_type_drift,
        )
    )
    print(load_info)
    log_schema_changes(load_info)


def log_schema_changes(load_info) -> None:
    """Print any tables/columns dlt added to the destination during this run."""
    for package in load_info.load_packages:
        for table_name, table in package.schema_update.items():
            for column_name, column in table["columns"].items():
                print(f"[SCHEMA EVOLVED] {table_name}.{column_name}: {column['data_type']}")


if __name__ == "__main__":
    load_coingecko()
```

`simulate_new_field`/`simulate_type_drift` are test-only hooks, defaulted off — normal runs (`load_coingecko()` with no args) never touch them.

---

## 2. Watermark + idempotent merge

- CoinGecko's `/coins/markets` has no server-side delta filter (always returns full current top-N state) — dlt's `incremental()` cursor doesn't apply. The watermark is self-generated: `snapshot_date` (UTC) is stamped onto every row at extraction time.
- `write_disposition="merge"` + composite `primary_key=["id", "snapshot_date"]` gives both properties from one mechanism: same-day rerun matches on the full key and updates in place (idempotent); a new day's run has a new `snapshot_date`, so nothing matches and rows insert (incremental).
- `snapshot_date` is parametrized, not hardcoded to `pendulum.today()` — required for backfill capability (Phase 3), not just testing convenience.

**Verify:**
```sql
SELECT snapshot_date, COUNT(*) FROM raw.coins_markets GROUP BY snapshot_date ORDER BY snapshot_date;
SELECT COUNT(*) FROM raw.coins_markets;
```

---

## 3. Schema contract

```python
"schema_contract": {"tables": "evolve", "columns": "evolve", "data_type": "freeze"}
```

- `tables`/`columns` stay `evolve`: a new field or a new nested/child table lands in `raw` automatically. Freezing either would fail the *entire* daily load over a harmless addition — for a single bulk snapshot call covering 250 coins, that's total data loss for the day, not a contained problem. Real impact-analysis gate is downstream: dbt staging models explicitly enumerate columns, so a new raw column stays inert until deliberately wired in via a reviewed PR.
- `data_type` is frozen: an already-relied-upon column receiving a value of an unexpected type is a real corruption risk, not a business-decision to make later. The load fails outright instead of silently creating a confusing variant column.
- `columns={"roi": {"data_type": "json"}}` — `roi` is a nested object (`{times, currency, percentage}`) when present, `null` on many coins (no ICO). Without an explicit type hint, dlt can't infer a type from an all-null batch and silently skips materializing the column.

**Visibility on evolution events** (dlt's documented pattern): `log_schema_changes()` in §1 walks `load_info.load_packages[].schema_update` after every run and prints anything that changed. There's a known dlt GitHub issue reporting `schema_update` sometimes returns empty even when a column was added — verified empirically in this pipeline that it populates correctly; don't assume it's reliable in a different dlt version without checking.

---

## 4. Secrets

- `dlt/.dlt/secrets.toml` — holds the CoinGecko Demo API key, never committed. Confirmed ignored via `dlt/.gitignore:3` (auto-generated by `dlt init`).
- `dlt/.dlt/config.toml` — non-sensitive dlt runtime config only (`log_level`, `dlthub_telemetry`), correctly tracked by git per dlt convention. Confirmed contents clean (untouched scaffold defaults).

**Verify a file is actually ignored (needs a path argument, doesn't work bare):**
```bash
git check-ignore -v dlt/.dlt/secrets.toml
```

**Recreate on a new machine** — see `docs/runbook.md`, "Cold start on a new machine," step 5.

---

## 5. Verification scripts

Both live in `dlt/`, documented with a docstring stating what they prove and expected output — not pytest tests (that's Phase 6), rerunnable manual proof scripts.

- `verify_watermark_idempotency.py` — three runs (real today, same-day rerun, forced next day), proves idempotency + incremental growth via row counts.
- `verify_schema_evolution.py` — three runs (baseline, simulated new field, simulated type drift), proves `evolve` lands new fields with visibility logging and `freeze` rejects a type mismatch outright.

---

## 6. Known issues / fix history

**DuckDB can't `ALTER TABLE ADD COLUMN` with a constraint on a table that already has rows.** Hit when `coins_markets` pre-existed in dev DuckDB (from earlier Phase 0 testing) before the `primary_key` hint was added — dlt tried to migrate the existing table in place, DuckDB rejected it (`Parser Error: Adding columns with constraints not yet supported`). Fix for disposable dev data: wipe and reload clean —
```bash
rm -f "$CRYPTO_PIPELINE_DUCKDB_PATH_DEV"
rm -rf ~/.dlt/pipelines/crypto_market_pipeline
```
Real-world fix when data can't be dropped: create a new table with the constraint from creation, copy + dedupe existing rows into it, verify no duplicate keys survived, swap table names. Not needed here since dev data is disposable, but the pattern is documented for when a real client's data is at stake.

**`merge` doesn't prune stale members.** Discovered when two separate calls tagged the same `snapshot_date` (a forced test date that later coincided with a real run) produced 252 rows instead of 250 for that date — confirmed via `GROUP BY snapshot_date`, traced to real CoinGecko top-250 ranking churn between the two calls. `merge` only upserts what's present in the current batch; it never deletes a row for a key that simply didn't appear in a later call. Not fixed — carried forward as a known gap for Phase 3's backfill/reconciliation design.

---

## 7. Deferred

**Optional SQL source** (dlt's `sql_database` source against e.g. a Dockerized Postgres) — listed as optional in the Build Brief, not part of the "done when" criteria. No business justification exists inside the current crypto scenario (both CoinGecko and the optional DeFiLlama enrichment are REST APIs, not SQL). Deliberately deferred rather than force-fit a synthetic justification — likely relevant later for an actual freelance client whose source of truth is a relational database.
