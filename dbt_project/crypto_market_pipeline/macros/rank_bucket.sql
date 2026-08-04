-- macros/rank_bucket.sql
{% macro rank_bucket(rank_column) %}
    case
        when {{ rank_column }} is null then 'Unranked'
        when {{ rank_column }} <= 10 then 'Top 10'
        when {{ rank_column }} <= 50 then 'Top 50'
        when {{ rank_column }} <= 100 then 'Top 100'
        else 'Other'
    end
{% endmacro %}