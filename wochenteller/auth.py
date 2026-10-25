"""Passwörter, Sitzungen, Sperren nach Fehlversuchen.

* Passwörter: scrypt mit eigenem Salt pro Konto.
* Sitzungen: zufälliges Token im HttpOnly-Cookie, in der Datenbank nur als SHA-256 gespeichert.
* Jede schreibende Anfrage braucht zusätzlich das CSRF-Token der Sitzung im Header.
"""
import base64
import hashlib
import hmac
import re
import secrets
import threading
import time

SESSION_DAYS = 30
SESSION_COOKIE = "wt_session"
MIN_PASSWORD = 8
USERNAME_RE = re.compile(r"^[A-Za-z0-9ÄÖÜäöüß._-]{3,32}$")
_N, _R, _P = 2 ** 14, 8, 1


def hash_password(pw):
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(pw.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=32)
    return "scrypt${}${}${}${}${}".format(_N, _R, _P, base64.b64encode(salt).decode(), base64.b64encode(dk).decode())


def verify_password(pw, stored):
    try:
        alg, n, r, p, salt, dk = stored.split("$")
        if alg != "scrypt":
            return False
        calc = hashlib.scrypt(pw.encode(), salt=base64.b64decode(salt), n=int(n), r=int(r), p=int(p),
                              dklen=len(base64.b64decode(dk)))
        return hmac.compare_digest(calc, base64.b64decode(dk))
    except Exception:
        return False


# Wird bei unbekannten Benutzernamen geprüft, damit die Antwortzeit nichts verrät.
_DUMMY_HASH = hash_password(secrets.token_urlsafe(12))


def password_problem(pw, username=""):
    if len(pw) < MIN_PASSWORD:
        return f"Das Passwort muss mindestens {MIN_PASSWORD} Zeichen lang sein."
    if len(pw) > 200:
        return "Das Passwort ist zu lang."
    if username and pw.lower() == username.lower():
        return "Das Passwort darf nicht dem Benutzernamen entsprechen."
    if pw.lower() in {"12345678", "123456789", "passwort", "password", "wochenteller", "qwertzui", "00000000"}:
        return "Dieses Passwort ist zu leicht zu erraten."
    return None


def username_problem(u):
    if not USERNAME_RE.match(u or ""):
        return "Der Benutzername muss 3–32 Zeichen lang sein (Buchstaben, Ziffern, Punkt, Binde- oder Unterstrich)."
    return None


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ---------- Drosselung pro IP (im Speicher) ----------
class Throttle:
    def __init__(self, limit, window):
        self.limit, self.window = limit, window
        self.hits = {}
        self.lock = threading.Lock()

    def blocked(self, key):
        with self.lock:
            ts = [t for t in self.hits.get(key, []) if t > time.time() - self.window]
            self.hits[key] = ts
            return len(ts) >= self.limit

    def hit(self, key):
        with self.lock:
            self.hits.setdefault(key, []).append(time.time())

    def reset(self, key):
        with self.lock:
            self.hits.pop(key, None)


login_ip_throttle = Throttle(limit=10, window=15 * 60)
signup_ip_throttle = Throttle(limit=5, window=60 * 60)


def lock_seconds(failed):
    """Ab dem 5. Fehlversuch in Folge wächst die Sperre: 1, 2, 4 … Minuten, höchstens 1 Stunde."""
    if failed < 5:
        return 0
    return min(3600, 60 * 2 ** (failed - 5))


# ---------- Sitzungen ----------
def create_session(c, user_id, user_agent=""):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(24)
    t = time.time()
    c.execute("INSERT INTO sessions(token_hash,user_id,csrf,created,expires,last_seen,user_agent) VALUES(?,?,?,?,?,?,?)",
              (sha(token), user_id, csrf, t, t + SESSION_DAYS * 86400, t, (user_agent or "")[:200]))
    c.execute("DELETE FROM sessions WHERE expires<?", (t,))
    return token, csrf


def get_session(c, token):
    if not token or len(token) > 100:
        return None
    row = c.one("""SELECT s.token_hash, s.csrf, s.expires, s.last_seen, u.* FROM sessions s
                   JOIN users u ON u.id=s.user_id WHERE s.token_hash=?""", (sha(token),))
    if not row or row["expires"] < time.time() or row["disabled"]:
        return None
    t = time.time()
    if t - row["last_seen"] > 600:  # gleitende Verlängerung, höchstens alle 10 Minuten geschrieben
        c.execute("UPDATE sessions SET last_seen=?, expires=? WHERE token_hash=?",
                  (t, t + SESSION_DAYS * 86400, row["token_hash"]))
    return row


def end_session(c, token):
    if token:
        c.execute("DELETE FROM sessions WHERE token_hash=?", (sha(token),))


def end_all_sessions(c, user_id, except_token=None):
    if except_token:
        c.execute("DELETE FROM sessions WHERE user_id=? AND token_hash<>?", (user_id, sha(except_token)))
    else:
        c.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))


def new_code(digits=6):
    return "".join(secrets.choice("0123456789") for _ in range(digits))


def new_invite_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    raw = "".join(secrets.choice(alphabet) for _ in range(10))
    return raw[:5] + "-" + raw[5:]
