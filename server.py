# -*- coding: utf-8 -*-
"""Wochenteller – lokaler Server mit SQLite-Datenbank (nur Python-Standardbibliothek).
Start: python server.py   ->   http://localhost:5040
"""
import json, os, socket, sqlite3, sys, threading, uuid, webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

PORT = 5040
BASE = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE, "app")
DATA_DIR = os.path.join(BASE, "data")
DB_PATH = os.path.join(DATA_DIR, "wochenteller.db")
SEED_PATH = os.path.join(DATA_DIR, "recipes_seed.json")
LOCK = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id         TEXT PRIMARY KEY,
  name       TEXT NOT NULL,
  color      INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS user_state (
  user_id    TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  state      TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS recipes (
  id          TEXT PRIMARY KEY,
  name        TEXT NOT NULL,
  emoji       TEXT,
  meal_type   TEXT NOT NULL DEFAULT 'm',   -- m = Hauptgericht, f = Frühstück
  minutes     INTEGER NOT NULL DEFAULT 30,
  styles      TEXT NOT NULL DEFAULT '',    -- z.B. 'oesterr familie protein'
  appliances  TEXT NOT NULL DEFAULT '',    -- Geräte-Code, z.B. 'H' oder 'BA H'
  ingredients TEXT NOT NULL,               -- JSON: {"nudeln":125,"zwiebel":0.5}
  steps       TEXT NOT NULL,               -- JSON: ["Schritt 1","Schritt 2"]
  source      TEXT NOT NULL DEFAULT 'standard'
);
CREATE TABLE IF NOT EXISTS user_recipes (
  user_id      TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  recipe_id    TEXT NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
  favorite     INTEGER NOT NULL DEFAULT 0,
  times_cooked INTEGER NOT NULL DEFAULT 0,
  last_cooked  TEXT,
  PRIMARY KEY (user_id, recipe_id)
);
CREATE VIEW IF NOT EXISTS gespeicherte_rezepte AS
  SELECT u.name AS person, r.name AS rezept, ur.favorite AS gemerkt,
         ur.times_cooked AS mal_gekocht, ur.last_cooked AS zuletzt_gekocht
  FROM user_recipes ur JOIN users u ON u.id = ur.user_id JOIN recipes r ON r.id = ur.recipe_id
  ORDER BY u.name, ur.favorite DESC, ur.times_cooked DESC;
"""


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with LOCK, connect() as con:
        con.executescript(SCHEMA)
        count = con.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
        if count == 0 and os.path.exists(SEED_PATH):
            with open(SEED_PATH, encoding="utf-8") as f:
                seed = json.load(f)
            con.executemany(
                "INSERT INTO recipes (id,name,emoji,meal_type,minutes,styles,appliances,ingredients,steps) VALUES (?,?,?,?,?,?,?,?,?)",
                [(r["id"], r["n"], r["e"], r["type"], r["t"], " ".join(r["s"]), r["need"],
                  json.dumps(r["i"], ensure_ascii=False), json.dumps(r["st"], ensure_ascii=False)) for r in seed])
            print(f"  {len(seed)} Rezepte in die Datenbank geladen.")


def recipe_out(row):
    return {"id": row["id"], "n": row["name"], "e": row["emoji"], "type": row["meal_type"], "t": row["minutes"],
            "s": [s for s in (row["styles"] or "").split() if s], "need": row["appliances"] or "",
            "i": json.loads(row["ingredients"]), "st": json.loads(row["steps"])}


def sync_user_recipes(con, user_id, state):
    """Gemerkte und gekochte Rezepte aus dem App-Zustand in die Tabelle user_recipes schreiben."""
    known = {r[0] for r in con.execute("SELECT id FROM recipes")}
    saved = {str(x) for x in (state.get("saved") or []) if str(x) in known}
    log = {str(k): v for k, v in (state.get("cookLog") or {}).items() if str(k) in known and isinstance(v, dict)}
    con.execute("DELETE FROM user_recipes WHERE user_id = ?", (user_id,))
    rows = []
    for rid in saved | set(log):
        entry = log.get(rid, {})
        rows.append((user_id, rid, 1 if rid in saved else 0, int(entry.get("n") or 0), entry.get("last")))
    con.executemany("INSERT INTO user_recipes (user_id,recipe_id,favorite,times_cooked,last_cooked) VALUES (?,?,?,?,?)", rows)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=APP_DIR, **kw)

    def log_message(self, fmt, *args):
        pass  # ruhige Konsole

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8") or "null") if n else None

    def _parts(self):
        return [p for p in urlparse(self.path).path.split("/") if p]

    def do_GET(self):
        p = self._parts()
        if not p or p[0] != "api":
            return super().do_GET()
        try:
            with LOCK, connect() as con:
                if p[1:] == ["ping"]:
                    return self._json({"ok": True})
                if p[1:] == ["profiles"]:
                    rows = con.execute("SELECT id,name,color FROM users ORDER BY created_at").fetchall()
                    return self._json([dict(r) for r in rows])
                if p[1:] == ["recipes"]:
                    rows = con.execute("SELECT * FROM recipes ORDER BY meal_type DESC, rowid").fetchall()
                    return self._json([recipe_out(r) for r in rows])
                if len(p) == 3 and p[1] == "state":
                    row = con.execute("SELECT state FROM user_state WHERE user_id=?", (p[2],)).fetchone()
                    return self._json({"state": json.loads(row["state"]) if row else None})
                if len(p) == 4 and p[1] == "users" and p[3] == "recipes":
                    rows = con.execute("""SELECT r.id, r.name, ur.favorite, ur.times_cooked, ur.last_cooked
                        FROM user_recipes ur JOIN recipes r ON r.id=ur.recipe_id WHERE ur.user_id=?
                        ORDER BY ur.favorite DESC, ur.times_cooked DESC""", (p[2],)).fetchall()
                    return self._json([dict(r) for r in rows])
            self._json({"error": "nicht gefunden"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_POST(self):
        p = self._parts()
        try:
            if p == ["api", "profiles"]:
                data = self._body() or {}
                name = str(data.get("name", "")).strip()[:30]
                if not name:
                    return self._json({"error": "Name fehlt"}, 400)
                with LOCK, connect() as con:
                    color = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                    uid = "u" + uuid.uuid4().hex[:10]
                    con.execute("INSERT INTO users (id,name,color) VALUES (?,?,?)", (uid, name, color))
                return self._json({"id": uid, "name": name, "color": color}, 201)
            self._json({"error": "nicht gefunden"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_PUT(self):
        p = self._parts()
        try:
            if len(p) == 3 and p[:2] == ["api", "state"]:
                state = self._body()
                if not isinstance(state, dict):
                    return self._json({"error": "ungültig"}, 400)
                with LOCK, connect() as con:
                    if not con.execute("SELECT 1 FROM users WHERE id=?", (p[2],)).fetchone():
                        return self._json({"error": "Person unbekannt"}, 404)
                    con.execute("""INSERT INTO user_state (user_id,state,updated_at) VALUES (?,?,datetime('now','localtime'))
                        ON CONFLICT(user_id) DO UPDATE SET state=excluded.state, updated_at=excluded.updated_at""",
                                (p[2], json.dumps(state, ensure_ascii=False)))
                    sync_user_recipes(con, p[2], state)
                return self._json({"ok": True})
            self._json({"error": "nicht gefunden"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def do_DELETE(self):
        p = self._parts()
        try:
            if len(p) == 3 and p[:2] == ["api", "profiles"]:
                with LOCK, connect() as con:
                    con.execute("DELETE FROM users WHERE id=?", (p[2],))
                return self._json({"ok": True})
            self._json({"error": "nicht gefunden"}, 404)
        except Exception as e:
            self._json({"error": str(e)}, 500)


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None


def main():
    print("\n  Wochenteller startet ...")
    init_db()
    try:
        server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError:
        print(f"\n  Port {PORT} ist schon belegt. Läuft Wochenteller vielleicht schon in einem anderen Fenster?")
        input("\n  Enter drücken zum Beenden ...")
        sys.exit(1)
    url = f"http://localhost:{PORT}"
    print(f"\n  Läuft auf:        {url}")
    ip = lan_ip()
    if ip:
        print(f"  Im WLAN (Handy):  http://{ip}:{PORT}")
    print(f"  Datenbank:        {DB_PATH}")
    print("\n  Zum Beenden dieses Fenster schließen oder Strg+C drücken.\n")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Beendet.")


if __name__ == "__main__":
    main()
