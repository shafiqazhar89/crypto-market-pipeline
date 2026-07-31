
import pendulum
import os
import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


@dlt.source
def coingecko_source(api_key=dlt.secrets.value, snapshot_date=None):
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

    for resource in rest_api_resources(config):
            if resource.name == "coins_markets":
                resource.add_map(add_snapshot_date)
            yield resource



def load_coingecko(snapshot_date: str | None = None) -> None:
    duckdb_path = os.environ["CRYPTO_PIPELINE_DUCKDB_PATH_DEV"]
    os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)
    
    pipeline = dlt.pipeline(
        pipeline_name="crypto_market_pipeline",
        destination=dlt.destinations.duckdb(
            credentials= duckdb_path
        ),
        dataset_name="raw",
    )
    load_info = pipeline.run(coingecko_source(snapshot_date=snapshot_date))
    print(load_info)



if __name__ == "__main__":
    load_coingecko()
