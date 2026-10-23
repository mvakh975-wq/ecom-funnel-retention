-- Схема для событий интернет-магазина Retailrocket.
-- Пересоздаётся целиком: drop schema ... cascade.

drop schema if exists rr cascade;
create schema rr;

-- Справочник типов событий: новые типы добавляются строкой, а не изменением CHECK.
create table rr.event_types (
    event_type text primary key,
    step_no    smallint not null unique check (step_no between 1 and 3),
    step_name  text not null unique
);

insert into rr.event_types (event_type, step_no, step_name) values
    ('view',        1, 'Просмотр'),
    ('addtocart',   2, 'Корзина'),
    ('transaction', 3, 'Покупка');

-- Дерево категорий: ссылка на родителя внутри той же таблицы.
create table rr.categories (
    category_id bigint primary key,
    parent_id   bigint references rr.categories (category_id) on delete restrict
);
create index on rr.categories (parent_id);

create table rr.events (
    event_id       bigint generated always as identity primary key,
    event_ts       timestamptz not null,
    visitor_id     bigint not null,
    event_type     text not null references rr.event_types (event_type) on delete restrict,
    item_id        bigint not null,
    transaction_id bigint,
    -- id покупки есть ровно у событий-покупок
    constraint events_transaction_id_check
        check ((event_type = 'transaction') = (transaction_id is not null)),
    -- полные дубли строк источника отбрасываются при загрузке
    constraint events_natural_key
        unique nulls not distinct (event_ts, visitor_id, event_type, item_id, transaction_id)
);
create index on rr.events (visitor_id, event_ts);
-- тип события первым: запрос берёт из индекса только нужный шаг воронки, уже
-- упорядоченный по посетителю, и не читает саму таблицу (Index Only Scan)
create index on rr.events (event_type, visitor_id, event_ts);
