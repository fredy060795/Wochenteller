"""Rezept- und Zutatenkatalog plus alles, was Planer und Oberfläche über Rezepte wissen müssen."""
import re

from .data.ingredients import INGREDIENTS, CATEGORY_ORDER, PANTRY_ORDER, DEFAULT_PANTRY
from .data.recipes import RECIPES

APPLIANCE_CODES = {"H": "Herd", "B": "Backrohr", "A": "Airfryer", "M": "Mikrowelle", "W": "Wasserkocher",
                   "X": "Mixer", "R": "Reiskocher", "S": "Slow Cooker", "T": "Toaster"}
APPLIANCES = [["Herd", "🍳", "Herd / Kochfeld"], ["Backrohr", "🥧", "Backrohr"], ["Airfryer", "🍟", "Airfryer"],
              ["Mikrowelle", "⏲️", "Mikrowelle"], ["Wasserkocher", "🫖", "Wasserkocher"],
              ["Mixer", "🥤", "Mixer / Pürierstab"], ["Reiskocher", "🍚", "Reiskocher"],
              ["Slow Cooker", "🍲", "Slow Cooker"], ["Toaster", "🍞", "Toaster"]]
STORES = [["hofer", "Hofer", 1.00], ["lidl", "Lidl", 0.99], ["penny", "Penny", 1.01], ["billa", "Billa", 1.14],
          ["spar", "Spar", 1.12], ["interspar", "Interspar", 1.09], ["mpreis", "MPreis", 1.17],
          ["unimarkt", "Unimarkt", 1.13]]
STORE_MULT = {s[0]: s[2] for s in STORES}
STORE_NAME = {s[0]: s[1] for s in STORES}
DIETS = [["alles", "🍽️", "Ich esse alles"], ["vegetarisch", "🥕", "Vegetarisch"],
         ["pescetarisch", "🐟", "Pescetarisch"], ["vegan", "🥑", "Vegan"]]
EXTRAS = [["glutenfrei", "🌾", "Glutenfrei"], ["laktosefrei", "🥛", "Laktosefrei"]]
ALLERGIES = [["nuss", "🌰", "Nüsse"], ["erdnuss", "🥜", "Erdnüsse"], ["ei", "🥚", "Eier"], ["fisch", "🐟", "Fisch"],
             ["schalentier", "🦐", "Schalentiere"], ["soja", "🫘", "Soja"]]
PROTEINS = [["rind", "🥩", "Rindfleisch"], ["huhn", "🍗", "Huhn & Pute"], ["schwein", "🥓", "Schweinefleisch"],
            ["fisch", "🐟", "Fisch & Meeresfrüchte"], ["huelse", "🫘", "Hülsenfrüchte"], ["tofu", "🥡", "Tofu"]]
CUISINES = ["oesterr", "ital", "medi", "asia", "mex", "orient", "indisch"]
STYLES = [["oesterr", "🥨", "Österreichisch"], ["ital", "🍝", "Italienisch"], ["medi", "🫒", "Mediterran"],
          ["asia", "🥢", "Asiatisch"], ["mex", "🌮", "Mexikanisch"], ["orient", "🧆", "Orientalisch"],
          ["indisch", "🍛", "Indisch"], ["schnell", "⏱️", "Schnell & einfach", "bis 25 Minuten"],
          ["leicht", "🥗", "Leicht"], ["protein", "💪", "Proteinreich"], ["familie", "🏡", "Familienlieblinge"],
          ["guenstig", "💶", "Extra günstig"], ["suess", "🥞", "Süße Hauptspeisen", "Kaiserschmarrn & Co."],
          ["saison", "🍂", "Saisonal", "Kürbis im Herbst, Spargel im Frühling"],
          ["mealprep", "📦", "Meal-Prep", "einmal kochen, zweimal essen"]]
MEALS = [["abend", "🌙", "Nur Abendessen", "1 Mahlzeit pro Tag"],
         ["mittag_abend", "☀️", "Mittag & Abend", "2 Mahlzeiten pro Tag"],
         ["alle", "🌅", "Frühstück, Mittag & Abend", "3 Mahlzeiten pro Tag"]]
MEAL_SLOTS = {"abend": ["abend"], "mittag_abend": ["mittag", "abend"], "alle": ["frueh", "mittag", "abend"]}
SLOT_LABEL = {"frueh": "Frühstück", "mittag": "Mittagessen", "abend": "Abendessen"}
KCAL_SHARE = {"alle": {"frueh": .25, "mittag": .35, "abend": .4}, "mittag_abend": {"mittag": .4, "abend": .4},
              "abend": {"abend": .4}}
RECIPE_TAGS = set(CUISINES) | {"leicht", "protein", "familie", "suess", "guenstig", "schnell"}

TOKEN_RE = re.compile(r"\{([^}]+)\}")
TIMER_RE = re.compile(r"(\d+)(?:\s*[–-]\s*(\d+))?\s*(Minuten|Minute|Min\.|Stunden|Stunde)")

INGS = INGREDIENTS
RBY = {}


def _months(spec):
    if not spec:
        return None
    a, b = (int(x) for x in spec.split("-"))
    return [m for m in range(1, 13) if (a <= m <= b if a <= b else (m >= a or m <= b))]


def step_timer(text):
    """Erste Zeitangabe in einem Schritt als Sekunden (für den Kochmodus), sonst None."""
    m = TIMER_RE.search(text)
    if not m:
        return None
    n = int(m.group(1))
    return n * 3600 if m.group(3).startswith("Stunde") else n * 60


def validate():
    """Liefert eine Liste von Fehlern im Katalog (leer = alles gut)."""
    errors, seen = [], set()
    for r in RECIPES:
        rid = r["id"]
        if rid in seen:
            errors.append(f"{rid}: doppelte ID")
        seen.add(rid)
        if not re.fullmatch(r"[a-z0-9-]+", rid):
            errors.append(f"{rid}: ungültige ID")
        for iid, q in r["i"].items():
            if iid not in INGS:
                errors.append(f"{rid}: unbekannte Zutat {iid}")
            if not (isinstance(q, (int, float)) and q > 0):
                errors.append(f"{rid}: ungültige Menge für {iid}")
        for g in r["need"].split():
            for c in g:
                if c not in APPLIANCE_CODES:
                    errors.append(f"{rid}: unbekanntes Gerät {c}")
        for t in r["s"]:
            if t not in RECIPE_TAGS:
                errors.append(f"{rid}: unbekannter Tag {t}")
        if r["type"] not in ("m", "f"):
            errors.append(f"{rid}: unbekannter Typ")
        if len(r["st"]) < 3:
            errors.append(f"{rid}: zu wenige Schritte")
        for s in r["st"]:
            for tok in TOKEN_RE.findall(s):
                if tok.startswith("="):
                    if not re.fullmatch(r"=\d+(?:[.,]\d+)?\s*(ml|g|l|kg|EL|TL|Stk)", tok):
                        errors.append(f"{rid}: ungültige Mengenangabe {{{tok}}}")
                elif tok not in r["i"]:
                    errors.append(f"{rid}: Platzhalter {{{tok}}} ist keine Zutat des Rezepts")
        if r.get("season"):
            try:
                _months(r["season"])
            except Exception:
                errors.append(f"{rid}: ungültige Saison")
    return errors


def _prepare():
    for r in RECIPES:
        r["months"] = _months(r.get("season"))
        r["timers"] = [step_timer(s) for s in r["st"]]
        r["main"] = [iid for iid in r["i"] if not INGS[iid]["minor"]]
        prot = set()
        for iid in r["i"]:
            for t in INGS[iid]["tags"]:
                if t in ("rind", "huhn", "schwein", "fisch", "schalentier", "huelse", "tofu"):
                    prot.add("fisch" if t == "schalentier" else t)
        r["prot"] = sorted(prot) or ["veggie"]
        RBY[r["id"]] = r


_prepare()


def public_catalog():
    """Alles, was die Oberfläche braucht – einmal laden und cachen."""
    return {
        "ingredients": INGS,
        "recipes": [{k: r[k] for k in ("id", "n", "e", "s", "t", "need", "i", "st", "type", "season", "tip", "timers", "prot")}
                    for r in RECIPES],
        "options": {
            "appliances": APPLIANCES, "applianceCodes": APPLIANCE_CODES, "stores": STORES, "diets": DIETS,
            "extras": EXTRAS, "allergies": ALLERGIES, "proteins": PROTEINS, "styles": STYLES, "meals": MEALS,
            "mealSlots": MEAL_SLOTS, "slotLabel": SLOT_LABEL, "kcalShare": KCAL_SHARE,
            "categoryOrder": CATEGORY_ORDER, "pantryOrder": PANTRY_ORDER, "defaultPantry": DEFAULT_PANTRY,
        },
    }
