#!/usr/bin/env python3
"""MEC — مراقب أسعار الموردين التلقائي عبر تلغرام (v3)
Runs on GitHub Actions every 30 minutes (or on-demand dispatch from the owner
console). Owner-authorized 2026-10-09/11/12.

ماذا يفعل في كل تشغيل:
  1) قفل تشغيل (منع تزامن جلستين — حماية الجلسة من الإبطال)
  2) قراءة السياسات من settings (قابلة للضبط من لوحة تحكم المالك)
  3) مسح تفاضلي دوّار لكل المصادر المسجلة (الأقدم مسحًا أولًا)
  4) استخراج الأسعار/الضمانات/الشروط → Supabase
  5) تسجيل الاكتشافات: مقابض عامة + روابط دعوة خاصة
  6) الانضمام المنضبط:
     - العامة: تلقائي ضمن الميزانيات (سياسة المالك القائمة)
     - الخاصة: بوابة موافقة — معاينة قراءةً فقط → بانتظار المالك →
       التنفيذ عند status=approved (بعد اعتماده من لوحة التحكم)
  7) تنبيهات + تدقيق: كل حدث حساس يُسجل في alerts و audit_log

═══ طبقة الانضباط (شروط خدمة تلغرام — قراءة رسمية 2026-10-11) ═══
  · ToS: السبام = إرسال رسائل غير مرغوبة أو إضافة أشخاص — لا نرسل شيئًا
    أبدًا ولا نضيف أحدًا ولا نتفاعل؛ الانضمام عبر روابط معلنة سلوك مستخدم طبيعي.
  · API Terms: api_id خاص بالمالك، لا تدريب نماذج AI على بيانات تلغرام،
    لا أفعال دون علم المالك ورضاه (كل عملياتنا بتفويضه المباشر).
  · حدود المنصة: عضوية ≤500 قناة/مجموعة (مجاني) — سقفنا 250 بهامش مضاعف.
  · الانضباط الرقمي: انضمامات قليلة بمعدلات منخفضة، فواصل عشوائية،
    قواطع دوائر (PeerFlood 48h · FloodWait ≥6h)، احترام كامل لـ FloodWait.

Auth: TG_SESSION (StringSession, GitHub secret) أو ملف جلسة محلي.
"""
import os, sys, json, re, time, random, urllib.request, faulthandler
from urllib.parse import quote as _urlq
from datetime import datetime, timezone, timedelta

faulthandler.enable()  # تتبع الجمود فور حدوثه (التزام تشغيلي معتمد)

# ---------------- config (env defaults; settings table overrides) ----------------
FIRST_SCAN_CAP = int(os.environ.get("FIRST_SCAN_CAP", "1200"))
DELTA_CAP      = int(os.environ.get("DELTA_CAP", "800"))
TIME_BUDGET_S  = int(os.environ.get("TIME_BUDGET_S", "960"))
JOIN_DEADLINE_S = int(os.environ.get("JOIN_DEADLINE_S", "1500"))
SCAN_DELAY     = (1.5, 3.5)

TOTAL_JOIN_BUDGET   = int(os.environ.get("TOTAL_JOIN_BUDGET", "3"))
PRIVATE_JOIN_CAP    = int(os.environ.get("PRIVATE_JOIN_CAP", "2"))
JOIN_TOTAL_CEILING  = int(os.environ.get("JOIN_TOTAL_CEILING", "250"))
JOIN_DELAY          = (12.0, 30.0)
PREVIEW_DELAY       = (5.0, 10.0)
PRIVATE_MIN_MEMBERS = int(os.environ.get("PRIVATE_MIN_MEMBERS", "20"))
PEERFLOOD_PAUSE_H     = 48
FLOODWAIT_PAUSE_MIN_H = 6
FLOODWAIT_PAUSE_MAX_H = 48
LOCK_WINDOW_MIN = 25

SB_URL   = os.environ.get("SUPABASE_URL", "")
SB_KEY   = os.environ.get("SUPABASE_KEY", "")
API_ID   = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")
RUNNER   = os.environ.get("RUNNER", "github-actions")
DISPATCHED_BY = os.environ.get("DISPATCHED_BY", "") or None

GENERIC_BLOCKLIST = {
    "android", "chatgpt", "chatgptapp", "cultureamp", "discord", "github",
    "mailforspam", "mattythetechy", "mithemesofficial", "primevue", "source",
    "telegram", "username", "spotify", "gmail", "notion", "openai", "claude_ai",
    "xai", "gemini", "netflix", "steam", "primevideo", "apple", "microsoft",
    "google", "youtube", "whatsapp", "facebook", "instagram", "tiktok",
}
TG_RESERVED_PATHS = {
    "joinchat", "share", "addstickers", "addtheme", "addemoji", "addlist",
    "proxy", "socks", "iv", "login", "contact", "premium", "giftcode", "ton",
    "confirmphone", "setlanguage", "boost", "c",
}
COMMERCIAL_WORDS = re.compile(
    r"shop|store|market|seller|resell|premium|key|account|acc\b|subscri|gift|card|"
    r"vpn|topup|top.?up|donat|license|token|verify|checker|stock|cheap|price|"
    r"магазин|продаж|подписк|аккаунт|ключ|дешев|пополн|"
    r"متجر|بيع|اشتراك|حساب|رصيد|شحن|ضمان|توثيق|توكن|كروت|بطاق|تحويل|سعر|ارخص|أرخص|"
    r"toko|jual|murah|game|soft|ai\b", re.I)

# ---------------- regex bank (منطق C3 المجرَّب — نفس القواعد) ----------------
R_ADDED   = re.compile(r'(?:➕\s*)?[Aa]dded:\s*(\d+)')
R_STOCK   = re.compile(r'(?:📦|✅)?\s*(?:Current stock|stock|Stock):\s*(\d+)|(\d+)\s*items? available')
R_PRICE_USD  = re.compile(r'(?:Unit price|Price|💰 Price|💵 Unit price):\s*\$?([\d,]+\.?\d*)\s*(USDT|USD)?(?!\s*[đ₫d])', re.I)
R_PRICE_USDT = re.compile(r'Price:\s*([\d,]+\.?\d*)\s*USDT', re.I)
R_BULK    = re.compile(r'[•\-]\s*(\d+)\+\s*(?:units?|items?)?\s*(?:→|->|=|:)\s*\$?([\d.]+)\s*(USDT)?', re.I)
R_BULK2   = re.compile(r'[Bb]uy\s+(\d+)\s*[+\-–—]?\s*(?:units?|items?)?\s*(?:→|->|=|:)?\s*\$?([\d.]+)', re.I)
R_WARRANTY = re.compile(r'(full warranty|without warranty|no warranty|warranty[^,\n]{0,20}|\(W\d+D\)|\(FW\)|\(NW\)|ضمان[^\n,]{0,40}|استبدال[^\n,]{0,40}|استرجاع[^\n,]{0,40}|تعويض[^\n,]{0,40}|replacement[^\n,]{0,30}|refund[^\n,]{0,30})', re.I)
R_DURATION = re.compile(r'(\d+)\s*(M\b|Months?\b|Days?\b|D\b|Y\b|Years?\b|شهر|أشهر|يوم|أيام|سنة|سنوات)', re.I)
R_PAY     = re.compile(r'(USDT|TRC20|BEP20|PayPal|Payeer|Perfect Money|Binance|BTC|Bitcoin|Litecoin|Visa|Mastercard|محفظة|كريبتو|دفع)', re.I)
R_MINORD  = re.compile(r'(min(?:imum)?\.?\s*(?:order|purchase|qty|quantity)|MOQ|الحد الأدنى)', re.I)
R_HANDLE  = re.compile(r'@([A-Za-z][A-Za-z0-9_]{3,31})\b')
R_INVITE  = re.compile(r'(?:telegram\.me|t\.me)/(?:joinchat/|\+)([A-Za-z0-9_\-]{8,80})', re.I)
R_TGLINK  = re.compile(r'(?:telegram\.me|t\.me)/([A-Za-z][A-Za-z0-9_]{2,31})\b', re.I)
EMOJI     = re.compile(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]')

stats = {"channels": 0, "new_messages": 0, "prices": 0, "statements": 0,
         "new_handles": 0, "invites_found": 0, "joins_ok": 0, "joins_private": 0,
         "join_skipped": 0, "awaiting": 0, "approved_executed": 0,
         "alerts": 0, "errors": []}

# ---------------- supabase helpers ----------------
def sb(path, payload=None, method="POST", prefer="return=minimal"):
    req = urllib.request.Request(
        f"{SB_URL}/rest/v1/{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY,
                 "Content-Type": "application/json", "Prefer": prefer}, method=method)
    return urllib.request.urlopen(req, timeout=90)

def sb_rows(path):
    r = sb(path, method="GET", prefer="count=none")
    return json.loads(r.read().decode())

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def iso_minus_minutes(m):
    return (datetime.now(timezone.utc) - timedelta(minutes=m)).strftime("%Y-%m-%dT%H:%M:%SZ")

_settings_cache = {}

def load_settings():
    global _settings_cache
    try:
        _settings_cache = {s["key"]: s["value"] for s in sb_rows("settings?select=key,value&limit=500")}
    except Exception:
        _settings_cache = {}

def get_setting(key):
    return _settings_cache.get(key)

def set_setting(key, value):
    _settings_cache[key] = value
    sb("settings?on_conflict=key", {"key": key, "value": value, "updated_at": now_iso(),
                                     "updated_by": "monitor"},
       prefer="resolution=merge-duplicates,return=minimal")

def setting_int(key, default):
    v = get_setting(key)
    try:
        return int(v) if v is not None else default
    except (TypeError, ValueError):
        return default

def disc_path(h):
    return "discoveries?handle=eq." + _urlq(h, safe="")

def mask(key):
    return "+" + ("*" * max(len(key) - 4, 0)) + key[-4:]

def audit(action, entity=None, entity_id=None, details=None):
    try:
        sb("audit_log", {"actor": "monitor", "action": action, "entity": entity,
                         "entity_id": str(entity_id) if entity_id is not None else None,
                         "details": details})
    except Exception:
        pass

def raise_alert(severity, category, title, message=None, entity=None, entity_id=None):
    """تنبيه مع منع تكرار بسيط: فئة واحدة كل 12 ساعة كحد أقصى لغير الحرج."""
    try:
        if severity != "critical":
            since = (datetime.now(timezone.utc) - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
            recent = sb_rows(f"alerts?category=eq.{category}&created_at=gte.{since}&select=id&limit=1")
            if recent:
                return
        sb("alerts", {"severity": severity, "category": category, "title": title,
                      "message": (message or "")[:500], "entity": entity,
                      "entity_id": str(entity_id) if entity_id is not None else None})
        stats["alerts"] += 1
    except Exception:
        pass

# ---------------- extraction (منطق C3 المجرَّب) ----------------
def parse_message(text):
    t = text or ""
    if not t.strip():
        return [], []
    obs_rows, st_rows = [], []
    added = R_ADDED.search(t)
    stock = R_STOCK.search(t)
    price = R_PRICE_USD.search(t) or R_PRICE_USDT.search(t)
    if (added or stock) and price:
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        prod = EMOJI.sub("", lines[0]).strip(" |•-–—")
        prod = re.sub(r'^(New Stock Alert!?|restocked!?.*|has been.*)$', "", prod).strip()
        dur = R_DURATION.search(prod) or R_DURATION.search(t)
        cur = (price.group(2) or ("USD" if "$" in t else "USDT"))
        pval = float(price.group(1).replace(",", ""))
        if pval > 500 and ("đ" in t or "₫" in t):
            alt = re.search(r'\$([\d.]+)', t)
            if alt:
                pval = float(alt.group(1))
            elif pval > 5000:
                return [], []
        def mk(p, c, unit):
            return {"product": prod[:120], "price": p, "currency": c or cur,
                    "unit": unit, "raw_text": t[:800]}
        obs_rows.append(mk(pval, cur, dur.group(0) if dur else None))
        for a, b, c in R_BULK.findall(t):
            obs_rows.append(mk(float(b), c or cur, f"bulk {a}+"))
        for a, b in R_BULK2.findall(t):
            obs_rows.append(mk(float(b), None, f"bulk {a}+"))
        obs_rows = obs_rows[:7]
    if R_WARRANTY.search(t) and not obs_rows and len(t) > 40:
        st_rows.append({"kind": "warranty", "text": t[:600]})
    pays = set(p.lower() for p in R_PAY.findall(t))
    if pays and (R_MINORD.search(t) or "warranty" in t.lower() or "ضمان" in t):
        st_rows.append({"kind": "payment", "text": t[:600]})
    if R_MINORD.search(t):
        st_rows.append({"kind": "min_order", "text": t[:400]})
    return obs_rows, st_rows

def classify(ent):
    from telethon.tl.types import User
    if isinstance(ent, User):
        return ("bot" if ent.bot else "user"), (ent.first_name or "")
    if getattr(ent, "broadcast", False):
        return "channel", (ent.title or "")
    return "group", (ent.title or "")

def extract_links(m, text):
    from telethon.tl.types import MessageEntityTextUrl, MessageEntityUrl
    blobs = [text or ""]
    try:
        for ent in (m.entities or []):
            if isinstance(ent, MessageEntityTextUrl):
                blobs.append(ent.url or "")
            elif isinstance(ent, MessageEntityUrl):
                blobs.append((text or "")[ent.offset:ent.offset + ent.length])
    except Exception:
        pass
    try:
        for row in (m.buttons or []):
            for b in row:
                u = getattr(b, "url", None)
                if u:
                    blobs.append(u)
    except Exception:
        pass
    invites, handles = set(), set()
    for b in blobs:
        for h in R_INVITE.findall(b):
            invites.add(h)
        for h in R_TGLINK.findall(b):
            if h.lower() not in TG_RESERVED_PATHS:
                handles.add(h)
    return invites, handles

async def jitter(lo_hi):
    import asyncio
    await asyncio.sleep(random.uniform(*lo_hi))

# ---------------- main ----------------
async def main():
    from telethon import TelegramClient, errors as tg_errors
    from telethon.sessions import StringSession

    # 1) قفل التشغيل — لا تشغيلين متزامنين (حماية الجلسة)
    active = sb_rows(f"runs?finished_at=is.null&started_at=gte.{iso_minus_minutes(LOCK_WINDOW_MIN)}&select=id")
    if active:
        print(f"LOCK: run #{active[0]['id']} still active — aborting to protect session")
        return

    load_settings()
    # سياسات قابلة للضبط من لوحة المالك (تفضيل settings على env)
    join_budget     = setting_int("join_budget", TOTAL_JOIN_BUDGET)
    private_cap     = setting_int("private_join_cap", PRIVATE_JOIN_CAP)
    join_ceiling    = setting_int("join_total_ceiling", JOIN_TOTAL_CEILING)
    time_budget     = setting_int("time_budget_s", TIME_BUDGET_S)
    first_scan_cap  = setting_int("first_scan_cap", FIRST_SCAN_CAP)
    delta_cap       = setting_int("delta_cap", DELTA_CAP)
    print(f"policy: budget={join_budget} private_cap={private_cap} "
          f"ceiling={join_ceiling} scan_budget={time_budget}s "
          f"(settings-overridable from owner console)")

    r = sb("runs?select=id", {"runner": RUNNER, "started_at": now_iso(),
                              "dispatched_by": DISPATCHED_BY},
           prefer="return=representation")
    run_id = json.loads(r.read().decode())[0]["id"]
    print(f"=== MEC price-monitor v3 run #{run_id} @ {now_iso()} ({RUNNER}"
          + (f", by owner console" if DISPATCHED_BY else "") + ") ===")
    t0 = time.time()

    # 0) مزامنة مزودي API (معزولة تمامًا عن مسار تلغرام — فشل أي مزود لا يكسر الدورة)
    try:
        from providers.base import sync_all_providers
        psum = sync_all_providers(run_trigger="scheduled" if not DISPATCHED_BY else "manual")
        for s in psum:
            print(f"  [provider] {s.get('code')}: {s.get('status')}"
                  + (f" items={s.get('items')} new={s.get('new')} ms={s.get('ms')}" if s.get('status') == 'success' else ''))
    except Exception as e:
        print(f"  [provider] engine error (isolated, cycle continues): {type(e).__name__}: {e}")

    # 0.5) مطابقة المنتجات عبر المزودين (قواعد حتمية — تعمل على بيانات القاعدة فقط)
    try:
        from providers.matching import run_matching
        m = run_matching()
        warn = "" if m.get("ok") else f" warn={str(m.get('write_back_error') or m.get('benchmark_error'))[:80]}"
        print(f"  [match] benchmarks={m.get('benchmarks')} comparable={m.get('comparable')} "
              f"matched={m.get('matched')}/{m.get('rows')} ms={m.get('ms')}{warn}")
    except Exception as e:
        print(f"  [match] engine error (isolated, cycle continues): {type(e).__name__}: {e}")


    sess_env = os.environ.get("TG_SESSION")
    local = "/home/z/my-project/research/tg_si/tg_session"
    if sess_env:
        session = StringSession(sess_env)
    elif os.path.exists(local) or os.path.exists(local + ".session"):
        session = local
    else:
        raise SystemExit("no session (TG_SESSION env or local file missing)")

    client = TelegramClient(session, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        raise SystemExit("SESSION NOT AUTHORIZED")
    me = await client.get_me()
    print(f"session ok: {me.first_name} ({me.id})")

    # 2) المسح التفاضلي الدوّار
    channels = sb_rows(
        "tg_channels?joined=eq.true&select=tg_id,username,title,kind,last_msg_id"
        "&order=last_scanned.asc.nullsfirst,tg_id.asc&limit=800")
    print(f"channels to scan: {len(channels)} (rotated: least-recently-scanned first)")
    known_handles = {c["username"].lower() for c in channels if c.get("username")}
    known_handles |= {d["handle"].lower() for d in sb_rows("discoveries?select=handle&limit=5000")}
    mention_counter = {}

    for ch in channels:
        if time.time() - t0 > time_budget:
            print(f"scan budget reached — deferring remaining channels to next run")
            break
        uname = ch.get("username") or str(ch["tg_id"])
        sp = get_setting(f"scan_pause_{ch['tg_id']}")
        if sp and sp > now_iso():
            continue
        last = ch.get("last_msg_id") or 0
        try:
            try:
                ent = await client.get_entity(ch["tg_id"])
            except Exception:
                ent = await client.get_entity(uname)
            new_rows, st_rows = [], []
            max_id = last
            if last == 0:
                msgs = client.iter_messages(ent, limit=first_scan_cap)
            else:
                msgs = client.iter_messages(ent, min_id=last, limit=delta_cap, reverse=True)
            disc_new = {}
            async for m in msgs:
                max_id = max(max_id, m.id)  # المؤشر يتقدم لكل رسالة (حتى media-only) — منع إعادة مسح القنوات الميتة كل دورة
                if not m.message or m.out:
                    continue
                text = m.message
                stats["new_messages"] += 1
                obs, sts = parse_message(text)
                iso = m.date.isoformat() if m.date else None
                for o in obs:
                    o.update({"channel_id": ch["tg_id"], "username": uname,
                              "message_id": m.id, "posted_at": iso})
                new_rows.extend(obs)
                for s in sts:
                    s.update({"channel_id": ch["tg_id"], "message_id": m.id, "posted_at": iso})
                st_rows.extend(sts)
                for h in R_HANDLE.findall(text):
                    h = h.lower()
                    if h not in known_handles:
                        mention_counter[h] = mention_counter.get(h, 0) + 1
                        disc_new[h] = "handle"
                iv_hashes, url_handles = extract_links(m, text)
                for h in url_handles:
                    h = h.lower()
                    if h not in known_handles:
                        mention_counter[h] = mention_counter.get(h, 0) + 1
                        disc_new[h] = "handle"
                for iv in iv_hashes:
                    k = "+" + iv.lower()
                    if k not in known_handles:
                        mention_counter[k] = mention_counter.get(k, 0) + 1
                        disc_new[k] = "invite"
                        stats["invites_found"] += 1
            if max_id > last:
                sb("tg_channels?tg_id=eq." + str(ch["tg_id"]),
                   {"last_msg_id": max_id, "last_scanned": now_iso(), "updated_at": now_iso()},
                   method="PATCH")
            else:
                sb("tg_channels?tg_id=eq." + str(ch["tg_id"]),
                   {"last_scanned": now_iso(), "updated_at": now_iso()}, method="PATCH")
            if new_rows:
                try:
                    sb("price_observations?on_conflict=channel_id,message_id,product,price,currency",
                       new_rows, prefer="resolution=merge-duplicates,return=minimal")
                    stats["prices"] += len(new_rows)
                except Exception as e:
                    stats["errors"].append(f"{uname}: obs {str(e)[:50]}")
            if st_rows:
                try:
                    sb("statements?on_conflict=channel_id,message_id,kind,text", st_rows,
                       prefer="resolution=merge-duplicates,return=minimal")
                    stats["statements"] += len(st_rows)
                except Exception as e:
                    stats["errors"].append(f"{uname}: stmt {str(e)[:50]}")
            if disc_new:
                sb("discoveries?on_conflict=handle",
                   [{"handle": k, "seen_in": ch["tg_id"], "status": "pending", "kind": kd}
                    for k, kd in sorted(disc_new.items())],
                   prefer="resolution=merge-duplicates,return=minimal")
                stats["new_handles"] += sum(1 for k in disc_new.values() if k == "handle")
            stats["channels"] += 1
            print(f"  [{stats['channels']:3d}] {uname[:28]:30s} +{len(new_rows):3d} prices (last_id={max_id})")
        except tg_errors.FloodWaitError as e:
            wait = min(e.seconds, 240)
            pause = (datetime.now(timezone.utc)
                     + timedelta(seconds=min(e.seconds, 21600) + 60)).strftime("%Y-%m-%dT%H:%M:%SZ")
            set_setting(f"scan_pause_{ch['tg_id']}", pause)
            print(f"  FLOOD {uname}: {e.seconds}s -> sleep {wait}s (paused until {pause})")
            await client.disconnect(); time.sleep(wait); await client.connect()
        except Exception as e:
            stats["errors"].append(f"{uname}: {type(e).__name__} {str(e)[:40]}")
        await jitter(SCAN_DELAY)

    # 3) الانضمام المنضبط (عام تلقائي · خاص بموافقة المالك)
    print("--- join phase (disciplined · private = owner-approval-gated) ---")
    pause_until = get_setting("join_pause_until")
    if pause_until and pause_until > now_iso():
        print(f"  CIRCUIT-BREAKER active until {pause_until} "
              f"({get_setting('join_pause_reason') or 'n/a'}) — joins suspended")
    elif len(channels) >= join_ceiling:
        print(f"  CEILING reached ({len(channels)}/{join_ceiling}) — joins suspended")
    else:
        budget = join_budget
        private_used = 0
        stop_joins = False

        def pause_hours(h, reason):
            h = max(0.05, min(h, FLOODWAIT_PAUSE_MAX_H))
            until = (datetime.now(timezone.utc) + timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
            set_setting("join_pause_until", until)
            set_setting("join_pause_reason", reason)
            raise_alert("critical", "breaker",
                        "قاطع أمان: تعليق الانضمام",
                        f"{reason} — الانضمامات معلقة حتى {until} (تلقائي). "
                        "يمكن للمالك رفعه من الإعدادات بعد فهم السبب.")
            audit("monitor.breaker", "settings", "join_pause_until", {"reason": reason, "until": until})
            print(f"  CIRCUIT-BREAKER: joins paused until {until} ({reason})")

        async def preview_private(key):
            """معاينة قراءةً فقط. key=hash (بلا +). يعيد (verdict, ent, title, members, err)."""
            from telethon.tl.functions.messages import CheckChatInviteRequest
            from telethon.tl.types import ChatInviteAlready
            try:
                prev = await client(CheckChatInviteRequest(key))
            except Exception as e:
                nm = type(e).__name__
                if nm in ("InviteHashExpiredError", "InviteHashInvalidError", "InviteHashEmptyError"):
                    return ("expired", None, None, 0, nm)
                return ("preview_fail", None, None, 0, nm + " " + str(e)[:50])
            if isinstance(prev, ChatInviteAlready):
                return ("already", prev.chat, getattr(prev.chat, "title", ""), 0, None)
            title = getattr(prev, "title", "") or ""
            members = getattr(prev, "participants_count", 0) or 0
            if getattr(prev, "scam", False) or getattr(prev, "fake", False):
                return ("reject", None, title, members, "Telegram-flagged scam/fake")
            if not (getattr(prev, "broadcast", False) or getattr(prev, "megagroup", False)):
                return ("reject", None, title, members, f"not channel/group type (members={members})")
            if members < PRIVATE_MIN_MEMBERS:
                return ("reject", None, title, members, f"too small ({members}<{PRIVATE_MIN_MEMBERS})")
            if getattr(prev, "request_needed", False):
                return ("request_needed", None, title, members, None)
            return ("gated_ok", None, title, members, None)

        async def join_private(key):
            """تنفيذ الانضمام (فقط لما اعتمده المالك). يعيد (verdict, ent, title, err)."""
            from telethon.tl.functions.messages import ImportChatInviteRequest
            from telethon.tl.types import ChatInvitePeek
            try:
                res = await client(ImportChatInviteRequest(key))
                ent = None
                if isinstance(res, ChatInvitePeek):
                    ent = res.chat
                for c in (getattr(res, "chats", None) or []):
                    if getattr(c, "broadcast", False) or getattr(c, "megagroup", False):
                        ent = c
                        break
                return ("joined", ent, getattr(ent, "title", ""), None)
            except Exception as e:
                return ("error", None, None, type(e).__name__ + " " + str(e)[:60])

        def register_channel(ent, kind_key, title, uname=None):
            try:
                sb("tg_channels?on_conflict=tg_id",
                   {"tg_id": ent.id, "username": uname, "title": title, "kind": kind_key,
                    "relevance": "new", "joined": True, "joined_at": now_iso(),
                    "updated_at": now_iso()},
                   prefer="resolution=merge-duplicates,return=minimal")
            except Exception as e:
                stats["errors"].append(f"register {str(ent.id)}: {str(e)[:40]}")

        # 3-أ) المعتمدون من المالك أولًا (تنفيذ قرارات الاعتماد)
        approved = sb_rows("discoveries?status=eq.approved&kind=eq.invite&select=handle,kind&limit=30")
        print(f"  owner-approved private invites to execute: {len(approved)}")
        for d in approved:
            if budget <= 0 or private_used >= private_cap or stop_joins:
                break
            if time.time() - t0 > JOIN_DEADLINE_S:
                break
            h = d["handle"]
            key = h[1:]
            try:
                verdict, ent, title, err = await join_private(key)
            except tg_errors.FloodWaitError as e:
                pause_hours(max(2 * e.seconds / 3600.0, FLOODWAIT_PAUSE_MIN_H),
                            f"FloodWait {e.seconds}s on approved private join")
                stop_joins = True
                break
            except Exception as e:
                if type(e).__name__ == "PeerFloodError":
                    pause_hours(PEERFLOOD_PAUSE_H, "PeerFlood on approved private join")
                    stop_joins = True
                    break
                stats["errors"].append(f"join-approved {mask(key)}: {type(e).__name__}")
                await jitter(PREVIEW_DELAY)
                continue
            if verdict == "joined":
                if ent is not None:
                    cls, _ = classify(ent)
                    register_channel(ent, cls, title or (ent.title or ""))
                    print(f"  JOINED (owner-approved) {mask(key)} -> {cls}: {(title or '')[:44]}")
                else:
                    print(f"  JOINED (owner-approved) {mask(key)} (entity unresolved — reconcile next run)")
                sb(disc_path(h), {"status": "joined"}, method="PATCH")
                budget -= 1; private_used += 1
                stats["joins_ok"] += 1; stats["joins_private"] += 1; stats["approved_executed"] += 1
                audit("tg.join", "discoveries", h,
                      {"mode": "owner-approved", "title": (title or "")[:80], "run": run_id})
            elif verdict == "error":
                nm = (err or "").split(" ")[0]
                if nm in ("InviteHashExpiredError", "InviteHashInvalidError"):
                    sb(disc_path(h), {"status": "expired", "last_error": err[:120]}, method="PATCH")
                    continue
                if nm == "UserAlreadyParticipantError":
                    sb(disc_path(h), {"status": "joined"}, method="PATCH")
                    continue
                if nm == "JoinRequestSentError":
                    sb(disc_path(h), {"status": "request_sent"}, method="PATCH")
                    continue
                if nm in ("ChannelPrivateError", "UserBannedInChannelError"):
                    sb(disc_path(h), {"status": "rejected", "last_error": err[:120]}, method="PATCH")
                    continue
                stats["errors"].append(f"join-approved {mask(key)}: {err[:60] if err else 'unknown'}")
                sb(disc_path(h), {"last_error": (err or "")[:120]}, method="PATCH")
            await jitter(JOIN_DELAY)

        # 3-ب) طابور الدعوات الخاصة: معاينة → بوابات جودة → بانتظار المالك
        invites = sb_rows("discoveries?status=eq.pending&kind=eq.invite&select=handle&limit=40")
        print(f"  private invites to screen (preview-only, then await owner): {len(invites)}")
        for d in invites:
            if stop_joins or time.time() - t0 > JOIN_DEADLINE_S:
                break
            h = d["handle"]
            key = h[1:]
            try:
                verdict, ent, title, members, err = await preview_private(key)
            except Exception as e:
                stats["errors"].append(f"preview {mask(key)}: {type(e).__name__}")
                await jitter(PREVIEW_DELAY)
                continue
            if verdict == "already":
                if ent is not None and (getattr(ent, "broadcast", False) or getattr(ent, "megagroup", False)):
                    register_channel(ent, "channel" if getattr(ent, "broadcast", False) else "group",
                                     title or (ent.title or ""))
                sb(disc_path(h), {"status": "joined"}, method="PATCH")
                print(f"  already-member private {mask(key)} — reconciled")
            elif verdict == "gated_ok":
                sb(disc_path(h),
                   {"status": "awaiting_approval", "title": (title or "")[:120],
                    "members": members, "preview_at": now_iso()}, method="PATCH")
                stats["awaiting"] += 1
                print(f"  AWAITING OWNER: {mask(key)} -> {(title or '')[:44]} ({members} members)")
            elif verdict == "expired":
                sb(disc_path(h), {"status": "expired"}, method="PATCH")
                print(f"  invite expired {mask(key)} — closed permanently")
            elif verdict == "request_needed":
                sb(disc_path(h), {"status": "request_needed", "title": (title or "")[:120],
                                  "members": members, "preview_at": now_iso()}, method="PATCH")
                print(f"  skip {mask(key)}: requires admin approval — no join request sent (anti-spam policy)")
            elif verdict == "reject":
                sb(disc_path(h), {"status": "rejected", "title": (title or "")[:120],
                                  "members": members, "last_error": err}, method="PATCH")
                stats["join_skipped"] += 1
                print(f"  rejected {mask(key)}: {err}")
            elif verdict == "preview_fail":
                stats["errors"].append(f"preview {mask(key)}: {err[:60] if err else ''}")
            await jitter(PREVIEW_DELAY)

        # 3-ج) المقابض العامة (تلقائي كما اعتُمد للمالك سابقًا)
        handles = sb_rows("discoveries?status=eq.pending&kind=eq.handle&select=handle&limit=60")
        random.shuffle(handles)
        for d in handles:
            if budget <= 0 or stop_joins or time.time() - t0 > JOIN_DEADLINE_S:
                break
            h = d["handle"]
            if h.lower() in GENERIC_BLOCKLIST:
                sb(disc_path(h), {"status": "rejected"}, method="PATCH")
                continue
            try:
                ent = await client.get_entity(h)
            except Exception:
                try:
                    sb(disc_path(h), {"status": "not_found"}, method="PATCH")
                except Exception:
                    pass
                continue
            cls, title = classify(ent)
            if cls not in ("channel", "group"):
                sb(disc_path(h), {"status": "rejected"}, method="PATCH")
                continue
            if not (COMMERCIAL_WORDS.search(title or "") or mention_counter.get(h, 0) >= 5):
                sb(disc_path(h), {"status": "rejected"}, method="PATCH")
                stats["join_skipped"] += 1
                continue
            try:
                from telethon.tl.functions.channels import JoinChannelRequest
                await client(JoinChannelRequest(h))
                register_channel(ent, cls, title, uname=h)
                sb(disc_path(h), {"status": "joined"}, method="PATCH")
                budget -= 1
                stats["joins_ok"] += 1
                print(f"  JOINED public {h} ({title[:40]})")
                audit("tg.join", "discoveries", h,
                      {"mode": "auto-public", "title": (title or "")[:80], "run": run_id})
            except tg_errors.UserAlreadyParticipantError:
                register_channel(ent, cls, title, uname=h)
                sb(disc_path(h), {"status": "joined"}, method="PATCH")
                budget -= 1
            except tg_errors.FloodWaitError as e:
                pause_hours(max(2 * e.seconds / 3600.0, FLOODWAIT_PAUSE_MIN_H),
                            f"FloodWait {e.seconds}s on public join")
                break
            except Exception as e:
                if type(e).__name__ == "PeerFloodError":
                    pause_hours(PEERFLOOD_PAUSE_H, "PeerFlood on public join")
                    break
                stats["errors"].append(f"join {h}: {type(e).__name__} {str(e)[:40]}")
            await jitter(JOIN_DELAY)

    # 4) إغلاق السجل + تنبيهات الجودة
    if stats["errors"]:
        raise_alert("warning", "monitor",
                    f"دورة #{run_id}: {len(stats['errors'])} أخطاء غير حرجة",
                    json.dumps(stats["errors"][:8], ensure_ascii=False))
    if stats["awaiting"] > 0:
        raise_alert("info", "monitor",
                    f"{stats['awaiting']} انضمامًا خاصًا بانتظار موافقتك",
                    "راجع قسم الاكتشافات والموافقات في لوحة التحكم واعتمد أو ارفض.")
    sb("runs?id=eq." + str(run_id),
       {"finished_at": now_iso(), "channels_scanned": stats["channels"],
        "new_messages": stats["new_messages"], "prices_added": stats["prices"],
        "new_handles": stats["new_handles"], "invites_found": stats["invites_found"],
        "joins_ok": stats["joins_ok"], "joins_private": stats["joins_private"],
        "errors": json.dumps(stats["errors"][:20], ensure_ascii=False)},
       method="PATCH")
    # 5) تحديث مزود تلغرام في سجل المزودين الموحد (المراقب هو محرك مزامنته)
    try:
        sb("providers?on_conflict=code", {
            "code": "telegram_ecosystem",
            "name": f"منظومة تلغرام ({stats['channels']} مصدرًا مراقَبًا)",
            "kind": "telegram", "status": "SYNC_ACTIVE",
            "sync_interval_min": 30,
            "last_sync_at": now_iso(), "last_ok_at": now_iso(),
            "updated_at": now_iso(),
        }, prefer="return=minimal,resolution=merge-duplicates")
    except Exception as e:
        print(f"[provider-registry] telegram row update failed (isolated): {e}")
    print(f"=== done in {int(time.time()-t0)}s: {stats['channels']} ch · "
          f"+{stats['new_messages']} msg · +{stats['prices']} prices · "
          f"+{stats['new_handles']} handles · +{stats['invites_found']} invites · "
          f"{stats['joins_ok']} joins ({stats['joins_private']} private, "
          f"{stats['approved_executed']} owner-approved) · "
          f"{stats['awaiting']} awaiting owner · +{stats['alerts']} alerts ===")
    if stats["errors"]:
        print("errors:", stats["errors"][:5])
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except SystemExit as e:
        raise_alert("critical", "monitor", "فشل دورة المراقب", str(e)[:400])
        raise
    except Exception as e:
        raise_alert("critical", "monitor", "تعطل دورة المراقب", f"{type(e).__name__}: {str(e)[:400]}")
        raise
