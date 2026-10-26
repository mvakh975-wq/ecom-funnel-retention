-- Чем покупатели отличаются от остальных: сессии и просмотры на посетителя,
-- медианное число просмотров до первой покупки. Распределения с тяжёлым хвостом
-- (единичные посетители с тысячами событий), поэтому рядом со средними — медианы.
with first_purchase as (
    select visitor_id, min(event_ts) as purchase_ts
    from rr.events
    where event_type = 'transaction'
    group by visitor_id
),
per_visitor as (
    select e.visitor_id,
           fp.purchase_ts is not null as is_buyer,
           count(*) filter (where e.event_type = 'view') as views,
           count(*) filter (where e.event_type = 'view' and e.event_ts < fp.purchase_ts)
               as views_before_purchase
    from rr.events e
    left join first_purchase fp using (visitor_id)
    group by e.visitor_id, fp.purchase_ts
),
sessions as (
    select visitor_id, count(*) as sessions
    from rr.sessions
    group by visitor_id
)
select case when is_buyer then 'Покупатели' else 'Не покупали' end as segment,
       count(*) as visitors,
       round(avg(s.sessions), 2) as avg_sessions,
       round(avg(v.views), 2) as avg_views,
       percentile_cont(0.5) within group (order by s.sessions) as median_sessions,
       percentile_cont(0.5) within group (order by v.views) as median_views,
       percentile_cont(0.5) within group (order by v.views_before_purchase)
           filter (where is_buyer) as median_views_before_purchase
from per_visitor v
join sessions s using (visitor_id)
group by is_buyer
order by is_buyer desc;
