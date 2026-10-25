"""SQLite-Speicher. Jede Anfrage öffnet ihre eigene Verbindung; WAL erlaubt parallele Leser."""
import json
import os
import sqlite3
import threading
import time

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE COLLATE NOCASE,
  display_name TEXT NOT NULL,
  pw_hash TEXT NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0,
  disabled INTEGER NOT NULL DEFAULT 0,
  must_change_pw INTEGER NOT NULL DEFAULT 0,
  email TEXT, email_verified INTEGER NOT NULL DEFAULT 0,
  phone TEXT, phone_verified INTEGER NOT NULL DEFAULT 0,
  failed_logins INTEGER NOT NULL DEFAULT 0,
  locked_until REAL NOT NULL DEFAULT 0,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  csrf TEXT NOT NULL,
  created REAL NOT NULL, expires REAL NOT NULL, last_seen REAL NOT NULL,
  user_agent TEXT
);
CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);
CREATE TABLE IF NOT EXISTS profiles (
  user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS plan (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date TEXT NOT NULL, slot TEXT NOT NULL,
  recipe_id TEXT NOT NULL,
  portions INTEGER NOT NULL,
  cook_portions INTEGER NOT NULL,
  leftover INTEGER NOT NULL DEFAULT 0,
  cooked INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, date, slot)
);
CREATE TABLE IF NOT EXISTS shop_checks (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  week TEXT NOT NULL, item TEXT NOT NULL, checked INTEGER NOT NULL,
  PRIMARY KEY (user_id, week, item)
);
CREATE TABLE IF NOT EXISTS shop_custom (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  week TEXT NOT NULL, text TEXT NOT NULL, checked INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS verify_codes (
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  channel TEXT NOT NULL, target TEXT NOT NULL, code_hash TEXT NOT NULL,
  expires REAL NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, channel)
);
CREATE TABLE IF NOT EXISTS send_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  channel TEXT NOT NULL, kind TEXT NOT NULL, period_key TEXT,
  created REAL NOT NULL, status TEXT NOT NULL, error TEXT
);
CREATE INDEX IF NOT EXISTS send_log_user ON send_log(user_id, created);
CREATE TABLE IF NOT EXISTS invites (
  code_hash TEXT PRIMARY KEY,
  created_by INTEGER, created REAL NOT NULL, expires REAL NOT NULL,
  used_by INTEGER
);
CREATE TABLE IF NOT EXISTS config (
  key TEXT PRIMARY KEY, value TEXT NOT NULL
);
"""

_lock = threading.Lock()
DB_PATH = None


def init(path):
    global DB_PATH
    DB_PATH = path
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with connect() as c:
        c.executescript(SCHEMA)


def connect():
    c = sqlite3.connect(DB_PATH, timeout=15, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=15000")
    return _Conn(c)


class _Conn:
    """Kleine Hülle: `with db.connect() as c:` schließt die Verbindung zuverlässig;
    `with c.tx():` bündelt mehrere Schreibvorgänge atomar."""

    def __init__(self, c):
        self.c = c

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.c.close()

    def execute(self, *a):
        return self.c.execute(*a)

    def executescript(self, s):
        return self.c.executescript(s)

    def one(self, sql, args=()):
        return self.c.execute(sql, args).fetchone()

    def all(self, sql, args=()):
        return self.c.execute(sql, args).fetchall()

    def tx(self):
        return _Tx(self.c)


class _Tx:
    def __init__(self, c):
        self.c = c

    def __enter__(self):
        _lock.acquire()
        self.c.execute("BEGIN IMMEDIATE")
        return self

    def __exit__(self, et, ev, tb):
        try:
            self.c.execute("ROLLBACK" if et else "COMMIT")
        finally:
            _lock.release()


# ---------- Konfiguration ----------
def get_config(c, key, default=None):
    row = c.one("SELECT value FROM config WHERE key=?", (key,))
    return json.loads(row["value"]) if row else default


def set_config(c, key, value):
    c.execute("INSERT INTO config(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
              (key, json.dumps(value)))


# ---------- Profile ----------
def load_profile(c, user_id):
    row = c.one("SELECT data FROM profiles WHERE user_id=?", (user_id,))
    return json.loads(row["data"]) if row else None


def save_profile(c, user_id, data):
    c.execute("INSERT INTO profiles(user_id,data) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data",
              (user_id, json.dumps(data, ensure_ascii=False)))


def now():
    return time.time()
