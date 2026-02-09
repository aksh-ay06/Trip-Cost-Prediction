{{ config(materialized='view') }}

select
    cast(pickup_datetime as timestamp)   as pickup_datetime,
    cast(dropoff_datetime as timestamp)  as dropoff_datetime,
    cast(passenger_count as int64)       as passenger_count,
    cast(trip_distance as float64)       as trip_distance,
    cast(fare_amount as float64)         as fare_amount,
    cast(tip_amount as float64)          as tip_amount,
    cast(tolls_amount as float64)        as tolls_amount,
    cast(total_amount as float64)        as total_amount,
    cast(payment_type as string)         as payment_type,
    cast(pickup_hour as int64)           as pickup_hour,
    cast(pickup_dayofweek as int64)      as pickup_dayofweek,
    cast(is_weekend as int64)            as is_weekend,
    cast(trip_duration_min as float64)   as trip_duration_min
from {{ source('taxi_staging', 'yellow_trips_processed') }}
