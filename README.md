# Wochenteller

Rezept-, Wochen- und Einkaufsplaner für den eigenen PC. Mehrere Personen können ihn gleichzeitig nutzen. Jede Person hat ihr eigenes Konto mit Passwort und sieht nur ihre eigenen Daten.

- **249 Rezepte** (217 Hauptgerichte, 32 Frühstücke) mit ausführlichen Schritt-für-Schritt-Anleitungen. Mengen in den Schritten werden auf die Portionen umgerechnet.
- **Planung über 1 Woche bis 6 Monate.** Ein Gericht kommt erst nach einer Sperrfrist wieder (bis zu 42 Tage, je nachdem, wie viele Rezepte zu den Einstellungen passen). Gekochte Mahlzeiten bleiben beim Neuplanen erhalten.
- **Budget mit echten Packungen.** Der Planer rechnet mit ganzen Packungen und bevorzugt Gerichte, die angebrochene Packungen aufbrauchen. Haltbares (Reis, Nudeln, Konserven, Tiefkühl) wird in die Folgewochen übernommen statt neu gekauft.
- **Einkaufsliste pro Woche** mit Preisvergleich zwischen Geschäften, Abhaken, eigenen Artikeln, „Eingekauft → in den Vorrat“, Teilen und Drucken.
- **Vorrat/Kühlschrank:** Beim Kochen werden die Zutaten automatisch abgebucht. Die App schlägt vor, was du aus deinen Vorräten kochen kannst.
- **Kochmodus:** großer Text, ein Schritt nach dem anderen, Zutaten-Checkliste, Timer mit Ton und Vibration. Der Bildschirm bleibt an.
- **Ernährung:** vegetarisch, pescetarisch, vegan, laktose- und glutenfrei, Allergien, Abneigungen. Milch, Butter, Obers, Honig, Nudeln, Mehl usw. werden bei Bedarf automatisch ersetzt.
- **Saisonal:** Kürbis im Herbst, Spargel im Frühling.
- **Versand per E-Mail** (eigener SMTP-Server) **und WhatsApp** (über das JARVIS-Gateway): Einkaufsliste, Wochenplan oder Tagesmenü auf Knopfdruck. Auf Wunsch kommt die Einkaufsliste automatisch am Einkaufstag und das Tagesmenü zur gewählten Uhrzeit.

## Starten (Windows)

Voraussetzung: Python 3.9 oder neuer (`py --version`). Zusatzpakete braucht es nicht.

1. Doppelklick auf `start_wochenteller.bat` (oder `py -m wochenteller`)
2. Im Fenster stehen die Adressen, z. B. `http://localhost:8080` und `http://192.168.0.20:8080` für Handys im WLAN.
3. Beim allerersten Start steht dort ein **Einrichtungscode**. Öffne die Adresse, gib den Code ein und lege das Verwaltungskonto an.

Falls Windows fragt: Den Zugriff im **privaten** Netzwerk erlauben, damit Handys im WLAN die App erreichen.

Optionen: `--port 8080`, `--host 0.0.0.0`, `--db Pfad\zur\datei.db`, `--cert`/`--key` für HTTPS (z. B. die Zertifikate aus `JARVIS\certs`). Die Daten liegen standardmäßig in `daten\wochenteller.db`. Zum Sichern genügt es, diese Datei zu kopieren.

Weitere Befehle:

```
py -m wochenteller reset-password NAME   # Passwort neu setzen (falls sich jemand ausgesperrt hat)
py -m wochenteller make-admin NAME       # Konto zur Verwaltung machen
py -m wochenteller check                 # Rezeptkatalog prüfen
```

## Konten und Sicherheit

- Anmeldung mit Benutzername und Passwort (scrypt-Hash, mindestens 8 Zeichen). Die Sitzung liegt in einem HttpOnly-Cookie. Schreibende Anfragen brauchen zusätzlich ein CSRF-Token.
- Nach 5 falschen Passwörtern wird das Konto gesperrt, zuerst 1 Minute, danach mit wachsender Dauer bis zu 1 Stunde. Zusätzlich gibt es eine Drosselung pro Gerät.
- Der Server leitet die Person ausschließlich aus der Sitzung ab. Keine Schnittstelle nimmt eine fremde Benutzer-ID an, außer die Verwaltungsfunktionen, und die prüfen Admin-Rechte.
- **Registrierung** (Verwaltung → Registrierung): *Nur Verwaltung* (Standard, am sichersten), *Mit Einladung* (einmaliger Code, 7 Tage gültig) oder *Offen*.
- Neue Konten aus der Verwaltung bekommen ein vorläufiges Passwort, das beim ersten Anmelden geändert werden muss.
- Im Profil: Passwort ändern, auf anderen Geräten abmelden, Konto löschen.

Wer den Wochenteller aus dem Internet erreichbar machen will, sollte ihn hinter einen Reverse-Proxy mit HTTPS stellen (`--trust-proxy --secure-cookies`) oder direkt `--cert/--key` nutzen.

## E-Mail (eigener SMTP-Server)

Verwaltung → *E-Mail*: Server, Port, Verschlüsselung (STARTTLS/SSL), Benutzer, Passwort und Absender eintragen, dann „Test-E-Mail senden“. Das Passwort wird nie an den Browser zurückgegeben. Jede Person bestätigt ihre Adresse im Profil mit einem Code.

## WhatsApp über JARVIS

Der Wochenteller nutzt das vorhandene Gateway aus `JARVIS\Whatsapp_Buissines` (`start_gateway.bat`, Port 3000). Es nimmt nur Anfragen vom selben PC an, deshalb muss der Wochenteller **auf dem JARVIS-PC laufen**.

1. JARVIS-Gateway starten (WhatsApp muss verbunden sein).
2. Im Wochenteller: Verwaltung → *WhatsApp über JARVIS* → aktivieren (Adresse `http://127.0.0.1:3000/send`) → „Gateway prüfen“ → Test-Nachricht.
3. Jede Person trägt im Profil ihre Handynummer ein und bestätigt sie mit dem Code, den sie per WhatsApp bekommt.

Es gehen nur Nachrichten an bestätigte Nummern. Pro Person und Tag sind es höchstens 40 Nachrichten. Automatische Nachrichten tragen eine feste `request_id`, damit das Gateway Doppelungen erkennt.

## Automatische Nachrichten

Profil → *Automatische Nachrichten*:

- **Einkaufsliste:** am gewählten Einkaufstag zur gewählten Uhrzeit, für die Woche ab dem nächsten Montag (bzw. die laufende, wenn der Einkaufstag ein Montag ist).
- **Tagesmenü:** täglich zur gewählten Uhrzeit. Enthält, was heute gekocht wird und was laut Vorrat noch fehlt.

Jede Nachricht geht pro Zeitraum nur einmal raus, auch nach einem Neustart. War der PC zur Uhrzeit aus, wird sie bis zu 3 Stunden später nachgeholt.

## Entwicklung

```
python3 -m unittest discover -s tests -t .
```

Aufbau: `wochenteller/server.py` (HTTP + API), `planner.py` (Planung, Einkauf, Vorrat), `notify.py` (SMTP/WhatsApp, Nachrichtentexte), `scheduler.py` (Erinnerungen), `auth.py`, `db.py` (SQLite), `data/` (Zutaten und Rezepte), `web/` (Oberfläche ohne Build-Schritt).

Neue Rezepte kommen nach `wochenteller/data/recipes/*.py`. `py -m wochenteller check` prüft Zutaten, Platzhalter (`{zutat}`, `{=350 ml}`) und Geräte.
