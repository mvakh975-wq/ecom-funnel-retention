-- Сколько покупателей не попадает в упорядоченную воронку и почему:
-- часть покупала без события «корзина», у части события идут в другом порядке.
with per_visitor as (
    select visitor_id,
           min(event_ts) filter (where event_type = 'view') as view_ts,
           bool_or(event_type = 'addtocart') as has_cart,
           bool_or(event_type = 'transaction') as is_buyer
    from rr.events
    group by visitor_id
),
ordered as (
    select distinct c.visitor_id
    from per_visitor v
    join lateral (
        select e.visitor_id, min(e.event_ts) as cart_ts
        from rr.events e
        where e.visitor_id = v.visitor_id
          and e.event_type = 'addtocart'
          and e.event_ts >= v.view_ts
        group by e.visitor_id
    ) c on true
    join rr.events t
      on t.visitor_id = c.visitor_id
     and t.event_type = 'transaction'
     and t.event_ts >= c.cart_ts
)
select count(*) filter (where is_buyer) as buyers,
       (select count(*) from ordered) as in_ordered_funnel,
       count(*) filter (where is_buyer and not has_cart) as never_carted,
       round(1 - (select count(*) from ordered)::numeric / count(*) filter (where is_buyer), 4)
           as share_outside_funnel
from per_visitor;
