{% snapshot dim_coin_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='coin_id',
        strategy='check',
        check_cols=['symbol', 'name', 'categories', 'total_supply', 'max_supply'],
    )
}}

select * from {{ ref('stg_coingecko__coin_metadata') }}

{% endsnapshot %}