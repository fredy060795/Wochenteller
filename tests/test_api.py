import unittest
from datetime import date, datetime, timedelta

from wochenteller import auth, db, scheduler
from tests.helpers import AppServer, FakeGateway, FakeSMTP, find_code

PW = "geheim-123"


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = AppServer()
        cls.smtp = FakeSMTP()
        cls.gw = FakeGateway()
        cls.admin = cls.app.client()
        st, res = cls.admin.req("POST", "setup", {"setup_code": "ABCDE-FGHIJ", "username": "fredy", "display_name": "Fredy", "password": PW})
        assert st == 200, res
        cls.admin.csrf = res["csrf"]
        cls.admin.ok("PUT", "admin/config", {
            "smtp": {"host": "127.0.0.1", "port": cls.smtp.port, "security": "none", "from_addr": "wt@example.org"},
            "whatsapp": {"enabled": True, "gateway_url": cls.gw.url, "country_code": "43"},
            "public_url": "http://wochenteller.local:8080"})

    @classmethod
    def tearDownClass(cls):
        cls.app.close()
        cls.smtp.shutdown()
        cls.gw.shutdown()

    def new_user(self, name):
        r = self.admin.ok("POST", "admin/users", {"username": name, "display_name": name.title()})
        c = self.app.client()
        st, res = c.login(name, r["temp_password"])
        self.assertEqual(st, 200)
        st, res = c.req("GET", "state")
        self.assertEqual(res.get("code"), "password_change_required")
        c.ok("POST", "account/password", {"current": r["temp_password"], "new": PW})
        return c

    def test_setup_only_once(self):
        st, _ = self.app.client().req("POST", "setup", {"setup_code": "ABCDE-FGHIJ", "username": "boese", "password": PW})
        self.assertEqual(st, 403)

    def test_registration_closed_by_default(self):
        st, _ = self.app.client().req("POST", "register", {"username": "fremd", "password": PW})
        self.assertEqual(st, 403)

    def test_invite_registration(self):
        self.admin.ok("PUT", "admin/config", {"registration": "invite"})
        try:
            code = self.admin.ok("POST", "admin/invites", {})["code"]
            c = self.app.client()
            st, _ = c.req("POST", "register", {"username": "gast1", "password": PW, "invite": "FALSCH-CODE"})
            self.assertEqual(st, 403)
            st, res = c.req("POST", "register", {"username": "gast1", "password": PW, "invite": code})
            self.assertEqual(st, 200, res)
            st, _ = self.app.client().req("POST", "register", {"username": "gast2", "password": PW, "invite": code})
            self.assertEqual(st, 403)  # Code nur einmal verwendbar
        finally:
            self.admin.ok("PUT", "admin/config", {"registration": "closed"})

    def test_users_are_isolated(self):
        anna, ben = self.new_user("anna"), self.new_user("ben")
        monday = date.today() - timedelta(days=date.today().weekday())
        anna.ok("PUT", "profile", {"persons": 2, "appliances": ["Herd", "Backrohr"]})
        anna.ok("POST", "plan/generate", {"start": monday.isoformat(), "weeks": 2})
        anna.ok("PUT", "fridge", {"id": "nudeln", "qty": 500})
        cid = anna.ok("POST", "shopping/custom", {"week": monday.isoformat(), "text": "Geheimer Kaffee"})["id"]
        ra = anna.ok("GET", f"plan?from={monday}&to={monday + timedelta(days=14)}")
        self.assertGreater(len(ra["rows"]), 10)
        rb = ben.ok("GET", f"plan?from={monday}&to={monday + timedelta(days=14)}")
        self.assertEqual(rb["rows"], [])
        self.assertEqual(ben.ok("GET", "state")["profile"]["fridge"], {})
        self.assertEqual(ben.ok("GET", f"shopping?week={monday}")["custom"], [])
        # fremden Artikel löschen/abhaken wirkt nicht
        ben.req("DELETE", f"shopping/custom/{cid}")
        ben.req("POST", f"shopping/custom/{cid}", {"checked": True})
        own = anna.ok("GET", f"shopping?week={monday}")["custom"]
        self.assertEqual([(x["text"], x["checked"]) for x in own], [("Geheimer Kaffee", 0)])
        # Nicht-Admins kommen nicht an die Verwaltung
        for path in ("admin/users", "admin/config"):
            st, _ = ben.req("GET", path)
            self.assertEqual(st, 403)
        st, _ = ben.req("PUT", "admin/users/1", {"is_admin": False})
        self.assertEqual(st, 403)
        # Anmeldung mit fremdem Passwort/Benutzer klappt nicht
        st, _ = self.app.client().login("anna", "falsch-falsch")
        self.assertEqual(st, 401)

    def test_csrf_and_origin(self):
        c = self.new_user("carla")
        st, res = c.req("PUT", "profile", {"persons": 3}, csrf=False)
        self.assertEqual((st, res.get("code")), (403, "csrf"))
        st, res = c.req("PUT", "profile", {"persons": 3}, headers={"Origin": "http://evil.example"})
        self.assertEqual(st, 403)
        self.assertEqual(c.ok("PUT", "profile", {"persons": 3})["profile"]["persons"], 3)

    def test_lockout(self):
        self.new_user("dora")
        for _ in range(5):
            st, _ = self.app.client().login("dora", "falsch-falsch")
            self.assertEqual(st, 401)
        auth.login_ip_throttle.reset("127.0.0.1")
        st, res = self.app.client().login("dora", PW)
        self.assertEqual(st, 429, res)  # gesperrt trotz richtigem Passwort
        with db.connect() as c:
            c.execute("UPDATE users SET locked_until=0 WHERE username='dora'")
        st, _ = self.app.client().login("dora", PW)
        self.assertEqual(st, 200)
        auth.login_ip_throttle.reset("127.0.0.1")

    def test_logout_invalidates_session(self):
        c = self.new_user("emil")
        c.ok("POST", "logout")
        st, _ = c.req("GET", "state")
        self.assertEqual(st, 401)

    def test_plan_actions_and_shopping(self):
        c = self.new_user("fritz")
        today = date.today()
        c.ok("POST", "plan/generate", {"start": today.isoformat(), "weeks": 1})
        rows = c.ok("GET", f"plan?from={today}&to={today + timedelta(days=7)}")["rows"]
        row = rows[0]
        rid = c.ok("POST", "plan/swap", {"date": row["date"], "slot": row["slot"]})["recipe_id"]
        self.assertNotEqual(rid, row["recipe_id"])
        alt = c.ok("GET", f"alternatives?date={row['date']}&slot={row['slot']}")["ids"]
        self.assertTrue(alt)
        c.ok("POST", "plan/set", {"date": row["date"], "slot": row["slot"], "recipe_id": "carbonara"})
        week = today - timedelta(days=today.weekday())
        shop = c.ok("GET", f"shopping?week={week}")
        self.assertTrue(shop["items"])
        item = shop["items"][0]["id"]
        c.ok("POST", "shopping/check", {"week": week.isoformat(), "item": item, "checked": True})
        moved = c.ok("POST", "shopping/finish", {"week": week.isoformat()})["moved"]
        self.assertEqual(moved, [item])
        self.assertIn(item, c.ok("GET", "state")["profile"]["fridge"])
        before = c.ok("GET", "state")["profile"]["cooklog"]
        c.ok("POST", "plan/cook", {"date": row["date"], "slot": row["slot"]})
        st = c.ok("GET", "state")["profile"]
        self.assertEqual(st["cooklog"]["carbonara"]["n"], before.get("carbonara", {}).get("n", 0) + 1)
        st, _ = c.req("POST", "plan/swap", {"date": row["date"], "slot": row["slot"]})
        self.assertEqual(st, 400)  # gekocht → nicht mehr tauschbar
        c.ok("POST", "plan/cook", {"date": row["date"], "slot": row["slot"], "undo": True})
        c.ok("POST", "plan/skip", {"date": row["date"], "slot": row["slot"]})
        st, _ = c.req("POST", "plan/cook", {"date": row["date"], "slot": row["slot"]})
        self.assertEqual(st, 404)

    def test_verify_and_send(self):
        c = self.new_user("gerda")
        n0 = len(self.smtp.messages)
        st, res = c.req("POST", "send", {"kind": "today", "channel": "email"})
        self.assertNotEqual(st, 200)  # noch nicht bestätigt
        c.ok("POST", "contact/email", {"email": "gerda@example.org"})
        code = find_code(self.smtp.messages[-1]["data"])
        st, _ = c.req("POST", "contact/email/verify", {"code": "000000" if code != "000000" else "111111"})
        self.assertEqual(st, 400)
        c.ok("POST", "contact/email/verify", {"code": code})
        self.assertTrue(c.ok("GET", "state")["user"]["email_verified"])
        c.ok("POST", "contact/phone", {"phone": "0664 1234567"})
        msg = self.gw.sent[-1]
        self.assertEqual(msg["phone"], "436641234567")
        c.ok("POST", "contact/phone/verify", {"code": find_code(msg["message"])})
        today = date.today()
        c.ok("POST", "plan/generate", {"start": today.isoformat(), "weeks": 1})
        week = (today - timedelta(days=today.weekday())).isoformat()
        c.ok("POST", "send", {"kind": "shopping", "channel": "email", "week": week})
        self.assertIn("gerda@example.org", self.smtp.messages[-1]["to"])
        self.assertIn("Einkaufsliste", self.smtp.messages[-1]["data"])
        self.assertGreater(len(self.smtp.messages), n0)
        c.ok("POST", "send", {"kind": "shopping", "channel": "whatsapp", "week": week})
        self.assertIn("Einkaufsliste KW", self.gw.sent[-1]["message"])
        self.assertIn("http://wochenteller.local:8080", self.gw.sent[-1]["message"])

    def test_scheduler_sends_once(self):
        c = self.new_user("hans")
        c.ok("POST", "contact/phone", {"phone": "+43 660 7654321"})
        c.ok("POST", "contact/phone/verify", {"code": find_code(self.gw.sent[-1]["message"])})
        today = date.today()
        c.ok("POST", "plan/generate", {"start": today.isoformat(), "weeks": 2})
        c.ok("PUT", "profile", {"notify": {"daily": {"enabled": True, "time": "07:00", "channels": ["whatsapp"]},
                                           "shopping": {"enabled": True, "weekday": today.weekday(), "time": "07:00", "channels": ["whatsapp"]}}})
        now = datetime.combine(today, datetime.min.time()).replace(hour=7, minute=30)
        before = len([m for m in self.gw.sent if m["phone"] == "436607654321"])
        scheduler.tick(now)
        scheduler.tick(now + timedelta(minutes=5))
        mine = [m for m in self.gw.sent if m["phone"] == "436607654321"][before:]
        kinds = sorted("Einkaufsliste" in m["message"] for m in mine)
        self.assertEqual(kinds, [False, True])  # je einmal Tagesmenü und Einkaufsliste
        self.assertTrue(all(m["request_id"].startswith("wt-") for m in mine))
        # außerhalb des Zeitfensters nichts
        scheduler.tick(now.replace(hour=5))
        self.assertEqual(len([m for m in self.gw.sent if m["phone"] == "436607654321"][before:]), 2)

    def test_static_and_headers(self):
        import urllib.request
        with urllib.request.urlopen(self.app.base + "/") as r:
            self.assertIn("Content-Security-Policy", r.headers)
            self.assertIn(b"app.js", r.read())
        with urllib.request.urlopen(self.app.base + "/app.js") as r:
            self.assertEqual(r.status, 200)
        st, _ = self.app.client().req("GET", "state")
        self.assertEqual(st, 401)


if __name__ == "__main__":
    unittest.main()
