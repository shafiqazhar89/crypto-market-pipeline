with source as (
    select * from {{ source('raw', 'coins_markets') }}
),

renamed as (
    select
        id as coin_id,
        snapshot_date,
        current_price as price_usd,
        market_cap,
        total_volume,
        price_change_percentage_24h as price_change_pct_24h,
        market_cap_rank,
        circulating_supply,
        last_updated

    from source
)

select * from renamed