-- macros/max_snapshot_date.sql
{% macro max_snapshot_date(relation) %}
    (select max(snapshot_date) from {{ relation }})
{% endmacro %}