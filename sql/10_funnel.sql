-- Воронка «просмотр → корзина → покупка» на уровне посетителя за весь период.
-- Шаг засчитывается, только если он случился не раньше предыдущего:
-- покупка без корзины или корзина без просмотра в воронку не попадают.
with first_view as (
    select visitor_id, min(event_ts) as view_ts
    from rr.events
    where event_type = 'view'
    group by visitor_id
),
first_cart as (
    select v.visitor_id, min(e.event_ts) as cart_ts
    from first_view v
    join rr.events e
      on e.visitor_id = v.visitor_id
     and e.event_type = 'addtocart'
     and e.event_ts >= v.view_ts
    group by v.visitor_id
),
purchase as (
    select distinct c.visitor_id
    from first_cart c
    join rr.events e
      on e.visitor_id = c.visitor_id
     and e.event_type = 'transaction'
     and e.event_ts >= c.cart_ts
),
steps as (
    select 1 as step_no, count(*) as visitors from first_view
    union all
    select 2, count(*) from first_cart
    union all
    select 3, count(*) from purchase
)
select s.step_no,
       t.step_name as step,
       s.visitors,
       round(s.visitors::numeric / lag(s.visitors) over (order by s.step_no), 4) as conv_from_prev,
       round(s.visitors::numeric / first_value(s.visitors) over (order by s.step_no), 4)
           as conv_from_start
from steps s
join rr.event_types t using (step_no)
order by s.step_no;
