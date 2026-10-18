-- Retention по недельным когортам: когорта — неделя первого визита посетителя,
-- активен — было любое событие в неделю cohort_week + week_offset.
-- Берутся только полные недели: и когорта, и неделя возврата.
with first_week as (
    select visitor_id, date_trunc('week', min(event_ts))::date as cohort_week
    from rr.events
    group by visitor_id
),
activity as (
    select distinct visitor_id, date_trunc('week', event_ts)::date as week
    from rr.events
),
cohorts as (
    select cohort_week, count(*) as cohort_size
    from first_week
    join rr.full_weeks f on f.week = first_week.cohort_week
    group by cohort_week
),
returns as (
    select fw.cohort_week,
           (a.week - fw.cohort_week) / 7 as week_offset,
           count(*) as active
    from first_week fw
    join activity a using (visitor_id)
    join rr.full_weeks f on f.week = a.week
    group by fw.cohort_week, a.week
)
select c.cohort_week,
       c.cohort_size,
       r.week_offset,
       r.active,
       round(r.active::numeric / c.cohort_size, 4) as retention
from cohorts c
join returns r using (cohort_week)
order by c.cohort_week, r.week_offset;
