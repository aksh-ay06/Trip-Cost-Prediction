{{ config(
    materialized='table',
    schema='taxi_prod'
) }}

select
    pickup_hour,
    pickup_dayofweek,
    is_weekend,
    passenger_count,
    trip_distance,
    fare_amount
from {{ ref('stg_taxi_trips') }}
where trip_distance between 0.1 and 100
  and fare_amount between 2.5 and 500
