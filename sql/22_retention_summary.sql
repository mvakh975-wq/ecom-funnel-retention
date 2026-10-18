-- Retention недели N в среднем по когортам, взвешенно: сумма вернувшихся / сумма размеров
-- когорт, у которых неделя N уже полностью прошла.
with cells as (
    select fw.cohort_week, (a.week - fw.cohort_week) / 7 as week_offset, a.visitor_id
    from (
        select visitor_id, date_trunc('week', min(event_ts))::date as cohort_week
        from rr.events
        group by visitor_id
    ) fw
    join (select distinct visitor_id, date_trunc('week', event_ts)::date as week from rr.events) a
      using (visitor_id)
    join rr.full_weeks w on w.week = a.week
    join rr.full_weeks c on c.week = fw.cohort_week
),
sizes as (
    select cohort_week, count(distinct visitor_id) as cohort_size
    from cells
    group by cohort_week
),
returns as (
    select cohort_week, week_offset, count(distinct visitor_id) as active
    from cells
    group by cohort_week, week_offset
)
select r.week_offset,
       count(*) as cohorts,
       sum(r.active) as active,
       sum(s.cohort_size) as cohort_size,
       round(sum(r.active)::numeric / sum(s.cohort_size), 4) as retention
from returns r
join sizes s using (cohort_week)
group by r.week_offset
order by r.week_offset;
