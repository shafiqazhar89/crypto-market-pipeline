
import pendulum
import os
import dlt
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
                "columns": {"roi": {"data_type": "json"}},
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
                row["current_price"] = "not-a-number"  # inject a string where dlt has already inferred a numeric type
                return row

    for resource in rest_api_resources(config):
            if resource.name == "coins_markets":
                resource.add_map(add_snapshot_date)
                if simulate_new_field:
                    resource.add_map(add_test_field)
                if simulate_type_drift:
                    resource.add_map(corrupt_current_price)
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

def log_schema_changes(load_info) -> None:
    """Print any tables/columns dlt added to the destination during this run."""
    for package in load_info.load_packages:
        for table_name, table in package.schema_update.items():
            for column_name, column in table["columns"].items():
                print(f"[SCHEMA EVOLVED] {table_name}.{column_name}: {column['data_type']}")


if __name__ == "__main__":
    load_coingecko()
