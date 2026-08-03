{% snapshot dim_coin_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='coin_id',
        strategy='check',
        check_cols=['symbol', 'name', 'categories', 'max_supply', 'market_cap_rank_bucket'],
        hard_deletes='invalidate',
    )
}}

select * from {{ ref('int_coin_metadata_enriched') }}

{% endsnapshot %}