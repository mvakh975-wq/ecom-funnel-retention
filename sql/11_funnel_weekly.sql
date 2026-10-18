-- Воронка по неделям: посетители, которые смотрели товары в эту неделю, и сколько из них
-- в ту же неделю положили товар в корзину и затем купили. Только полные недели (UTC).
with weekly as (
    select visitor_id,
           date_trunc('week', event_ts)::date as week,
           min(event_ts) filter (where event_type = 'view') as view_ts
    from rr.events
    group by visitor_id, date_trunc('week', event_ts)::date
),
carts as (
    select w.visitor_id, w.week, min(e.event_ts) as cart_ts
    from weekly w
    join rr.events e
      on e.visitor_id = w.visitor_id
     and e.event_type = 'addtocart'
     and e.event_ts >= w.view_ts
     and date_trunc('week', e.event_ts)::date = w.week
    group by w.visitor_id, w.week
),
purchases as (
    select distinct c.visitor_id, c.week
    from carts c
    join rr.events e
      on e.visitor_id = c.visitor_id
     and e.event_type = 'transaction'
     and e.event_ts >= c.cart_ts
     and date_trunc('week', e.event_ts)::date = c.week
)
select w.week,
       count(*) as visitors,
       count(c.visitor_id) as carted,
       count(p.visitor_id) as purchased,
       round(count(c.visitor_id)::numeric / count(*), 4) as cr_cart,
       round(count(p.visitor_id)::numeric / count(*), 4) as cr_purchase
from weekly w
join rr.full_weeks using (week)
left join carts c using (visitor_id, week)
left join purchases p using (visitor_id, week)
where w.view_ts is not null
group by w.week
order by w.week;
