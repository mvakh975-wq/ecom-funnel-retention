-- Перенос из сырых таблиц-стейджингов (заполняются COPY) в рабочую схему.
-- timestamp источника — миллисекунды Unix в UTC.

insert into rr.categories (category_id, parent_id)
select categoryid, parentid
from raw_category_tree;

insert into rr.events (event_ts, visitor_id, event_type, item_id, transaction_id)
select to_timestamp(timestamp / 1000.0), visitorid, event, itemid, transactionid
from raw_events
order by timestamp
on conflict on constraint events_natural_key do nothing;

analyze rr.events;
