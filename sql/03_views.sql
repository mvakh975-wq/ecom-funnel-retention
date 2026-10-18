-- Представления, на которые опираются отчёты.

-- Полные недели данных (понедельник–воскресенье, UTC). Первая и последняя неделя
-- источника неполные, их значения занижены, поэтому в недельных отчётах их нет.
create or replace view rr.full_weeks as
with bounds as (
    select min(event_ts) as first_ts, max(event_ts) as last_ts from rr.events
)
select week::date as week
from bounds,
     generate_series(date_trunc('week', first_ts), last_ts, interval '1 week') as week
where week >= first_ts::date
  and week + interval '7 days' <= last_ts;

-- Сессии: новая сессия начинается, если с предыдущего события посетителя прошло
-- больше 30 минут (стандартный порог веб-аналитики).
create or replace view rr.sessions as
with marked as (
    select visitor_id,
           event_id,
           event_ts,
           event_type,
           case
               when event_ts - lag(event_ts) over w <= interval '30 minutes' then 0
               else 1
           end as is_new_session
    from rr.events
    window w as (partition by visitor_id order by event_ts, event_id)
),
numbered as (
    select *,
           sum(is_new_session) over (
               partition by visitor_id order by event_ts, event_id
               rows between unbounded preceding and current row
           ) as session_no
    from marked
)
select visitor_id,
       session_no,
       min(event_ts) as session_start,
       max(event_ts) as session_end,
       count(*) as n_events,
       bool_or(event_type = 'addtocart') as has_cart,
       bool_or(event_type = 'transaction') as has_purchase
from numbered
group by visitor_id, session_no;
