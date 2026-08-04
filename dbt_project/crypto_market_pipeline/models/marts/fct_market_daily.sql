{{
    config(
        materialized='incremental',
        unique_key=['coin_id', 'snapshot_date'],
        incremental_strategy='delete+insert',
    )
}}

select
    coin_id,
    snapshot_date,
    price_usd,
    market_cap,
    total_volume,
    price_change_pct_24h,
    market_cap_rank,
    circulating_supply,
    last_updated
from {{ ref('stg_coingecko__coins_markets') }}

{% if is_incremental() %}
where snapshot_date > {{ max_snapshot_date(this) }}
{% endif %}