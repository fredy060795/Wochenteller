"""Start:  py -m wochenteller            (Server auf Port 8080)
Hilfe:  py -m wochenteller --help

Befehle:
  py -m wochenteller reset-password NAME   neues Passwort für ein Konto setzen
  py -m wochenteller make-admin NAME       Konto zur Verwaltung machen
  py -m wochenteller check                 Rezeptkatalog prüfen
"""
import argparse
import getpass
import os
import socket
import sys

from . import auth, catalog, db, scheduler, server

DEFAULT_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daten", "wochenteller.db")


def local_ips():
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(ips)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="wochenteller", description="Wochenteller – Rezept-, Wochen- und Einkaufsplaner")
    ap.add_argument("command", nargs="?", default="serve", choices=["serve", "reset-password", "make-admin", "check"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--host", default=os.environ.get("WT_HOST", "0.0.0.0"), help="Adresse (Standard 0.0.0.0 = im ganzen Heimnetz)")
    ap.add_argument("--port", type=int, default=int(os.environ.get("WT_PORT", "8080")))
    ap.add_argument("--db", default=os.environ.get("WT_DB", DEFAULT_DB), help="Pfad zur Datenbank")
    ap.add_argument("--cert", default=os.environ.get("WT_CERT"), help="TLS-Zertifikat (PEM) für HTTPS")
    ap.add_argument("--key", default=os.environ.get("WT_KEY"), help="Privater Schlüssel zum Zertifikat")
    ap.add_argument("--trust-proxy", action="store_true", default=os.environ.get("WT_TRUST_PROXY") == "1",
                    help="hinter einem Reverse-Proxy: X-Forwarded-* auswerten")
    ap.add_argument("--secure-cookies", action="store_true", default=os.environ.get("WT_SECURE_COOKIES") == "1",
                    help="Cookies nur über HTTPS (bei Reverse-Proxy mit HTTPS setzen)")
    a = ap.parse_args(argv)

    if a.command == "check":
        errs = catalog.validate()
        print(f"{len(catalog.RECIPES)} Rezepte, {len(catalog.INGS)} Zutaten, {len(errs)} Fehler")
        for e in errs:
            print(" -", e)
        return 1 if errs else 0

    db.init(a.db)
    if a.command in ("reset-password", "make-admin"):
        with db.connect() as c:
            u = c.one("SELECT * FROM users WHERE username=?", (a.name or "",))
            if not u:
                print("Kein Konto mit diesem Namen.")
                return 1
            if a.command == "make-admin":
                c.execute("UPDATE users SET is_admin=1, disabled=0 WHERE id=?", (u["id"],))
                print(f"{u['username']} ist jetzt Verwaltung.")
                return 0
            pw = getpass.getpass("Neues Passwort: ")
            err = auth.password_problem(pw, u["username"])
            if err:
                print(err)
                return 1
            c.execute("UPDATE users SET pw_hash=?, must_change_pw=0, failed_logins=0, locked_until=0 WHERE id=?",
                      (auth.hash_password(pw), u["id"]))
            auth.end_all_sessions(c, u["id"])
            print("Passwort geändert, alle Sitzungen abgemeldet.")
            return 0

    errs = catalog.validate()
    if errs:
        print("Rezeptkatalog fehlerhaft:", *errs[:10], sep="\n - ")
        return 1
    server.SETTINGS.trust_proxy = a.trust_proxy
    server.SETTINGS.secure_cookies = a.secure_cookies
    with db.connect() as c:
        has_users = c.one("SELECT 1 FROM users LIMIT 1") is not None
    httpd = server.make_server(a.host, a.port, a.cert, a.key)
    proto = "https" if a.cert else "http"
    print("=" * 62)
    print(" Wochenteller läuft")
    print(f"   Auf diesem PC:   {proto}://localhost:{a.port}")
    for ip in local_ips():
        print(f"   Im Heimnetz:     {proto}://{ip}:{a.port}")
    print(f"   Datenbank:       {a.db}")
    if not has_users:
        server.SETTINGS.setup_code = auth.new_invite_code()
        print()
        print(f"   ERSTEINRICHTUNG – Einrichtungscode: {server.SETTINGS.setup_code}")
        print("   Öffne die Adresse im Browser und lege mit diesem Code das Verwaltungskonto an.")
    print("   Beenden mit Strg+C")
    print("=" * 62, flush=True)
    sch = scheduler.Scheduler()
    sch.start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        sch.stop.set()
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
