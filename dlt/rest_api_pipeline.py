
import os
import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


@dlt.source
def coingecko_source(api_key=dlt.secrets.value):
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
    yield from rest_api_resources(config)


def load_coingecko() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="crypto_market_pipeline",
        destination=dlt.destinations.duckdb(
            credentials= os.environ["CRYPTO_PIPELINE_DUCKDB_PATH_DEV"]
        ),
        dataset_name="raw",
    )
    load_info = pipeline.run(coingecko_source())
    print(load_info)



if __name__ == "__main__":
    load_coingecko()
