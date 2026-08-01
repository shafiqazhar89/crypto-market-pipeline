"""
Proves schema evolution + drift handling for the coins_markets resource.

Run 1: baseline, no simulation -> normal load, no schema changes logged.
Run 2: simulate_new_field=True -> load succeeds, "test_field" column added,
       [SCHEMA EVOLVED] logged (schema_contract columns=evolve).
Run 3: simulate_type_drift=True -> load FAILS. current_price receives a
       string where dlt already inferred a numeric type
       (schema_contract data_type=freeze).

Verify manually after running:
    duckdb $CRYPTO_PIPELINE_DUCKDB_PATH_DEV
    SELECT snapshot_date, test_field FROM raw.coins_markets WHERE test_field IS NOT NULL LIMIT 5;
"""
from rest_api_pipeline import load_coingecko

load_coingecko()
load_coingecko(simulate_new_field=True)
load_coingecko(simulate_type_drift=True)