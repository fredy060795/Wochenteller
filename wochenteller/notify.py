"""Versand per E-Mail (eigener SMTP-Server) und WhatsApp (über das JARVIS-Gateway).

Das JARVIS-Gateway (Whatsapp_Buissines/jarvis_gateway.cjs) lauscht auf 127.0.0.1:3000 und nimmt
POST /send {"phone": "4366...", "message": "...", "request_id": "..."} an. Anfragen mit Browser-Origin
lehnt es ab – deshalb verschickt immer der Server, nie der Browser.
"""
import html
import json
import re
import smtplib
import ssl
import time
import urllib.error
import urllib.request
import uuid
from datetime import timedelta
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

from . import db
from .catalog import INGS, RBY, SLOT_LABEL
from .planner import (d2s, eff_ings, eur, fmt_qty, grouped_items, monday, s2d, shopping_for_week, sort_rows,
                      store_name, week_rows)

DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
DAILY_LIMIT = 40          # Nachrichten pro Person und Tag (ohne Bestätigungscodes)
CODE_LIMIT_PER_HOUR = 5   # Bestätigungscodes pro Person und Stunde

DEFAULT_SMTP = {"host": "", "port": 587, "security": "starttls", "username": "", "password": "",
                "from_addr": "", "from_name": "Wochenteller"}
DEFAULT_WHATSAPP = {"enabled": False, "gateway_url": "http://127.0.0.1:3000/send", "country_code": "43"}


class SendError(Exception):
    pass


# ---------- Konfiguration ----------
def smtp_config(c):
    cfg = dict(DEFAULT_SMTP)
    cfg.update(db.get_config(c, "smtp", {}) or {})
    return cfg


def whatsapp_config(c):
    cfg = dict(DEFAULT_WHATSAPP)
    cfg.update(db.get_config(c, "whatsapp", {}) or {})
    return cfg


def email_ready(c):
    cfg = smtp_config(c)
    return bool(cfg["host"] and cfg["from_addr"])


def whatsapp_ready(c):
    return bool(whatsapp_config(c)["enabled"])


# ---------- Validierung ----------
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[A-Za-z]{2,}$")


def clean_email(s):
    s = (s or "").strip()
    if not EMAIL_RE.match(s) or len(s) > 254 or any(ch in s for ch in "\r\n<>,;\""):
        raise ValueError("Bitte gib eine gültige E-Mail-Adresse ein.")
    return s


def clean_phone(s, country_code="43"):
    """Normalisiert auf internationale Ziffern ohne + (z. B. 436641234567)."""
    p = re.sub(r"[\s()./-]", "", s or "")
    if p.startswith("+"):
        p = p[1:]
    elif p.startswith("00"):
        p = p[2:]
    elif p.startswith("0"):
        p = (country_code or "43") + p[1:]
    if not re.fullmatch(r"\d{8,15}", p):
        raise ValueError("Bitte gib eine gültige Handynummer ein, z. B. +43 664 1234567.")
    return p


def mask_phone(p):
    return ("+" + p[:2] + " … " + p[-3:]) if p and len(p) > 5 else p


# ---------- Transport ----------
def send_email(c, to, subject, text, html_body=None):
    cfg = smtp_config(c)
    if not (cfg["host"] and cfg["from_addr"]):
        raise SendError("Es ist noch kein SMTP-Server eingerichtet (Verwaltung → E-Mail).")
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((cfg.get("from_name") or "Wochenteller", cfg["from_addr"]))
    msg["To"] = to
    msg["Message-ID"] = make_msgid(domain=cfg["from_addr"].split("@")[-1])
    msg.set_content(text)
    if html_body:
        msg.add_alternative(html_body, subtype="html")
    port = int(cfg.get("port") or (465 if cfg["security"] == "ssl" else 587))
    ctx = ssl.create_default_context()
    try:
        if cfg["security"] == "ssl":
            s = smtplib.SMTP_SSL(cfg["host"], port, timeout=25, context=ctx)
        else:
            s = smtplib.SMTP(cfg["host"], port, timeout=25)
        with s:
            s.ehlo()
            if cfg["security"] == "starttls":
                s.starttls(context=ctx)
                s.ehlo()
            if cfg.get("username"):
                s.login(cfg["username"], cfg.get("password") or "")
            s.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        raise SendError("Der SMTP-Server hat die Anmeldung abgelehnt (Benutzer/Passwort prüfen).")
    except (smtplib.SMTPException, OSError) as e:
        raise SendError(f"E-Mail konnte nicht gesendet werden: {e}")


def send_whatsapp(c, phone, text, request_id=None):
    cfg = whatsapp_config(c)
    if not cfg["enabled"]:
        raise SendError("WhatsApp-Versand ist nicht aktiviert (Verwaltung → WhatsApp).")
    url = cfg["gateway_url"]
    if not re.match(r"^https?://", url or ""):
        raise SendError("Die Gateway-Adresse ist ungültig.")
    if len(text) > 3900:
        text = text[:3880].rsplit("\n", 1)[0] + "\n…"
    body = json.dumps({"phone": phone, "message": text, "request_id": request_id or "wt-" + uuid.uuid4().hex}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            res = json.loads(e.read().decode() or "{}")
        except Exception:
            res = {}
        raise SendError("WhatsApp-Gateway: " + str(res.get("error") or f"HTTP {e.code}"))
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise SendError("Das JARVIS-WhatsApp-Gateway ist nicht erreichbar. Läuft start_gateway.bat? "
                        f"({getattr(e, 'reason', e)})")
    if res.get("success") is not True:
        raise SendError("WhatsApp-Gateway hat den Versand nicht bestätigt: " + str(res.get("error") or res))
    return res


def gateway_health(c):
    url = whatsapp_config(c)["gateway_url"].rsplit("/", 1)[0] + "/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read().decode() or "{}")
    except Exception as e:
        return {"success": False, "ready": False, "error": str(getattr(e, "reason", e))}


# ---------- Protokoll & Limits ----------
def log(c, user_id, channel, kind, status, period_key=None, error=None):
    c.execute("INSERT INTO send_log(user_id,channel,kind,period_key,created,status,error) VALUES(?,?,?,?,?,?,?)",
              (user_id, channel, kind, period_key, time.time(), status, (error or "")[:500]))


def check_limit(c, user_id, kind):
    if kind == "code":
        n = c.one("SELECT COUNT(*) n FROM send_log WHERE user_id=? AND kind='code' AND created>?",
                  (user_id, time.time() - 3600))["n"]
        if n >= CODE_LIMIT_PER_HOUR:
            raise SendError("Zu viele Bestätigungscodes angefordert. Bitte in einer Stunde erneut versuchen.")
    else:
        n = c.one("SELECT COUNT(*) n FROM send_log WHERE user_id=? AND kind<>'code' AND status='sent' AND created>?",
                  (user_id, time.time() - 86400))["n"]
        if n >= DAILY_LIMIT:
            raise SendError("Tageslimit für Nachrichten erreicht.")


def already_sent(c, user_id, channel, kind, period_key):
    return c.one("SELECT 1 FROM send_log WHERE user_id=? AND channel=? AND kind=? AND period_key=? AND status='sent'",
                 (user_id, channel, kind, period_key)) is not None


def deliver(c, user, channel, kind, subject, text, html_body=None, period_key=None):
    """Schickt eine Nachricht an die bestätigte Adresse/Nummer der Person und protokolliert es."""
    check_limit(c, user["id"], kind)
    try:
        if channel == "email":
            if not (user["email"] and user["email_verified"]):
                raise SendError("Bitte bestätige zuerst deine E-Mail-Adresse (Profil → Kontakt).")
            send_email(c, user["email"], subject, text, html_body)
        elif channel == "whatsapp":
            if not (user["phone"] and user["phone_verified"]):
                raise SendError("Bitte bestätige zuerst deine WhatsApp-Nummer (Profil → Kontakt).")
            rid = f"wt-{user['id']}-{kind}-{period_key}" if period_key else None
            send_whatsapp(c, user["phone"], text, request_id=rid)
        else:
            raise SendError("Unbekannter Kanal.")
    except SendError as e:
        log(c, user["id"], channel, kind, "failed", period_key, str(e))
        raise
    log(c, user["id"], channel, kind, "sent", period_key)


# ---------- Nachrichtentexte ----------
def _date_de(d):
    return f"{d.day}.{d.month}."


def _footer(public_url):
    return f"\n\nIm Wochenteller öffnen: {public_url}" if public_url else ""


def shopping_message(S, rows, week_monday, public_url="", custom=None, today=None):
    shop = shopping_for_week(S, rows, week_monday, today=today)
    end = week_monday + timedelta(days=6)
    kw = week_monday.isocalendar()[1]
    head = f"🛒 Einkaufsliste KW {kw} ({_date_de(week_monday)}–{_date_de(end)}) · {store_name(shop['store'])}"
    lines, hl = [head, ""], []
    for cat, items in grouped_items(shop["items"]):
        lines.append(f"*{cat}*")
        hl.append(f"<h3 style='margin:18px 0 6px;font-size:15px;color:#1F4D36'>{html.escape(cat)}</h3><table style='width:100%;border-collapse:collapse'>")
        for it in items:
            g = INGS[it["id"]]
            lines.append(f"• {it['packs']}× {g['name']} ({g['packLabel']}) – {eur(it['price'])}")
            hl.append(f"<tr><td style='padding:4px 0;border-bottom:1px solid #eee'>☐ {it['packs']}× {html.escape(g['name'])} "
                      f"<span style='color:#777'>({html.escape(g['packLabel'])}, du brauchst {fmt_qty(it['need'], g['unit'])})</span></td>"
                      f"<td style='text-align:right;white-space:nowrap;border-bottom:1px solid #eee'>{eur(it['price'])}</td></tr>")
        lines.append("")
        hl.append("</table>")
    extra = [x for x in (custom or []) if not x.get("checked")]
    if extra:
        lines.append("*Sonstiges*")
        hl.append("<h3 style='margin:18px 0 6px;font-size:15px;color:#1F4D36'>Sonstiges</h3><ul>")
        for x in extra:
            lines.append(f"• {x['text']}")
            hl.append(f"<li>{html.escape(x['text'])}</li>")
        lines.append("")
        hl.append("</ul>")
    if not shop["items"] and not extra:
        lines.append("Für diese Woche musst du nichts einkaufen – alles ist da. 🎉")
        hl.append("<p>Für diese Woche musst du nichts einkaufen – alles ist da. 🎉</p>")
    lines.append(f"Summe ca. {eur(shop['total'])} (Budget {eur(S['budget'])})")
    if shop["fromFridge"]:
        lines.append("Schon im Vorrat: " + ", ".join(INGS[i]["name"] for i in shop["fromFridge"]))
    menu = week_menu_lines(rows, week_monday)
    if menu:
        lines += ["", "*Geplant:*"] + menu
    text = "\n".join(lines) + _footer(public_url)
    html_body = _html_wrap(head, "".join(hl) +
                           f"<p style='font-size:16px;font-weight:bold;border-top:2px solid #222;padding-top:8px'>Summe ca. {eur(shop['total'])} "
                           f"<span style='font-weight:normal;color:#666'>(Budget {eur(S['budget'])})</span></p>" +
                           (f"<h3 style='font-size:15px;color:#1F4D36'>Geplant</h3><p style='line-height:1.6'>{'<br>'.join(html.escape(m) for m in menu)}</p>" if menu else ""),
                           public_url)
    return head, text, html_body, shop


def week_menu_lines(rows, week_monday):
    out = []
    for row in sort_rows(week_rows(rows, week_monday)):
        if row["slot"] == "frueh":
            continue
        r = RBY.get(row["recipe_id"])
        if not r:
            continue
        d = s2d(row["date"])
        out.append(f"{DAYS[d.weekday()][:2]} {SLOT_LABEL[row['slot']]}: {r['n']}" + (" (Reste)" if row["leftover"] else ""))
    return out


def today_message(S, rows, day, public_url=""):
    todays = [r for r in sort_rows(rows) if r["date"] == d2s(day)]
    head = f"🍽️ Heute, {DAYS[day.weekday()]} {_date_de(day)}"
    if not todays:
        return head, None, None
    lines, hl = [head, ""], []
    for row in todays:
        r = RBY.get(row["recipe_id"])
        if not r:
            continue
        extra = " – Reste vom Vortag aufwärmen" if row["leftover"] else f" · {r['t']} Min"
        done = " ✓" if row["cooked"] else ""
        lines.append(f"{r['e']} {SLOT_LABEL[row['slot']]}: {r['n']}{extra}{done}")
        hl.append(f"<p style='margin:6px 0;font-size:16px'>{r['e']} <b>{SLOT_LABEL[row['slot']]}:</b> {html.escape(r['n'])}"
                  f"<span style='color:#666'>{html.escape(extra)}</span></p>")
    missing = []
    for row in todays:
        r = RBY.get(row["recipe_id"])
        if not r or row["cooked"] or not row["cook_portions"]:
            continue
        for iid, _q in eff_ings(r, S):
            if INGS[iid]["minor"] or iid in S["pantry"] or S["fridge"].get(iid, 0) > 0:
                continue
            if INGS[iid]["name"] not in missing:
                missing.append(INGS[iid]["name"])
    if missing:
        lines += ["", "Laut Vorrat fehlt noch: " + ", ".join(missing)]
        hl.append(f"<p style='color:#A3245A'>Laut Vorrat fehlt noch: {html.escape(', '.join(missing))}</p>")
    text = "\n".join(lines) + _footer(public_url)
    return head, text, _html_wrap(head, "".join(hl), public_url)


def week_plan_message(S, rows, week_monday, public_url=""):
    kw = week_monday.isocalendar()[1]
    head = f"📅 Wochenplan KW {kw} ({_date_de(week_monday)}–{_date_de(week_monday + timedelta(days=6))})"
    by_day = {}
    for row in sort_rows(week_rows(rows, week_monday)):
        by_day.setdefault(row["date"], []).append(row)
    lines, hl = [head], []
    for ds, lst in by_day.items():
        d = s2d(ds)
        lines += ["", f"*{DAYS[d.weekday()]} {_date_de(d)}*"]
        hl.append(f"<h3 style='margin:16px 0 4px;font-size:15px;color:#1F4D36'>{DAYS[d.weekday()]} {_date_de(d)}</h3>")
        for row in lst:
            r = RBY.get(row["recipe_id"])
            if r:
                t = f"{SLOT_LABEL[row['slot']]}: {r['n']}" + (" (Reste)" if row["leftover"] else "")
                lines.append(f"{r['e']} {t}")
                hl.append(f"<div style='margin:3px 0'>{r['e']} {html.escape(t)}</div>")
    if not by_day:
        lines.append("\nFür diese Woche ist noch nichts geplant.")
    text = "\n".join(lines) + _footer(public_url)
    return head, text, _html_wrap(head, "".join(hl), public_url)


def code_message(code, purpose):
    head = "Dein Wochenteller-Code"
    text = (f"Dein Bestätigungscode für Wochenteller lautet: {code}\n\n"
            f"Er gilt 15 Minuten und bestätigt {purpose}. Wenn du das nicht angefordert hast, kannst du diese Nachricht ignorieren.")
    return head, text, _html_wrap(head, f"<p>Dein Bestätigungscode lautet:</p><p style='font-size:30px;letter-spacing:6px;font-weight:bold'>{code}</p>"
                                        f"<p style='color:#666'>Er gilt 15 Minuten und bestätigt {html.escape(purpose)}. "
                                        "Wenn du das nicht angefordert hast, kannst du diese Nachricht ignorieren.</p>", "")


def _html_wrap(title, inner, public_url):
    link = (f"<p style='margin-top:24px'><a href='{html.escape(public_url)}' style='background:#1F4D36;color:#fff;"
            "padding:10px 18px;border-radius:8px;text-decoration:none'>Im Wochenteller öffnen</a></p>") if public_url else ""
    return (f"<!doctype html><html><body style='margin:0;background:#F2F5F0;font-family:Segoe UI,Roboto,Arial,sans-serif;color:#17201A'>"
            f"<div style='max-width:560px;margin:0 auto;padding:24px'><div style='background:#fff;border-radius:14px;padding:22px 24px'>"
            f"<h2 style='margin:0 0 8px;font-size:20px'>{html.escape(title)}</h2>{inner}{link}</div>"
            f"<p style='color:#888;font-size:12px;margin:14px 4px'>Gesendet von deinem Wochenteller. Benachrichtigungen kannst du im Profil abschalten.</p>"
            f"</div></body></html>")


def target_shopping_week(today):
    """Woche, für die am Einkaufstag eingekauft wird: die heute oder in den nächsten 6 Tagen beginnende."""
    return today if today.weekday() == 0 else monday(today) + timedelta(days=7)
