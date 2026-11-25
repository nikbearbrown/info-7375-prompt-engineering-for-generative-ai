-- dbt's four built-in tests (unique, not_null, accepted_values, relationships) have no range rule,
-- so this is a small custom generic test: it returns the rows that FAIL, and passes when none do.
{% test not_negative(model, column_name) %}
select * from {{ model }} where {{ column_name }} < 0
{% endtest %}
