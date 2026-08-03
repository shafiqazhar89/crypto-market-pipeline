select
    coin_id,
    symbol,
    name,
    categories,
    max_supply,
    market_cap_rank_bucket,
    case when dbt_valid_to is null then 'active' else 'inactive' end as status,
    dbt_valid_from,
    dbt_valid_to
from {{ ref('dim_coin_snapshot') }}