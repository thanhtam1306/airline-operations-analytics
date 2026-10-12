-- Route-level performance: on-time %, delays and cancellations per origin->dest.
with f as (
    select * from {{ ref('fact_flights') }}
)

select
    origin_airport,
    dest_airport,
    origin_airport || '-' || dest_airport                              as route,
    count(*)                                                           as total_flights,
    sum(case when is_cancelled then 1 else 0 end)                     as cancelled_flights,
    round(cast(100.0 * sum(case when is_cancelled then 1 else 0 end) / count(*) as numeric), 2) as cancellation_pct,
    round(cast(avg(case when not is_cancelled then dep_delay_min end) as numeric), 2)   as avg_dep_delay_min,
    round(cast(avg(case when not is_cancelled then arr_delay_min end) as numeric), 2)   as avg_arr_delay_min,
    round(
        cast(100.0 * sum(case when is_on_time then 1 else 0 end)
        / nullif(sum(case when not is_cancelled then 1 else 0 end), 0) as numeric), 2
    )                                                                  as on_time_pct,
    round(cast(avg(distance_miles) as numeric), 1)                     as avg_distance_miles
from f
group by 1, 2, 3
having count(*) >= 20
