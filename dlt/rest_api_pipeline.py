
import pendulum
import os
import dlt
import time
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


@dlt.source
def coingecko_source(api_key=dlt.secrets.value, snapshot_date=None, simulate_new_field=False, simulate_type_drift=False,):
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
                "columns": {
                    "roi": {"data_type": "json"},
                    "current_price": {"data_type": "double"},
                    "market_cap": {"data_type": "double"},
                    "fully_diluted_valuation": {"data_type": "double"},
                    "total_volume": {"data_type": "double"},
                    "high_24h": {"data_type": "double"},
                    "low_24h": {"data_type": "double"},
                    "price_change_24h": {"data_type": "double"},
                    "price_change_percentage_24h": {"data_type": "double"},
                    "market_cap_change_24h": {"data_type": "double"},
                    "market_cap_change_percentage_24h": {"data_type": "double"},
                    "circulating_supply": {"data_type": "double"},
                    "total_supply": {"data_type": "double"},
                    "max_supply": {"data_type": "double"},
                    "ath": {"data_type": "double"},
                    "ath_change_percentage": {"data_type": "double"},
                    "atl": {"data_type": "double"},
                    "atl_change_percentage": {"data_type": "double"},
                    "market_cap_rank": {"data_type": "bigint"},
                },
                "schema_contract": {"tables": "evolve", "columns": "evolve", "data_type": "freeze"},
                "endpoint": {
                    "path": "coins/markets",
                     # Query parameters for the endpoint
                     "params": {
                         "vs_currency": "usd",
                         "per_page": 250,
                         "page": 1
                     }
                    
                    }
            },
            {
                "name": "coin_metadata",
                "write_disposition": "replace",
                "columns": {"categories": {"data_type": "json"}},
                "endpoint": {
                    "path": "coins/{resources.coins_markets.id}",
                    "params": {
                        "localization": "false",
                        "tickers": "false",
                        "market_data": "true",
                        "community_data": "false",
                        "developer_data": "false",
                        "sparkline": "false",
                    },
                },
            },
        ],
    }
    if snapshot_date is None:
        snapshot_date = pendulum.today("UTC").to_date_string()

    def add_snapshot_date(row):
            # print(f"[DEBUG] add_snapshot_date fired, row has {len(row)} keys")
            row["snapshot_date"] = snapshot_date
            return row

    def add_test_field(row):
                row["test_field"] = "test_value"
                return row

    def corrupt_current_price(row):
                row["current_price"] = "not-a-number"  # inject a string where dlt has already inferred a numeric type
                return row

    def slim_coin_metadata(row):
        market_data = row.get("market_data") or {}
        return {
            "id": row.get("id"),
            "symbol": row.get("symbol"),
            "name": row.get("name"),
            "categories": row.get("categories"),
            "market_cap_rank": row.get("market_cap_rank"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "max_supply": market_data.get("max_supply"),
            "last_updated": row.get("last_updated"),
        }

    def throttle_coin_metadata_calls(row):
        time.sleep(0.7)
        return row

    for resource in rest_api_resources(config):
            # print(f"[DEBUG] discovered resource: {resource.name}")
            if resource.name == "coins_markets":
                resource.add_map(add_snapshot_date)
                if simulate_new_field:
                    resource.add_map(add_test_field)
                if simulate_type_drift:
                    resource.add_map(corrupt_current_price)
            if resource.name == "coin_metadata":
                resource.add_map(slim_coin_metadata)
                resource.add_map(add_snapshot_date)
                resource.add_map(throttle_coin_metadata_calls)
            yield resource



def load_coingecko(snapshot_date: str | None = None , simulate_new_field: bool = False, simulate_type_drift: bool = False) -> None:
    duckdb_path = os.environ["CRYPTO_PIPELINE_DUCKDB_PATH_DEV"]
    os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)
    
    pipeline = dlt.pipeline(
        pipeline_name="crypto_market_pipeline",
        destination=dlt.destinations.duckdb(
            credentials= duckdb_path
        ),
        dataset_name="raw",
    )
    load_info = pipeline.run(coingecko_source(snapshot_date=snapshot_date, simulate_new_field=simulate_new_field, simulate_type_drift=simulate_type_drift))
    print(load_info)

    log_schema_changes(load_info)
    assert_rows_loaded(load_info)

def log_schema_changes(load_info) -> None:
    """Print any tables/columns dlt added to the destination during this run."""
    for package in load_info.load_packages:
        for table_name, table in package.schema_update.items():
            for column_name, column in table["columns"].items():
                print(f"[SCHEMA EVOLVED] {table_name}.{column_name}: {column['data_type']}")

def assert_rows_loaded(load_info, expected_tables=("coins_markets", "coin_metadata")) -> None:
    """Fail loudly if a resource that must never be empty loaded zero rows.

    CoinGecko soft-throttles with HTTP 200 + an empty array rather than a 429,
    which dlt correctly interprets as 'no data' — a silent success that
    truncates replace-disposition tables. Never let that pass as OK.
    """
    row_counts = {}
    for package in load_info.load_packages:
        for job in package.jobs["completed_jobs"]:
            table = job.job_file_info.table_name
            if not table.startswith("_dlt"):
                row_counts[table] = row_counts.get(table, 0) + 1

    empty = [t for t in expected_tables if row_counts.get(t, 0) == 0]
    if empty:
        raise RuntimeError(
            f"Load produced no data for: {', '.join(empty)}. "
            "Likely a soft-throttled empty response from the source. "
            "Destination may have been truncated — investigate before rerunning."
        )


if __name__ == "__main__":
    load_coingecko()
