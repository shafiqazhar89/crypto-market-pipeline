with coin_metadata as (
    select * from {{ ref('stg_coingecko__coin_metadata') }}
),

latest_market_snapshot as (
    select coin_id, market_cap_rank
    from {{ ref('stg_coingecko__coins_markets') }}
    where snapshot_date = (
        select max(snapshot_date) from {{ ref('stg_coingecko__coins_markets') }}
    )
),

joined as (
    select
        cm.coin_id,
        cm.symbol,
        cm.name,
        cm.categories,
        cm.max_supply,
        cm.last_updated,
        lms.market_cap_rank,
        case
            when lms.market_cap_rank is null then 'Unranked'
            when lms.market_cap_rank <= 10 then 'Top 10'
            when lms.market_cap_rank <= 50 then 'Top 50'
            when lms.market_cap_rank <= 100 then 'Top 100'
            else 'Other'
        end as market_cap_rank_bucket
    from coin_metadata cm
    left join latest_market_snapshot lms on cm.coin_id = lms.coin_id
)

select * from joined