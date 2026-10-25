"""HTTP-Server und API. Läuft ohne Zusatzpakete (nur Python-Standardbibliothek).

Grundregel für die Trennung der Konten: Die Person kommt *ausschließlich* aus der Sitzung (Cookie).
Keine Route nimmt eine fremde Benutzer-ID entgegen – außer den Verwaltungsrouten, die Admin-Rechte prüfen.
"""
import gzip
import hashlib
import json
import mimetypes
import os
import re
import secrets
import ssl
import sys
import time
import traceback
from datetime import date, timedelta
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import auth, catalog, db, notify, planner
from .catalog import RBY, INGS

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
STATIC = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/app.css": "app.css",
          "/manifest.webmanifest": "manifest.webmanifest", "/icon.svg": "icon.svg"}
MAX_BODY = 512 * 1024
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'")


class ApiError(Exception):
    def __init__(self, status, message, code=None):
        super().__init__(message)
        self.status, self.message, self.code = status, message, code


class Settings:
    secure_cookies = False
    trust_proxy = False
    setup_code = None


SETTINGS = Settings()
ROUTES = []


def route(method, pattern, auth_required=True, admin=False, allow_pw_change=False):
    rx = re.compile("^" + pattern + "$")

    def deco(fn):
        ROUTES.append((method, rx, fn, auth_required, admin, allow_pw_change))
        return fn
    return deco


# ---------- Hilfen ----------
def user_public(u):
    return {"id": u["id"], "username": u["username"], "display_name": u["display_name"], "is_admin": bool(u["is_admin"]),
            "must_change_pw": bool(u["must_change_pw"]),
            "email": u["email"], "email_verified": bool(u["email_verified"]),
            "phone": u["phone"], "phone_masked": notify.mask_phone(u["phone"]), "phone_verified": bool(u["phone_verified"])}


def load_profile(c, uid):
    return planner.normalize_profile(db.load_profile(c, uid) or {})


def save_profile(c, uid, S):
    db.save_profile(c, uid, planner.storable(S))


def load_rows(c, uid, a=None, b=None):
    if a and b:
        rs = c.all("SELECT date,slot,recipe_id,portions,cook_portions,leftover,cooked FROM plan WHERE user_id=? AND date>=? AND date<? ",
                   (uid, a, b))
    else:
        rs = c.all("SELECT date,slot,recipe_id,portions,cook_portions,leftover,cooked FROM plan WHERE user_id=?", (uid,))
    return [dict(r) for r in rs if r["recipe_id"] in RBY]


def parse_day(s, name="date"):
    try:
        return date.fromisoformat(str(s))
    except (TypeError, ValueError):
        raise ApiError(400, f"Ungültiges Datum ({name}).")


def get_slot(c, uid, ds, slot):
    row = c.one("SELECT date,slot,recipe_id,portions,cook_portions,leftover,cooked FROM plan WHERE user_id=? AND date=? AND slot=?",
                (uid, ds, slot))
    if not row:
        raise ApiError(404, "An diesem Platz ist nichts geplant.")
    return dict(row)


MAIN_SLOTS = ("mittag", "abend")


def neighbor_main(c, uid, row, direction):
    """Nächster/vorheriger Hauptmahlzeit-Platz (für Meal-Prep-Paare)."""
    d = planner.s2d(row["date"])
    cand = []
    for k in (-1, 0, 1):
        ds = planner.d2s(d + timedelta(days=k))
        for s in MAIN_SLOTS:
            cand.append((ds, s))
    cand.sort(key=lambda x: (x[0], planner.SLOT_ORDER[x[1]]))
    i = cand.index((row["date"], row["slot"]))
    rows = {(r["date"], r["slot"]): dict(r) for r in c.all(
        "SELECT date,slot,recipe_id,portions,cook_portions,leftover,cooked FROM plan WHERE user_id=? AND date>=? AND date<=? AND slot IN ('mittag','abend')",
        (uid, cand[0][0], cand[-1][0]))}
    j = i + direction
    while 0 <= j < len(cand):
        if cand[j] in rows:
            return rows[cand[j]]
        j += direction
    return None


def leftover_partner(c, uid, row):
    """Für eine Koch-Zeile mit doppelter Menge: die zugehörige Reste-Zeile (und umgekehrt)."""
    if row["slot"] == "frueh":
        return None
    if row["leftover"]:
        p = neighbor_main(c, uid, row, -1)
        return p if p and p["recipe_id"] == row["recipe_id"] and p["cook_portions"] > p["portions"] else None
    if row["cook_portions"] > row["portions"]:
        n = neighbor_main(c, uid, row, 1)
        return n if n and n["recipe_id"] == row["recipe_id"] and n["leftover"] else None
    return None


def state_payload(c, u):
    S = load_profile(c, u["id"])
    ex = S["_ex"]
    eligible = [r["id"] for r in catalog.RECIPES if planner.eligible(r, S, ex)]
    return {
        "user": user_public(u),
        "profile": planner.storable(S),
        "subst": S["_subst"],
        "eligible": eligible,
        "channels": {"email": notify.email_ready(c), "whatsapp": notify.whatsapp_ready(c)},
        "public_url": db.get_config(c, "public_url", ""),
        "today": date.today().isoformat(),
        "max_weeks": planner.MAX_WEEKS,
    }


def week_param(q):
    w = parse_day((q.get("week") or [date.today().isoformat()])[0], "week")
    return planner.monday(w)


# ---------- Anmeldung ----------
@route("GET", "/api/session", auth_required=False)
def r_session(h, c, u, body, q):
    has_users = c.one("SELECT 1 FROM users LIMIT 1") is not None
    out = {"authenticated": bool(u), "setup_required": not has_users,
           "registration": db.get_config(c, "registration", "closed")}
    if u:
        out.update(user=user_public(u), csrf=h.session["csrf"])
    return out


@route("POST", "/api/setup", auth_required=False)
def r_setup(h, c, u, body, q):
    if c.one("SELECT 1 FROM users LIMIT 1"):
        raise ApiError(403, "Die Einrichtung ist bereits abgeschlossen.")
    if auth.signup_ip_throttle.blocked(h.ip):
        raise ApiError(429, "Zu viele Versuche. Bitte später erneut versuchen.")
    auth.signup_ip_throttle.hit(h.ip)
    code = str(body.get("setup_code", "")).strip().upper()
    if not SETTINGS.setup_code or not secrets.compare_digest(code, SETTINGS.setup_code):
        raise ApiError(403, "Der Einrichtungscode stimmt nicht. Du findest ihn im Fenster, in dem der Server läuft.")
    with c.tx():
        uid = create_user(c, body, is_admin=True)
    SETTINGS.setup_code = None
    return h.login_response(c, uid)


@route("POST", "/api/register", auth_required=False)
def r_register(h, c, u, body, q):
    mode = db.get_config(c, "registration", "closed")
    if mode not in ("open", "invite"):
        raise ApiError(403, "Neue Konten legt die Verwaltung an. Bitte frag die Person, die den Wochenteller betreibt.")
    if auth.signup_ip_throttle.blocked(h.ip):
        raise ApiError(429, "Zu viele Registrierungen von diesem Gerät. Bitte später erneut versuchen.")
    invite = None
    if mode == "invite":
        code = str(body.get("invite", "")).strip().upper()
        invite = c.one("SELECT * FROM invites WHERE code_hash=? AND used_by IS NULL AND expires>?",
                       (auth.sha(code), time.time()))
        if not invite:
            auth.signup_ip_throttle.hit(h.ip)
            raise ApiError(403, "Der Einladungscode ist ungültig oder abgelaufen.")
    auth.signup_ip_throttle.hit(h.ip)
    with c.tx():
        uid = create_user(c, body)
        if invite:
            c.execute("UPDATE invites SET used_by=? WHERE code_hash=?", (uid, invite["code_hash"]))
    return h.login_response(c, uid)


def create_user(c, body, is_admin=False, must_change=False):
    username = str(body.get("username", "")).strip()
    display = str(body.get("display_name") or username).strip()[:40] or username
    pw = str(body.get("password", ""))
    err = auth.username_problem(username) or auth.password_problem(pw, username)
    if err:
        raise ApiError(400, err)
    if c.one("SELECT 1 FROM users WHERE username=?", (username,)):
        raise ApiError(409, "Dieser Benutzername ist schon vergeben.")
    cur = c.execute("INSERT INTO users(username,display_name,pw_hash,is_admin,must_change_pw,created_at) VALUES(?,?,?,?,?,?)",
                    (username, display, auth.hash_password(pw), 1 if is_admin else 0, 1 if must_change else 0, time.time()))
    uid = cur.lastrowid
    save_profile(c, uid, planner.fresh_profile())
    return uid


@route("POST", "/api/login", auth_required=False)
def r_login(h, c, u, body, q):
    if auth.login_ip_throttle.blocked(h.ip):
        raise ApiError(429, "Zu viele Fehlversuche von diesem Gerät. Bitte in 15 Minuten erneut versuchen.")
    username = str(body.get("username", "")).strip()[:64]
    pw = str(body.get("password", ""))[:200]
    row = c.one("SELECT * FROM users WHERE username=?", (username,))
    t = time.time()
    if row and row["locked_until"] > t:
        mins = int((row["locked_until"] - t) // 60) + 1
        raise ApiError(429, f"Dieses Konto ist nach mehreren Fehlversuchen für {mins} Minute(n) gesperrt.")
    ok = auth.verify_password(pw, row["pw_hash"] if row else auth._DUMMY_HASH) and row is not None
    if not ok or row["disabled"]:
        auth.login_ip_throttle.hit(h.ip)
        if row:
            failed = row["failed_logins"] + 1
            c.execute("UPDATE users SET failed_logins=?, locked_until=? WHERE id=?",
                      (failed, t + auth.lock_seconds(failed), row["id"]))
        raise ApiError(401, "Benutzername oder Passwort ist falsch.")
    c.execute("UPDATE users SET failed_logins=0, locked_until=0 WHERE id=?", (row["id"],))
    auth.login_ip_throttle.reset(h.ip)
    return h.login_response(c, row["id"])


@route("POST", "/api/logout", allow_pw_change=True)
def r_logout(h, c, u, body, q):
    auth.end_session(c, h.token)
    h.set_cookie("", expire=True)
    return {"ok": True}


# ---------- Konto ----------
@route("POST", "/api/account/password", allow_pw_change=True)
def r_password(h, c, u, body, q):
    if not auth.verify_password(str(body.get("current", "")), u["pw_hash"]):
        raise ApiError(400, "Das aktuelle Passwort stimmt nicht.")
    new = str(body.get("new", ""))
    err = auth.password_problem(new, u["username"])
    if err:
        raise ApiError(400, err)
    c.execute("UPDATE users SET pw_hash=?, must_change_pw=0 WHERE id=?", (auth.hash_password(new), u["id"]))
    auth.end_all_sessions(c, u["id"], except_token=h.token)
    return {"ok": True}


@route("PUT", "/api/account")
def r_account(h, c, u, body, q):
    name = str(body.get("display_name", "")).strip()[:40]
    if not name:
        raise ApiError(400, "Bitte gib einen Namen ein.")
    c.execute("UPDATE users SET display_name=? WHERE id=?", (name, u["id"]))
    return {"ok": True}


@route("POST", "/api/account/logout-others")
def r_logout_others(h, c, u, body, q):
    auth.end_all_sessions(c, u["id"], except_token=h.token)
    return {"ok": True}


@route("DELETE", "/api/account")
def r_delete_account(h, c, u, body, q):
    if not auth.verify_password(str(body.get("password", "")), u["pw_hash"]):
        raise ApiError(400, "Das Passwort stimmt nicht.")
    if u["is_admin"] and c.one("SELECT COUNT(*) n FROM users WHERE is_admin=1 AND disabled=0")["n"] <= 1:
        raise ApiError(400, "Du bist die einzige Verwaltung. Ernenne zuerst eine andere Person zur Verwaltung.")
    c.execute("DELETE FROM users WHERE id=?", (u["id"],))
    h.set_cookie("", expire=True)
    return {"ok": True}


# ---------- Kontakt bestätigen ----------
def start_verification(h, c, u, channel, target):
    code = auth.new_code()
    c.execute("INSERT INTO verify_codes(user_id,channel,target,code_hash,expires,attempts) VALUES(?,?,?,?,?,0) "
              "ON CONFLICT(user_id,channel) DO UPDATE SET target=excluded.target, code_hash=excluded.code_hash, "
              "expires=excluded.expires, attempts=0",
              (u["id"], channel, target, auth.sha(f"{u['id']}:{channel}:{code}"), time.time() + 900))
    subject, text, html_body = notify.code_message(code, "deine E-Mail-Adresse" if channel == "email" else "deine WhatsApp-Nummer")
    try:
        notify.check_limit(c, u["id"], "code")
        if channel == "email":
            notify.send_email(c, target, subject, text, html_body)
        else:
            notify.send_whatsapp(c, target, text)
    except notify.SendError as e:
        notify.log(c, u["id"], channel, "code", "failed", None, str(e))
        raise ApiError(502, str(e))
    notify.log(c, u["id"], channel, "code", "sent")


def finish_verification(c, u, channel, code):
    row = c.one("SELECT * FROM verify_codes WHERE user_id=? AND channel=?", (u["id"], channel))
    if not row or row["expires"] < time.time():
        raise ApiError(400, "Der Code ist abgelaufen. Bitte fordere einen neuen an.")
    if row["attempts"] >= 5:
        raise ApiError(429, "Zu viele falsche Eingaben. Bitte fordere einen neuen Code an.")
    c.execute("UPDATE verify_codes SET attempts=attempts+1 WHERE user_id=? AND channel=?", (u["id"], channel))
    if not secrets.compare_digest(row["code_hash"], auth.sha(f"{u['id']}:{channel}:{str(code).strip()}")):
        raise ApiError(400, "Der Code stimmt nicht.")
    col = "email" if channel == "email" else "phone"
    c.execute(f"UPDATE users SET {col}=?, {col}_verified=1 WHERE id=?", (row["target"], u["id"]))
    c.execute("DELETE FROM verify_codes WHERE user_id=? AND channel=?", (u["id"], channel))
    return {"ok": True}


@route("POST", "/api/contact/email")
def r_contact_email(h, c, u, body, q):
    try:
        email = notify.clean_email(body.get("email"))
    except ValueError as e:
        raise ApiError(400, str(e))
    start_verification(h, c, u, "email", email)
    return {"ok": True, "sent_to": email}


@route("POST", "/api/contact/email/verify")
def r_contact_email_verify(h, c, u, body, q):
    return finish_verification(c, u, "email", body.get("code", ""))


@route("DELETE", "/api/contact/email")
def r_contact_email_delete(h, c, u, body, q):
    c.execute("UPDATE users SET email=NULL, email_verified=0 WHERE id=?", (u["id"],))
    return {"ok": True}


@route("POST", "/api/contact/phone")
def r_contact_phone(h, c, u, body, q):
    if not notify.whatsapp_ready(c):
        raise ApiError(400, "WhatsApp-Versand ist auf diesem Server nicht aktiviert.")
    try:
        phone = notify.clean_phone(body.get("phone"), notify.whatsapp_config(c)["country_code"])
    except ValueError as e:
        raise ApiError(400, str(e))
    start_verification(h, c, u, "whatsapp", phone)
    return {"ok": True, "sent_to": notify.mask_phone(phone)}


@route("POST", "/api/contact/phone/verify")
def r_contact_phone_verify(h, c, u, body, q):
    return finish_verification(c, u, "whatsapp", body.get("code", ""))


@route("DELETE", "/api/contact/phone")
def r_contact_phone_delete(h, c, u, body, q):
    c.execute("UPDATE users SET phone=NULL, phone_verified=0 WHERE id=?", (u["id"],))
    return {"ok": True}


# ---------- Katalog & Profil ----------
_CATALOG_CACHE = {}


@route("GET", "/api/catalog")
def r_catalog(h, c, u, body, q):
    if "raw" not in _CATALOG_CACHE:
        raw = json.dumps(catalog.public_catalog(), ensure_ascii=False).encode()
        _CATALOG_CACHE["raw"] = raw
        _CATALOG_CACHE["etag"] = '"' + hashlib.sha256(raw).hexdigest()[:20] + '"'
    return RawJson(_CATALOG_CACHE["raw"], etag=_CATALOG_CACHE["etag"], cache="private, max-age=3600")


@route("GET", "/api/state")
def r_state(h, c, u, body, q):
    return state_payload(c, u)


@route("PUT", "/api/profile")
def r_profile(h, c, u, body, q):
    with c.tx():
        S = load_profile(c, u["id"])
        old_persons = S["persons"]
        for k, v in (body or {}).items():
            if k in planner.PROFILE_KEYS:
                S[k] = v
        S = planner.normalize_profile(planner.storable(S))
        save_profile(c, u["id"], S)
        if S["persons"] != old_persons:
            # künftige, noch nicht gekochte Mahlzeiten auf die neue Personenzahl umstellen
            c.execute("""UPDATE plan SET cook_portions = CASE WHEN cook_portions=0 THEN 0
                         ELSE ? * MAX(1, cook_portions / portions) END, portions=?
                         WHERE user_id=? AND cooked=0 AND date>=?""",
                      (S["persons"], S["persons"], u["id"], date.today().isoformat()))
    return state_payload(c, u)


@route("PUT", "/api/fridge")
def r_fridge(h, c, u, body, q):
    iid = str(body.get("id", ""))
    if iid not in INGS:
        raise ApiError(400, "Unbekannte Zutat.")
    try:
        qty = float(body.get("qty", 0))
    except (TypeError, ValueError):
        raise ApiError(400, "Ungültige Menge.")
    with c.tx():
        S = load_profile(c, u["id"])
        if qty <= 1e-6:
            S["fridge"].pop(iid, None)
        else:
            S["fridge"][iid] = min(qty, 1e6)
        save_profile(c, u["id"], S)
    return {"fridge": S["fridge"]}


@route("POST", "/api/recipes/rate")
def r_rate(h, c, u, body, q):
    rid = str(body.get("id", ""))
    if rid not in RBY:
        raise ApiError(404, "Unbekanntes Rezept.")
    with c.tx():
        S = load_profile(c, u["id"])
        for key in ("favorites", "hidden"):
            if key in body:
                lst = [x for x in S[key] if x != rid]
                if body[key]:
                    lst.append(rid)
                S[key] = lst
        if rid in S["hidden"]:
            S["favorites"] = [x for x in S["favorites"] if x != rid]
        save_profile(c, u["id"], S)
    return {"favorites": S["favorites"], "hidden": S["hidden"]}


# ---------- Plan ----------
@route("GET", "/api/plan")
def r_plan(h, c, u, body, q):
    a = parse_day((q.get("from") or [None])[0], "from")
    b = parse_day((q.get("to") or [None])[0], "to")
    if (b - a).days > 400:
        raise ApiError(400, "Zeitraum zu groß.")
    rows = load_rows(c, u["id"], a.isoformat(), b.isoformat())
    span = c.one("SELECT MIN(date) a, MAX(date) b FROM plan WHERE user_id=?", (u["id"],))
    return {"rows": planner.sort_rows(rows), "first": span["a"], "last": span["b"]}


@route("POST", "/api/plan/generate")
def r_generate(h, c, u, body, q):
    start = parse_day(body.get("start"), "start")
    try:
        weeks = int(body.get("weeks", 1))
    except (TypeError, ValueError):
        raise ApiError(400, "Ungültige Wochenanzahl.")
    if not 1 <= weeks <= planner.MAX_WEEKS:
        raise ApiError(400, f"Es lassen sich 1 bis {planner.MAX_WEEKS} Wochen planen.")
    days = body.get("days")
    if days is not None:
        try:
            days = int(days)
        except (TypeError, ValueError):
            raise ApiError(400, "Ungültige Anzahl Tage.")
        if not 1 <= days <= 7 * planner.MAX_WEEKS:
            raise ApiError(400, "Ungültige Anzahl Tage.")
    today = date.today()
    if start < today - timedelta(days=7) or start > today + timedelta(days=370):
        raise ApiError(400, "Der Start muss zwischen letzter Woche und nächstem Jahr liegen.")
    with c.tx():
        S = load_profile(c, u["id"])
        rows = load_rows(c, u["id"])
        new_rows, info = planner.generate(S, rows, start, weeks, today=today, days=days)
        if info.get("error"):
            raise ApiError(400, info["error"])
        end = start + timedelta(days=days or 7 * weeks)
        c.execute("DELETE FROM plan WHERE user_id=? AND cooked=0 AND date>=? AND date<?",
                  (u["id"], start.isoformat(), end.isoformat()))
        c.c.executemany("INSERT OR REPLACE INTO plan(user_id,date,slot,recipe_id,portions,cook_portions,leftover,cooked) VALUES(?,?,?,?,?,?,?,0)",
                        [(u["id"], r["date"], r["slot"], r["recipe_id"], r["portions"], r["cook_portions"], r["leftover"]) for r in new_rows])
        if not S["onboarded"]:
            S["onboarded"] = True
        if not days:
            S["horizon"] = weeks
        save_profile(c, u["id"], S)
    return {"ok": True, "info": info, "count": len(new_rows), "from": start.isoformat(), "to": end.isoformat()}


@route("POST", "/api/plan/clear")
def r_clear(h, c, u, body, q):
    a = parse_day(body.get("from"), "from")
    b = parse_day(body.get("to"), "to")
    c.execute("DELETE FROM plan WHERE user_id=? AND cooked=0 AND date>=? AND date<?", (u["id"], a.isoformat(), b.isoformat()))
    return {"ok": True}


def slot_args(body):
    ds = parse_day(body.get("date")).isoformat()
    slot = body.get("slot")
    if slot not in ("frueh", "mittag", "abend"):
        raise ApiError(400, "Ungültige Mahlzeit.")
    return ds, slot


def set_recipe(c, uid, row, rid):
    partner = leftover_partner(c, uid, row)
    c.execute("UPDATE plan SET recipe_id=? WHERE user_id=? AND date=? AND slot=?", (rid, uid, row["date"], row["slot"]))
    if partner:
        c.execute("UPDATE plan SET recipe_id=? WHERE user_id=? AND date=? AND slot=?", (rid, uid, partner["date"], partner["slot"]))


@route("POST", "/api/plan/swap")
def r_swap(h, c, u, body, q):
    ds, slot = slot_args(body)
    with c.tx():
        row = get_slot(c, u["id"], ds, slot)
        if row["cooked"]:
            raise ApiError(400, "Diese Mahlzeit ist schon gekocht.")
        S = load_profile(c, u["id"])
        rid = planner.pick_swap(S, load_rows(c, u["id"]), ds, slot, row["recipe_id"])
        if not rid:
            raise ApiError(400, "Es gibt kein anderes passendes Gericht.")
        set_recipe(c, u["id"], row, rid)
    return {"ok": True, "recipe_id": rid}


@route("POST", "/api/plan/set")
def r_set(h, c, u, body, q):
    ds, slot = slot_args(body)
    rid = str(body.get("recipe_id", ""))
    r = RBY.get(rid)
    if not r or (r["type"] == "f") != (slot == "frueh"):
        raise ApiError(400, "Dieses Rezept passt nicht zu dieser Mahlzeit.")
    with c.tx():
        S = load_profile(c, u["id"])
        existing = c.one("SELECT * FROM plan WHERE user_id=? AND date=? AND slot=?", (u["id"], ds, slot))
        if existing:
            if existing["cooked"]:
                raise ApiError(400, "Diese Mahlzeit ist schon gekocht.")
            set_recipe(c, u["id"], dict(existing), rid)
        else:
            c.execute("INSERT INTO plan(user_id,date,slot,recipe_id,portions,cook_portions,leftover,cooked) VALUES(?,?,?,?,?,?,0,0)",
                      (u["id"], ds, slot, rid, S["persons"], S["persons"]))
    return {"ok": True}


@route("POST", "/api/plan/skip")
def r_skip(h, c, u, body, q):
    ds, slot = slot_args(body)
    with c.tx():
        row = get_slot(c, u["id"], ds, slot)
        if row["cooked"]:
            raise ApiError(400, "Diese Mahlzeit ist schon gekocht.")
        partner = leftover_partner(c, u["id"], row)
        if partner and row["leftover"]:
            c.execute("UPDATE plan SET cook_portions=portions WHERE user_id=? AND date=? AND slot=?",
                      (u["id"], partner["date"], partner["slot"]))
        elif partner:
            c.execute("UPDATE plan SET leftover=0, cook_portions=portions WHERE user_id=? AND date=? AND slot=?",
                      (u["id"], partner["date"], partner["slot"]))
        c.execute("DELETE FROM plan WHERE user_id=? AND date=? AND slot=?", (u["id"], ds, slot))
    return {"ok": True}


@route("POST", "/api/plan/cook")
def r_cook(h, c, u, body, q):
    ds, slot = slot_args(body)
    undo = bool(body.get("undo"))
    with c.tx():
        row = get_slot(c, u["id"], ds, slot)
        if bool(row["cooked"]) != undo:
            return {"ok": True, "unchanged": True}
        S = load_profile(c, u["id"])
        planner.apply_cook(S, row, undo=undo)
        save_profile(c, u["id"], S)
        c.execute("UPDATE plan SET cooked=? WHERE user_id=? AND date=? AND slot=?", (0 if undo else 1, u["id"], ds, slot))
    return {"ok": True, "fridge": S["fridge"]}


@route("GET", "/api/alternatives")
def r_alternatives(h, c, u, body, q):
    ds, slot = slot_args({"date": (q.get("date") or [""])[0], "slot": (q.get("slot") or [""])[0]})
    S = load_profile(c, u["id"])
    cur = c.one("SELECT recipe_id FROM plan WHERE user_id=? AND date=? AND slot=?", (u["id"], ds, slot))
    sc = planner.alternatives(S, load_rows(c, u["id"]), ds, slot, exclude={cur["recipe_id"]} if cur else None, limit=12)
    return {"ids": [r["id"] for _w, r in sc]}


# ---------- Einkauf ----------
def shopping_payload(c, u, week, store=None):
    S = load_profile(c, u["id"])
    if store and store not in S["stores"]:
        store = None
    rows = load_rows(c, u["id"])
    shop = planner.shopping_for_week(S, rows, week, store=store)
    checks = {r["item"]: bool(r["checked"]) for r in c.all("SELECT item,checked FROM shop_checks WHERE user_id=? AND week=?", (u["id"], week.isoformat()))}
    custom = [dict(r) for r in c.all("SELECT id,text,checked FROM shop_custom WHERE user_id=? AND week=? ORDER BY id", (u["id"], week.isoformat()))]
    span = c.one("SELECT MIN(date) a, MAX(date) b FROM plan WHERE user_id=?", (u["id"],))
    shop.pop("needs", None)
    return dict(shop, week=week.isoformat(), checked=checks, custom=custom, first=span["a"], last=span["b"],
                budget=S["budget"])


@route("GET", "/api/shopping")
def r_shopping(h, c, u, body, q):
    return shopping_payload(c, u, week_param(q), (q.get("store") or [None])[0])


@route("POST", "/api/shopping/check")
def r_check(h, c, u, body, q):
    week = planner.monday(parse_day(body.get("week"), "week")).isoformat()
    item = str(body.get("item", ""))
    if item not in INGS:
        raise ApiError(400, "Unbekannter Artikel.")
    c.execute("INSERT INTO shop_checks(user_id,week,item,checked) VALUES(?,?,?,?) ON CONFLICT(user_id,week,item) DO UPDATE SET checked=excluded.checked",
              (u["id"], week, item, 1 if body.get("checked") else 0))
    return {"ok": True}


@route("POST", "/api/shopping/custom")
def r_custom_add(h, c, u, body, q):
    week = planner.monday(parse_day(body.get("week"), "week")).isoformat()
    text = str(body.get("text", "")).strip()[:120]
    if not text:
        raise ApiError(400, "Bitte gib etwas ein.")
    if c.one("SELECT COUNT(*) n FROM shop_custom WHERE user_id=? AND week=?", (u["id"], week))["n"] >= 100:
        raise ApiError(400, "Die Liste ist voll.")
    cur = c.execute("INSERT INTO shop_custom(user_id,week,text,checked) VALUES(?,?,?,0)", (u["id"], week, text))
    return {"id": cur.lastrowid}


@route("POST", r"/api/shopping/custom/(\d+)")
def r_custom_check(h, c, u, body, q, cid):
    c.execute("UPDATE shop_custom SET checked=? WHERE id=? AND user_id=?", (1 if body.get("checked") else 0, int(cid), u["id"]))
    return {"ok": True}


@route("DELETE", r"/api/shopping/custom/(\d+)")
def r_custom_delete(h, c, u, body, q, cid):
    c.execute("DELETE FROM shop_custom WHERE id=? AND user_id=?", (int(cid), u["id"]))
    return {"ok": True}


@route("POST", "/api/shopping/finish")
def r_finish(h, c, u, body, q):
    week = planner.monday(parse_day(body.get("week"), "week"))
    with c.tx():
        S = load_profile(c, u["id"])
        shop = planner.shopping_for_week(S, load_rows(c, u["id"]), week)
        checks = {r["item"] for r in c.all("SELECT item FROM shop_checks WHERE user_id=? AND week=? AND checked=1", (u["id"], week.isoformat()))}
        moved = []
        for it in shop["items"]:
            if it["id"] in checks:
                g = INGS[it["id"]]
                S["fridge"][it["id"]] = round(S["fridge"].get(it["id"], 0) + it["packs"] * g["pack"], 3)
                moved.append(it["id"])
        save_profile(c, u["id"], S)
        c.execute("DELETE FROM shop_checks WHERE user_id=? AND week=?", (u["id"], week.isoformat()))
        c.execute("DELETE FROM shop_custom WHERE user_id=? AND week=? AND checked=1", (u["id"], week.isoformat()))
    return {"ok": True, "moved": moved}


# ---------- Versand ----------
@route("POST", "/api/send")
def r_send(h, c, u, body, q):
    kind = body.get("kind")
    channel = body.get("channel")
    if channel not in ("email", "whatsapp"):
        raise ApiError(400, "Unbekannter Kanal.")
    S = load_profile(c, u["id"])
    rows = load_rows(c, u["id"])
    public_url = db.get_config(c, "public_url", "")
    if kind == "shopping":
        week = planner.monday(parse_day(body.get("week"), "week"))
        custom = [dict(r) for r in c.all("SELECT text,checked FROM shop_custom WHERE user_id=? AND week=?", (u["id"], week.isoformat()))]
        subject, text, html_body, _ = notify.shopping_message(S, rows, week, public_url, custom)
    elif kind == "week":
        week = planner.monday(parse_day(body.get("week"), "week"))
        subject, text, html_body = notify.week_plan_message(S, rows, week, public_url)
    elif kind == "today":
        subject, text, html_body = notify.today_message(S, rows, date.today(), public_url)
        if not text:
            raise ApiError(400, "Für heute ist nichts geplant.")
    else:
        raise ApiError(400, "Unbekannte Nachricht.")
    try:
        notify.deliver(c, u, channel, kind, subject, text, html_body)
    except notify.SendError as e:
        raise ApiError(502, str(e))
    return {"ok": True}


@route("GET", "/api/send-log")
def r_send_log(h, c, u, body, q):
    rows = c.all("SELECT channel,kind,created,status,error FROM send_log WHERE user_id=? ORDER BY id DESC LIMIT 20", (u["id"],))
    return {"log": [dict(r) for r in rows]}


# ---------- Verwaltung ----------
def admin_user_row(r):
    return {"id": r["id"], "username": r["username"], "display_name": r["display_name"], "is_admin": bool(r["is_admin"]),
            "disabled": bool(r["disabled"]), "must_change_pw": bool(r["must_change_pw"]), "created_at": r["created_at"],
            "email_verified": bool(r["email_verified"]), "phone_verified": bool(r["phone_verified"]),
            "locked": r["locked_until"] > time.time()}


@route("GET", "/api/admin/users", admin=True)
def r_admin_users(h, c, u, body, q):
    return {"users": [admin_user_row(r) for r in c.all("SELECT * FROM users ORDER BY username COLLATE NOCASE")]}


def temp_password():
    return secrets.token_urlsafe(9)


@route("POST", "/api/admin/users", admin=True)
def r_admin_create(h, c, u, body, q):
    pw = str(body.get("password") or "") or temp_password()
    with c.tx():
        uid = create_user(c, dict(body, password=pw), is_admin=bool(body.get("is_admin")), must_change=True)
    return {"id": uid, "temp_password": pw}


def other_admins(c, uid):
    return c.one("SELECT COUNT(*) n FROM users WHERE is_admin=1 AND disabled=0 AND id<>?", (uid,))["n"]


@route("PUT", r"/api/admin/users/(\d+)", admin=True)
def r_admin_update(h, c, u, body, q, uid):
    uid = int(uid)
    target = c.one("SELECT * FROM users WHERE id=?", (uid,))
    if not target:
        raise ApiError(404, "Unbekanntes Konto.")
    out = {"ok": True}
    with c.tx():
        if "is_admin" in body:
            if not body["is_admin"] and target["is_admin"] and other_admins(c, uid) == 0:
                raise ApiError(400, "Es muss mindestens eine Verwaltung geben.")
            c.execute("UPDATE users SET is_admin=? WHERE id=?", (1 if body["is_admin"] else 0, uid))
        if "disabled" in body:
            if uid == u["id"]:
                raise ApiError(400, "Du kannst dein eigenes Konto nicht sperren.")
            c.execute("UPDATE users SET disabled=? WHERE id=?", (1 if body["disabled"] else 0, uid))
            if body["disabled"]:
                auth.end_all_sessions(c, uid)
        if body.get("unlock"):
            c.execute("UPDATE users SET failed_logins=0, locked_until=0 WHERE id=?", (uid,))
        if body.get("reset_password"):
            pw = temp_password()
            c.execute("UPDATE users SET pw_hash=?, must_change_pw=1, failed_logins=0, locked_until=0 WHERE id=?",
                      (auth.hash_password(pw), uid))
            auth.end_all_sessions(c, uid)
            out["temp_password"] = pw
    return out


@route("DELETE", r"/api/admin/users/(\d+)", admin=True)
def r_admin_delete(h, c, u, body, q, uid):
    uid = int(uid)
    if uid == u["id"]:
        raise ApiError(400, "Dein eigenes Konto löschst du im Profil.")
    target = c.one("SELECT * FROM users WHERE id=?", (uid,))
    if not target:
        raise ApiError(404, "Unbekanntes Konto.")
    if target["is_admin"] and other_admins(c, uid) == 0:
        raise ApiError(400, "Es muss mindestens eine Verwaltung geben.")
    c.execute("DELETE FROM users WHERE id=?", (uid,))
    return {"ok": True}


@route("POST", "/api/admin/invites", admin=True)
def r_admin_invite(h, c, u, body, q):
    code = auth.new_invite_code()
    days = max(1, min(30, int(body.get("days") or 7)))
    c.execute("INSERT INTO invites(code_hash,created_by,created,expires) VALUES(?,?,?,?)",
              (auth.sha(code), u["id"], time.time(), time.time() + days * 86400))
    return {"code": code, "days": days}


@route("GET", "/api/admin/config", admin=True)
def r_admin_config(h, c, u, body, q):
    smtp = notify.smtp_config(c)
    smtp["password_set"] = bool(smtp.pop("password", ""))
    return {"registration": db.get_config(c, "registration", "closed"), "public_url": db.get_config(c, "public_url", ""),
            "smtp": smtp, "whatsapp": notify.whatsapp_config(c)}


@route("PUT", "/api/admin/config", admin=True)
def r_admin_config_put(h, c, u, body, q):
    with c.tx():
        if "registration" in body:
            if body["registration"] not in ("closed", "invite", "open"):
                raise ApiError(400, "Ungültiger Registrierungsmodus.")
            db.set_config(c, "registration", body["registration"])
        if "public_url" in body:
            url = str(body["public_url"] or "").strip()[:200]
            if url and not re.match(r"^https?://[^\s<>\"']+$", url):
                raise ApiError(400, "Die Adresse muss mit http:// oder https:// beginnen.")
            db.set_config(c, "public_url", url.rstrip("/"))
        if "smtp" in body:
            cur = notify.smtp_config(c)
            src = body["smtp"] or {}
            for k in ("host", "username", "from_name"):
                if k in src:
                    cur[k] = str(src[k] or "").strip()[:200]
            if "from_addr" in src:
                fa = str(src["from_addr"] or "").strip()
                if fa:
                    try:
                        fa = notify.clean_email(fa)
                    except ValueError:
                        raise ApiError(400, "Die Absenderadresse ist ungültig.")
                cur["from_addr"] = fa
            if "port" in src:
                try:
                    cur["port"] = max(1, min(65535, int(src["port"])))
                except (TypeError, ValueError):
                    raise ApiError(400, "Ungültiger Port.")
            if src.get("security") in ("starttls", "ssl", "none"):
                cur["security"] = src["security"]
            if src.get("password"):
                cur["password"] = str(src["password"])[:500]
            if src.get("clear_password"):
                cur["password"] = ""
            db.set_config(c, "smtp", cur)
        if "whatsapp" in body:
            cur = notify.whatsapp_config(c)
            src = body["whatsapp"] or {}
            if "enabled" in src:
                cur["enabled"] = bool(src["enabled"])
            if "gateway_url" in src:
                url = str(src["gateway_url"] or "").strip()
                if not re.match(r"^https?://[^\s<>\"']+$", url):
                    raise ApiError(400, "Die Gateway-Adresse muss mit http:// beginnen.")
                cur["gateway_url"] = url
            if "country_code" in src:
                cc = re.sub(r"\D", "", str(src["country_code"]))
                if not 1 <= len(cc) <= 3:
                    raise ApiError(400, "Ungültige Ländervorwahl.")
                cur["country_code"] = cc
            db.set_config(c, "whatsapp", cur)
    return r_admin_config(h, c, u, body, q)


@route("POST", "/api/admin/test-email", admin=True)
def r_admin_test_email(h, c, u, body, q):
    try:
        to = notify.clean_email(body.get("to") or u["email"])
    except ValueError as e:
        raise ApiError(400, str(e))
    try:
        notify.send_email(c, to, "Wochenteller: Test-E-Mail",
                          "Hallo! Der E-Mail-Versand deines Wochentellers funktioniert. 🎉",
                          notify._html_wrap("Test-E-Mail", "<p>Der E-Mail-Versand deines Wochentellers funktioniert. 🎉</p>", ""))
    except notify.SendError as e:
        raise ApiError(502, str(e))
    return {"ok": True}


@route("POST", "/api/admin/test-whatsapp", admin=True)
def r_admin_test_whatsapp(h, c, u, body, q):
    try:
        phone = notify.clean_phone(body.get("phone"), notify.whatsapp_config(c)["country_code"])
    except ValueError as e:
        raise ApiError(400, str(e))
    try:
        notify.send_whatsapp(c, phone, "✅ Wochenteller: Der WhatsApp-Versand über JARVIS funktioniert.")
    except notify.SendError as e:
        raise ApiError(502, str(e))
    return {"ok": True}


@route("GET", "/api/admin/gateway-health", admin=True)
def r_admin_gateway(h, c, u, body, q):
    return notify.gateway_health(c)


# ---------- HTTP-Schicht ----------
class RawJson:
    def __init__(self, raw, etag=None, cache=None):
        self.raw, self.etag, self.cache = raw, etag, cache


class Handler(BaseHTTPRequestHandler):
    server_version = "Wochenteller"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s [%s] %s\n" % (self.ip, time.strftime("%d.%m. %H:%M:%S"), fmt % args))

    @property
    def ip(self):
        if SETTINGS.trust_proxy:
            fwd = self.headers.get("X-Forwarded-For")
            if fwd:
                return fwd.split(",")[0].strip()
        return self.client_address[0]

    def do_GET(self):
        self.dispatch("GET")

    def do_POST(self):
        self.dispatch("POST")

    def do_PUT(self):
        self.dispatch("PUT")

    def do_DELETE(self):
        self.dispatch("DELETE")

    def do_HEAD(self):
        self.dispatch("GET", head=True)

    # --- Antworten ---
    def common_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Content-Security-Policy", CSP)
        if SETTINGS.secure_cookies:
            self.send_header("Strict-Transport-Security", "max-age=31536000")

    def send_bytes(self, status, data, ctype, extra=None, head=False):
        gz = "gzip" in (self.headers.get("Accept-Encoding") or "") and len(data) > 1024 and ctype.split(";")[0] in (
            "application/json", "text/html", "text/css", "application/javascript", "image/svg+xml", "application/manifest+json")
        if gz:
            data = gzip.compress(data, 6)
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if gz:
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Vary", "Accept-Encoding")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        for ck in getattr(self, "_cookies", []):
            self.send_header("Set-Cookie", ck)
        self.common_headers()
        self.end_headers()
        if not head:
            self.wfile.write(data)

    def send_json(self, status, obj, extra=None):
        extra = dict({"Cache-Control": "no-store"}, **(extra or {}))
        self.send_bytes(status, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", extra)

    def set_cookie(self, token, expire=False):
        c = cookies.SimpleCookie()
        c[auth.SESSION_COOKIE] = token
        m = c[auth.SESSION_COOKIE]
        m["path"] = "/"
        m["httponly"] = True
        m["samesite"] = "Lax"
        m["max-age"] = 0 if expire else auth.SESSION_DAYS * 86400
        if SETTINGS.secure_cookies:
            m["secure"] = True
        self._cookies = getattr(self, "_cookies", []) + [m.OutputString()]

    def login_response(self, c, uid):
        token, csrf = auth.create_session(c, uid, self.headers.get("User-Agent", ""))
        self.set_cookie(token)
        u = c.one("SELECT * FROM users WHERE id=?", (uid,))
        return {"authenticated": True, "user": user_public(u), "csrf": csrf}

    # --- Ablauf ---
    def dispatch(self, method, head=False):
        self._cookies = []
        url = urlparse(self.path)
        path = url.path
        try:
            if not path.startswith("/api/"):
                return self.serve_static(path, head)
            for m, rx, fn, need_auth, admin, allow_pw in ROUTES:
                if m != method:
                    continue
                mt = rx.match(path)
                if not mt:
                    continue
                return self.run(fn, mt.groups(), need_auth, admin, allow_pw, parse_qs(url.query), method)
            raise ApiError(404, "Unbekannte Schnittstelle.")
        except ApiError as e:
            self.send_json(e.status, {"error": e.message, "code": e.code})
        except Exception:
            traceback.print_exc()
            self.send_json(500, {"error": "Interner Fehler. Details stehen im Server-Fenster."})

    def read_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ApiError(413, "Anfrage zu groß.")
        if not n:
            return {}
        if "application/json" not in (self.headers.get("Content-Type") or ""):
            raise ApiError(415, "JSON erwartet.")
        try:
            data = json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise ApiError(400, "Ungültiges JSON.")
        if not isinstance(data, dict):
            raise ApiError(400, "JSON-Objekt erwartet.")
        return data

    def run(self, fn, groups, need_auth, admin, allow_pw, q, method):
        body = self.read_body() if method in ("POST", "PUT", "DELETE") else {}
        with db.connect() as c:
            raw = cookies.SimpleCookie(self.headers.get("Cookie") or "")
            self.token = raw[auth.SESSION_COOKIE].value if auth.SESSION_COOKIE in raw else None
            self.session = auth.get_session(c, self.token) if self.token else None
            u = self.session
            if method != "GET":
                self.check_origin()
                if u and fn not in (r_login, r_setup, r_register):
                    sent = self.headers.get("X-CSRF-Token") or ""
                    if not secrets.compare_digest(sent, u["csrf"]):
                        raise ApiError(403, "Sicherheitsprüfung fehlgeschlagen. Bitte Seite neu laden.", "csrf")
            if need_auth and not u:
                raise ApiError(401, "Bitte melde dich an.", "auth")
            if need_auth and u["must_change_pw"] and not allow_pw:
                raise ApiError(403, "Bitte vergib zuerst ein neues Passwort.", "password_change_required")
            if admin and not u["is_admin"]:
                raise ApiError(403, "Nur für die Verwaltung.")
            res = fn(self, c, u, body, q, *groups)
        if isinstance(res, RawJson):
            if res.etag and self.headers.get("If-None-Match") == res.etag:
                self.send_response(304)
                self.send_header("ETag", res.etag)
                self.common_headers()
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            return self.send_bytes(200, res.raw, "application/json; charset=utf-8",
                                   {"ETag": res.etag, "Cache-Control": res.cache or "no-store"})
        self.send_json(200, res)

    def check_origin(self):
        origin = self.headers.get("Origin")
        if not origin:
            return
        host = self.headers.get("X-Forwarded-Host") if SETTINGS.trust_proxy and self.headers.get("X-Forwarded-Host") else self.headers.get("Host")
        if urlparse(origin).netloc != host:
            raise ApiError(403, "Anfrage von fremder Seite abgelehnt.", "origin")

    def serve_static(self, path, head):
        name = STATIC.get(path)
        if not name:
            return self.send_bytes(404, b"Nicht gefunden", "text/plain; charset=utf-8", head=head)
        fp = os.path.join(WEB_DIR, name)
        with open(fp, "rb") as f:
            data = f.read()
        etag = '"' + hashlib.sha256(data).hexdigest()[:20] + '"'
        if self.headers.get("If-None-Match") == etag:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Content-Length", "0")
            self.common_headers()
            self.end_headers()
            return
        ctype = {"index.html": "text/html; charset=utf-8", "app.js": "application/javascript; charset=utf-8",
                 "app.css": "text/css; charset=utf-8", "manifest.webmanifest": "application/manifest+json",
                 "icon.svg": "image/svg+xml"}.get(name) or mimetypes.guess_type(name)[0] or "application/octet-stream"
        self.send_bytes(200, data, ctype, {"ETag": etag, "Cache-Control": "no-cache"}, head=head)


def make_server(host, port, certfile=None, keyfile=None):
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.daemon_threads = True
    if certfile:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.load_cert_chain(certfile, keyfile)
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
        SETTINGS.secure_cookies = True
    return httpd
