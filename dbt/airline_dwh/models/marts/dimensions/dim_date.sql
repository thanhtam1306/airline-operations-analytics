-- Conformed date dimension, generated across the range present in the data.
with bounds as (
    select
        min(flight_date) as min_date,
        max(flight_date) as max_date
    from {{ ref('stg_flights') }}
),

spine as (
    {% if target.type == 'postgres' %}
    select
        generate_series(min_date::timestamp, max_date::timestamp, interval '1 day')::date as date_day
    from bounds
    {% else %}
    select
        cast(unnest(generate_series(min_date, max_date, interval 1 day)) as date) as date_day
    from bounds
    {% endif %}
)

select
    {% if target.type == 'postgres' %}
    cast(to_char(date_day, 'YYYYMMDD') as integer) as date_key,
    date_day,
    extract(year    from date_day)::integer        as year,
    extract(quarter from date_day)::integer        as quarter,
    extract(month   from date_day)::integer        as month,
    trim(to_char(date_day, 'Month'))               as month_name,
    extract(day     from date_day)::integer        as day_of_month,
    extract(dow     from date_day)::integer        as day_of_week,
    trim(to_char(date_day, 'Day'))                 as day_name,
    (extract(dow    from date_day) in (0, 6))      as is_weekend,
    extract(week    from date_day)::integer        as week_of_year
    {% else %}
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,
    extract(year   from date_day)                 as year,
    extract(quarter from date_day)                as quarter,
    extract(month  from date_day)                 as month,
    strftime(date_day, '%B')                      as month_name,
    extract(day    from date_day)                 as day_of_month,
    extract(dayofweek from date_day)              as day_of_week,
    strftime(date_day, '%A')                      as day_name,
    (extract(dayofweek from date_day) in (0, 6))  as is_weekend,
    extract(week from date_day)                   as week_of_year
    {% endif %}
from spine
