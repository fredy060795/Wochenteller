"""Automatische Nachrichten: Einkaufsliste am Einkaufstag, Tagesmenü zur gewünschten Uhrzeit.

Läuft als Hintergrund-Thread im Server. Jede Nachricht wird pro Zeitraum höchstens einmal geschickt
(send_log), auch nach einem Neustart. War der Server zur Uhrzeit aus, wird bis zu 3 Stunden später nachgeholt.
"""
import threading
import time
import traceback
from datetime import datetime, timedelta

from . import db, notify, planner

CATCH_UP = timedelta(hours=3)


def due(now, hhmm):
    h, m = (int(x) for x in hhmm.split(":"))
    at = now.replace(hour=h, minute=m, second=0, microsecond=0)
    return at <= now < at + CATCH_UP


def recently_failed(c, user_id, channel, kind, period):
    """Nach einem Fehlschlag 30 Minuten warten, statt jede Minute erneut zu versuchen."""
    return c.one("SELECT 1 FROM send_log WHERE user_id=? AND channel=? AND kind=? AND period_key=? AND status='failed' "
                 "AND created>?", (user_id, channel, kind, period, time.time() - 1800)) is not None


def tick(now=None):
    now = now or datetime.now()
    today = now.date()
    sent = 0
    with db.connect() as c:
        public_url = db.get_config(c, "public_url", "")
        users = c.all("SELECT * FROM users WHERE disabled=0")
        for u in users:
            prof = db.load_profile(c, u["id"])
            if not prof:
                continue
            S = planner.normalize_profile(prof)
            n = S["notify"]
            jobs = []
            sh = n["shopping"]
            if sh["enabled"] and sh["channels"] and today.weekday() == sh["weekday"] and due(now, sh["time"]):
                jobs.append(("shopping", sh["channels"]))
            dl = n["daily"]
            if dl["enabled"] and dl["channels"] and due(now, dl["time"]):
                jobs.append(("daily", dl["channels"]))
            if not jobs:
                continue
            rows = None
            for kind, channels in jobs:
                if kind == "shopping":
                    week = notify.target_shopping_week(today)
                    period = week.isoformat()
                else:
                    period = today.isoformat()
                todo = [ch for ch in channels if not notify.already_sent(c, u["id"], ch, kind, period)
                        and not recently_failed(c, u["id"], ch, kind, period)]
                if not todo:
                    continue
                if rows is None:
                    rows = [dict(r) for r in c.all(
                        "SELECT date,slot,recipe_id,portions,cook_portions,leftover,cooked FROM plan WHERE user_id=?", (u["id"],))
                        if r["recipe_id"] in planner.RBY]
                if kind == "shopping":
                    if not planner.week_rows(rows, week):
                        continue  # nichts geplant → nichts schicken
                    custom = [dict(r) for r in c.all("SELECT text,checked FROM shop_custom WHERE user_id=? AND week=?",
                                                     (u["id"], period))]
                    subject, text, html_body, _ = notify.shopping_message(S, rows, week, public_url, custom, today=today)
                else:
                    subject, text, html_body = notify.today_message(S, rows, today, public_url)
                    if not text:
                        continue
                for ch in todo:
                    try:
                        notify.deliver(c, u, ch, kind, subject, text, html_body, period_key=period)
                        sent += 1
                    except notify.SendError as e:
                        print(f"[Erinnerung] {u['username']} {kind}/{ch}: {e}")
    return sent


class Scheduler(threading.Thread):
    def __init__(self, interval=60):
        super().__init__(daemon=True, name="wochenteller-scheduler")
        self.interval = interval
        self.stop = threading.Event()

    def run(self):
        while not self.stop.wait(5 if not hasattr(self, "_started_once") else self.interval):
            self._started_once = True
            try:
                tick()
            except Exception:
                traceback.print_exc()
