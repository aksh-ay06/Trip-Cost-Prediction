{#
  Use a model's custom schema as-is instead of dbt's default
  "<target_dataset>_<custom_schema>" naming. Without this, a model configured
  with schema='taxi_prod' lands in "taxi_staging_taxi_prod" rather than the
  taxi_prod dataset that Terraform creates.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.dataset }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
