"""Rezeptdatenbank.

R(id, name, emoji, tags, minuten, geräte, zutaten, schritte, type='m'|'f', season='9-12', tip=None)

* Zutatenmengen gelten pro Portion.
* Geräte: Leerzeichen trennt Pflicht-Gruppen, Buchstaben in einer Gruppe sind Alternativen
  (H Herd, B Backrohr, A Airfryer, M Mikrowelle, W Wasserkocher, X Mixer/Pürierstab,
  R Reiskocher, S Slow Cooker, T Toaster).
* In Schritten wird {zutat} durch Menge + Name für die gekochten Portionen ersetzt,
  {=350 ml} durch die auf die Portionen hochgerechnete Menge.
* season: Monate, in denen das Gericht Saison hat (z. B. '9-12' oder '10-3').
"""

RECIPES = []


def R(id, n, e, tags, t, need, ings, steps, type="m", season=None, tip=None):
    RECIPES.append({
        "id": id, "n": n, "e": e, "s": tags.split() if tags else [], "t": t, "need": need,
        "i": ings, "st": steps, "type": type, "season": season, "tip": tip,
    })


from . import oesterreich, italien, mediterran, asien, welt, vegan, fruehstueck  # noqa: E402,F401
