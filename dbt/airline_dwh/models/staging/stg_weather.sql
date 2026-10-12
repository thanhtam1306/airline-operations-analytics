-- Clean daily weather. Keeps the missing-precipitation flag so the gap is
-- observable downstream, and provides a zero-filled column for aggregation.
with source as (
    select * from {{ source('raw', 'weather') }}
)

select
    cast(weather_date as date)                       as weather_date,
    upper(trim(airport_code))                        as airport_code,
    cast(temperature_f as double precision)          as temperature_f,
    precipitation_in                                 as precipitation_in,
    (precipitation_in is null)                       as is_precip_missing,
    coalesce(precipitation_in, 0)                    as precipitation_in_filled,
    cast(wind_speed_mph as double precision)         as wind_speed_mph,
    cast(visibility_mi as double precision)          as visibility_mi,
    trim(conditions)                                 as conditions,
    (is_severe = 1)                                  as is_severe
from source
