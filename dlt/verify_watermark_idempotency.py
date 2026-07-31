
"""
Proves idempotency + incremental loading for the coins_markets resource.

Run 1: today's real snapshot_date -> expect 250 rows.
Run 2: same-day rerun -> expect still 250 (merge updates in place, no duplicate).
Run 3: forced next-day snapshot_date -> expect 500 total (250 new inserts).

Verify manually after running:
    duckdb $CRYPTO_PIPELINE_DUCKDB_PATH_DEV
    SELECT snapshot_date, COUNT(*) FROM raw.coins_markets GROUP BY snapshot_date;
"""
import pendulum
from rest_api_pipeline import load_coingecko  # confirm this matches your actual filename

load_coingecko()                                                # run 1: real today
load_coingecko()                                                 # run 2: same-day rerun
tomorrow = pendulum.today("UTC").add(days=1).to_date_string()
load_coingecko(snapshot_date=tomorrow)                            # run 3: forced next day
