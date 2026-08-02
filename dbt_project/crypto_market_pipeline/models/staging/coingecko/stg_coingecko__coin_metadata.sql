with source as (
    select * from {{ source('raw', 'coin_metadata') }}
),

renamed as (
    select
        id as coin_id,
        symbol,
        name,
        categories,
        total_supply,
        max_supply,
        last_updated

    from source
)

select * from renamed