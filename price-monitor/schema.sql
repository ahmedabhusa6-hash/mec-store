-- MEC — قاعدة مراقبة أسعار الموردين عبر تلغرام (Supabase schema v3)
-- v1 2026-10-09: الجداول الأساسية (TG-SI-E)
-- v2 2026-10-11: discoveries.kind + settings + latest_prices بعنوان (TG-SI-G)
-- v3 2026-10-12: بوابة موافقات المالك + app_users/alerts/audit_log + RLS + views قراءة
-- التطبيق: scripts/rebuild/migration_v3.py (idempotent — يحفظ كل البيانات التاريخية)

-- 1) سجل القنوات/المجموعات (المنضمّة + الأهداف المستقبلية)
create table if not exists tg_channels (
  tg_id        bigint primary key,
  username     text,
  title        text,
  kind         text not null default 'channel',      -- channel | group
  relevance    text not null default 'possible',     -- anchor | relevant | possible | new
  joined       boolean not null default false,
  joined_at    timestamptz,
  join_error   text,
  last_msg_id  bigint not null default 0,            -- آخر رسالة ممسوحة (مسح تفاضلي)
  last_scanned timestamptz,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now()
);

-- 2) رصد الأسعار (الخام، بلا مزج — كل ملاحظة بدليلها)
create table if not exists price_observations (
  id           bigserial primary key,
  channel_id   bigint,
  username     text,
  message_id   bigint,
  posted_at    timestamptz,
  captured_at  timestamptz not null default now(),
  product      text not null,
  price        numeric(12,4),
  currency     text not null default 'USD',
  unit         text,
  raw_text     text,
  unique (channel_id, message_id, product, price, currency)
);
create index if not exists idx_po_channel on price_observations (channel_id, posted_at desc);
create index if not exists idx_po_product on price_observations (product, posted_at desc);

-- 3) بيانات الضمان/الدفع/الحد الأدنى
create table if not exists statements (
  id           bigserial primary key,
  channel_id   bigint,
  message_id   bigint,
  posted_at    timestamptz,
  kind         text not null,                         -- warranty | payment | min_order | replacement
  text         text,
  unique (channel_id, message_id, kind, text)
);

-- 4) الاكتشافات: مقابض عامة + روابط دعوة خاصة (بوابة موافقة المالك)
create table if not exists discoveries (
  handle       text primary key,                      -- @handle أو +invite_hash
  seen_in      bigint,
  seen_at      timestamptz not null default now(),
  status       text not null default 'pending',       -- pending | awaiting_approval | approved | joined | rejected | not_found | expired | request_needed | request_sent
  kind         text not null default 'handle',        -- handle | invite
  title        text,                                  -- من معاينة الدعوة الخاصة
  members      integer,
  preview_at   timestamptz,
  source       text not null default 'auto',          -- auto | manual
  approved_by  text,
  approved_at  timestamptz,
  last_error   text
);
create index if not exists idx_disc_status on discoveries (status);
create index if not exists idx_disc_status_kind on discoveries (status, kind);

-- 5) سجل تشغيلات الأتمتة
create table if not exists runs (
  id               bigserial primary key,
  started_at       timestamptz not null default now(),
  finished_at      timestamptz,
  runner           text,                              -- github-actions | local
  dispatched_by    text,                              -- بريد المالك إن أُطلقت من اللوحة
  channels_scanned integer default 0,
  new_messages     integer default 0,
  prices_added     integer default 0,
  new_handles      integer default 0,
  invites_found    integer default 0,
  joins_ok         integer default 0,
  joins_private    integer default 0,
  errors           text
);

-- 6) إعدادات حية (سياسات + قواطع أمان) — يقرؤها المراقب كل دورة
create table if not exists settings (
  key        text primary key,
  value      text,
  updated_at timestamptz not null default now(),
  updated_by text
);

-- 7) حساب مالك لوحة التحكم (scrypt — لا تخزين لكلمة مرور صريحة)
create table if not exists app_users (
  id            bigserial primary key,
  email         text unique not null,
  password_hash text not null,
  role          text not null default 'owner',
  created_at    timestamptz not null default now(),
  last_login_at timestamptz
);

-- 8) التنبيهات (يولدها المراقب والمنصة)
create table if not exists alerts (
  id         bigserial primary key,
  severity   text not null default 'info',            -- info | warning | critical
  category   text not null,                           -- monitor | breaker | security | quality | system
  title      text not null,
  message    text,
  entity     text,
  entity_id  text,
  meta       jsonb,
  created_at timestamptz not null default now(),
  read_at    timestamptz
);
create index if not exists idx_alerts_created on alerts (created_at desc);
create index if not exists idx_alerts_read on alerts (read_at);

-- 9) سجل التدقيق (كل إجراء حساس — غير قابل للحذف من الواجهات)
create table if not exists audit_log (
  id         bigserial primary key,
  actor      text not null,                           -- email المالك | monitor
  action     text not null,
  entity     text,
  entity_id  text,
  details    jsonb,
  ip         text,
  created_at timestamptz not null default now()
);
create index if not exists idx_audit_created on audit_log (created_at desc);

-- 10) RLS: deny-by-default — المفتاح الخدمي (المراقب + خادم الويب) يتجاوز؛
--     القراءة العامة تمر حصريًا عبر واجهة facts-only في تطبيق الويب.
alter table tg_channels        enable row level security;
alter table price_observations enable row level security;
alter table statements         enable row level security;
alter table discoveries        enable row level security;
alter table runs               enable row level security;
alter table settings           enable row level security;
alter table app_users          enable row level security;
alter table alerts             enable row level security;
alter table audit_log          enable row level security;

-- 11) عرض أحدث سعر لكل (قناة × منتج)
create or replace view latest_prices as
select distinct on (po.channel_id, po.product)
  po.channel_id, po.username, c.title, po.product, po.price, po.currency,
  po.unit, po.posted_at, po.raw_text
from price_observations po
left join tg_channels c on c.tg_id = po.channel_id
order by po.channel_id, po.product, po.posted_at desc;

-- 12) views للتجميع من جانب قاعدة البيانات (تغذي لوحة التحكم)
create or replace view v_daily_volume as
select to_char(posted_at, 'YYYY-MM-DD') as day, count(*) as count
from price_observations
where posted_at is not null
group by 1 order by 1;

create or replace view v_product_stats as
select po.product,
       count(distinct po.channel_id) as suppliers,
       count(*) as observations,
       min(po.price) as min_price,
       max(po.price) as max_price,
       max(po.posted_at) as last_seen
from price_observations po
where po.price is not null
group by po.product;

create or replace view v_channel_stats as
select c.tg_id, c.username, c.title, c.kind, c.relevance, c.joined,
       c.last_scanned, c.last_msg_id, c.updated_at,
       (select count(*) from price_observations po where po.channel_id = c.tg_id) as observations,
       (select count(distinct po.product) from price_observations po where po.channel_id = c.tg_id) as products,
       (select max(po.posted_at) from price_observations po where po.channel_id = c.tg_id) as last_price_at
from tg_channels c;

create or replace view v_statement_stats as
select kind, count(*) as count from statements group by kind;

create or replace view v_supplier_stats as
select c.tg_id as channel_id, c.username, c.title, c.kind,
       count(distinct po.product) as products,
       count(po.id) as observations,
       min(po.posted_at) as first_seen,
       max(po.posted_at) as last_seen,
       round(avg(po.price) filter (where po.currency in ('USD','USDT')), 2) as avg_price_usd,
       (select count(*) from statements s where s.channel_id = c.tg_id and s.kind = 'warranty') as warranty,
       (select count(*) from statements s where s.channel_id = c.tg_id and s.kind = 'payment') as payment,
       (select count(*) from statements s where s.channel_id = c.tg_id and s.kind = 'min_order') as min_order
from tg_channels c
join price_observations po on po.channel_id = c.tg_id
group by c.tg_id, c.username, c.title, c.kind
having count(po.id) > 0;

create or replace view v_freshness as
select lp.channel_id, lp.username, lp.title, lp.product, lp.price, lp.currency,
       lp.unit, lp.posted_at,
       round(extract(epoch from (now() - lp.posted_at)) / 3600.0, 1) as age_hours
from latest_prices lp;
