"""Planung über Tage, Wochen und Monate, Einkaufslisten und Vorrat.

Zeilen eines Plans (dicts): date (ISO), slot (frueh|mittag|abend), recipe_id, portions (so viele essen mit),
cook_portions (so viel wird gekocht; 0 bei Resten vom Vortag), leftover (1 = Reste), cooked (0/1).
"""
import copy
import math
import random
from datetime import date, timedelta

from .catalog import (CUISINES, DEFAULT_PANTRY, INGS, KCAL_SHARE, MEAL_SLOTS, PROTEINS, RECIPES, RBY, STORE_MULT,
                      STORE_NAME, CATEGORY_ORDER)

MAX_WEEKS = 26
APPL_CODE = {"H": "Herd", "B": "Backrohr", "A": "Airfryer", "M": "Mikrowelle", "W": "Wasserkocher", "X": "Mixer",
             "R": "Reiskocher", "S": "Slow Cooker", "T": "Toaster"}

DEFAULT_PROFILE = {
    "v": 3, "onboarded": False, "persons": 1, "meals": "abend", "days": [0, 1, 2, 3, 4, 5, 6], "budget": 40,
    "kcal": 0, "appliances": ["Herd"], "diet": "alles", "extras": [], "allergies": [],
    "proteins": [p[0] for p in PROTEINS], "styles": [], "pantry": list(DEFAULT_PANTRY), "blocked": [],
    "stores": ["hofer"], "store": None, "fridge": {}, "favorites": [], "hidden": [], "cooklog": {},
    "horizon": 4,
    "notify": {
        "shopping": {"enabled": False, "channels": [], "weekday": 5, "time": "09:00"},
        "daily": {"enabled": False, "channels": [], "time": "16:00"},
    },
}

PROFILE_KEYS = {"onboarded", "persons", "meals", "days", "budget", "kcal", "appliances", "diet", "extras",
                "allergies", "proteins", "styles", "pantry", "blocked", "stores", "store", "horizon", "notify"}


def fresh_profile():
    return copy.deepcopy(DEFAULT_PROFILE)


def normalize_profile(p):
    """Füllt fehlende Felder auf und wirft Unbekanntes/Ungültiges weg."""
    out = fresh_profile()
    if isinstance(p, dict):
        for k in out:
            if k in p:
                out[k] = p[k]
    o = out
    o["persons"] = max(1, min(12, int(o.get("persons") or 1)))
    o["meals"] = o["meals"] if o["meals"] in MEAL_SLOTS else "abend"
    o["days"] = sorted({int(d) for d in o["days"] if 0 <= int(d) <= 6})
    o["budget"] = max(10, min(1000, int(o.get("budget") or 40)))
    o["kcal"] = max(0, min(5000, int(o.get("kcal") or 0)))
    o["horizon"] = max(1, min(MAX_WEEKS, int(o.get("horizon") or 4)))
    for k in ("appliances", "extras", "allergies", "proteins", "styles", "pantry", "blocked", "stores",
              "favorites", "hidden"):
        o[k] = [str(x) for x in (o.get(k) or []) if isinstance(x, (str, int))]
    o["pantry"] = [x for x in o["pantry"] if x in INGS]
    o["blocked"] = [x for x in o["blocked"] if x in INGS]
    o["stores"] = [x for x in o["stores"] if x in STORE_MULT] or ["hofer"]
    if o["store"] not in o["stores"]:
        o["store"] = None
    o["favorites"] = [x for x in o["favorites"] if x in RBY]
    o["hidden"] = [x for x in o["hidden"] if x in RBY]
    o["fridge"] = {k: float(v) for k, v in (o.get("fridge") or {}).items() if k in INGS and float(v) > 1e-6}
    o["cooklog"] = {k: v for k, v in (o.get("cooklog") or {}).items() if k in RBY and isinstance(v, dict)}
    n = o.get("notify") or {}
    base = copy.deepcopy(DEFAULT_PROFILE["notify"])
    for kind in base:
        src = n.get(kind) or {}
        b = base[kind]
        b["enabled"] = bool(src.get("enabled", b["enabled"]))
        b["channels"] = [c for c in (src.get("channels") or []) if c in ("email", "whatsapp")]
        t = str(src.get("time", b["time"]))
        if len(t) == 5 and t[2] == ":" and t[:2].isdigit() and t[3:].isdigit() and int(t[:2]) < 24 and int(t[3:]) < 60:
            b["time"] = t
        if "weekday" in b:
            try:
                b["weekday"] = max(0, min(6, int(src.get("weekday", b["weekday"]))))
            except (TypeError, ValueError):
                pass
    o["notify"] = base
    o["onboarded"] = bool(o.get("onboarded"))
    prepare(o)
    return o


def prepare(S):
    """Abgeleitete Werte (nicht gespeichert, beginnen mit _)."""
    S["_ex"] = ex_tags(S)
    S["_subst"] = subst_map(S, S["_ex"])
    return S


def storable(S):
    return {k: v for k, v in S.items() if not k.startswith("_")}


# ---------- Eignung & Kennzahlen ----------
# Ersatz, wenn eine Zutat wegen Ernährungsform/Unverträglichkeit ausgeschlossen ist: (Ersatz, Mengenfaktor)
SUBSTITUTES = {"honig": ("zucker", 1), "butter": ("oel", 0.1), "milch": ("hafermilch", 1), "obers": ("kokos", 1),
               "nudeln": ("nudeln_gf", 1), "mehl": ("mehl_gf", 1), "broesel": ("broesel_gf", 1),
               "hafer": ("hafer_gf", 1), "soja": ("tamari", 1), "brot": ("brot_gf", 1), "toast": ("brot_gf", 1)}


def excluded(iid, ex):
    return any(t in ex for t in INGS[iid]["tags"])


def subst_map(S, ex=None):
    ex = ex_tags(S) if ex is None else ex
    return {a: [b, f] for a, (b, f) in SUBSTITUTES.items() if excluded(a, ex) and not excluded(b, ex)}


def ex_tags(S):
    t = set()
    D = {"vegetarisch": ["fleisch", "fisch", "schalentier"], "pescetarisch": ["fleisch"],
         "vegan": ["fleisch", "fisch", "schalentier", "milch", "ei", "honig"]}
    t.update(D.get(S["diet"], []))
    if "glutenfrei" in S["extras"]:
        t.add("gluten")
    if "laktosefrei" in S["extras"]:
        t.add("laktose")
    t.update(S["allergies"])
    for k, *_ in PROTEINS:
        if k not in S["proteins"]:
            t.update(["fisch", "schalentier"] if k == "fisch" else [k])
    return t


def can_cook(r, S):
    return all(any(APPL_CODE[c] in S["appliances"] for c in g) for g in r["need"].split())


def eligible(r, S, ex=None):
    ex = ex_tags(S) if ex is None else ex
    sub = S.get("_subst") if ex is S.get("_ex") else subst_map(S, ex)
    if r["id"] in S["hidden"] or not can_cook(r, S):
        return False
    for iid in r["i"]:
        if iid in sub:
            iid = sub[iid][0]
        g = INGS[iid]
        if excluded(iid, ex):
            return False
        if iid in S["blocked"] and not g["minor"]:
            return False
    return True


def eff_ings(r, S):
    """Zutaten so, wie diese Person das Rezept kocht: Ersatzzutaten eingesetzt, Abneigungen weggelassen."""
    sub = S.get("_subst")
    if sub is None:
        sub = subst_map(S)
    out = []
    for iid, q in r["i"].items():
        if iid in sub:
            iid, f = sub[iid]
            q = q * f
        if iid not in S["blocked"]:
            out.append((iid, q))
    return out


def kcal_of(r, S):
    return round(sum(q * INGS[iid]["kcal"] for iid, q in eff_ings(r, S)) / 10) * 10


def current_store(S):
    if S.get("store") in S["stores"]:
        return S["store"]
    return sorted(S["stores"], key=lambda s: STORE_MULT[s])[0] if S["stores"] else "hofer"


def serving_cost(r, S, mult):
    return sum(q * INGS[iid]["price"] / INGS[iid]["pack"] * mult
               for iid, q in eff_ings(r, S) if iid not in S["pantry"])


def in_season(r, month):
    return r["months"] is None or month in r["months"]


def style_match(r, S, mult):
    m = 0
    for s in S["styles"]:
        if s in ("mealprep", "saison"):
            continue
        if s == "schnell":
            m += r["t"] <= 25
        elif s == "guenstig":
            m += serving_cost(r, S, mult) <= 1.6 or "guenstig" in r["s"]
        elif s in r["s"]:
            m += 1
    return m


def kcal_fit(r, S, slot):
    if not S["kcal"]:
        return 1
    tg = S["kcal"] * KCAL_SHARE[S["meals"]].get(slot, .35)
    d = (kcal_of(r, S) - tg) / (0.3 * tg)
    return 0.12 + math.exp(-d * d)


def main_cuisine(r):
    for c in r["s"]:
        if c in CUISINES:
            return c
    return None


# ---------- Hilfen für Datumsrechnung ----------
def d2s(d):
    return d.isoformat()


def s2d(s):
    return date.fromisoformat(s)


def monday(d):
    return d - timedelta(days=d.weekday())


SLOT_ORDER = {"frueh": 0, "mittag": 1, "abend": 2}


def sort_rows(rows):
    return sorted(rows, key=lambda r: (r["date"], SLOT_ORDER[r["slot"]]))


# ---------- Planerstellung ----------
class _Planner:
    def __init__(self, S, history_rows, today, rng):
        self.S, self.today, self.rng = S, today, rng
        prepare(S)
        self.ex = S["_ex"]
        self.mult = STORE_MULT[current_store(S)]
        self.mains = [r for r in RECIPES if r["type"] == "m" and eligible(r, S, self.ex)]
        self.bfs = [r for r in RECIPES if r["type"] == "f" and eligible(r, S, self.ex)]
        self.slots_per_day = len([m for m in MEAL_SLOTS[S["meals"]] if m != "frueh"]) or 1
        n = len(self.mains)
        # Sperrfrist: so lange, wie es die Anzahl passender Rezepte zulässt (4 bis 42 Tage)
        self.cooldown = max(4, min(42, int(n / self.slots_per_day * 0.7)))
        self.bf_cooldown = max(3, min(14, int(len(self.bfs) / 2)))
        self.hist = {}
        for row in history_rows:
            self._remember(row["recipe_id"], s2d(row["date"]).toordinal())
        for rid, lg in S["cooklog"].items():
            if lg.get("last"):
                try:
                    self._remember(rid, s2d(lg["last"]).toordinal())
                except ValueError:
                    pass
        self.uses = {}
        self.main_sets = {r["id"]: frozenset(i for i in r["main"] if i not in S["pantry"]) for r in RECIPES}
        self.cost = {r["id"]: serving_cost(r, S, self.mult) for r in RECIPES}
        # Was für eine Portion gekauft werden müsste: (Zutat, Menge, Packungsgröße, Packungspreis)
        self.buy = {r["id"]: [(iid, q, INGS[iid]["pack"], INGS[iid]["price"] * self.mult)
                              for iid, q in eff_ings(r, S) if iid not in S["pantry"]] for r in RECIPES}
        self.cheap = "guenstig" in S["styles"]
        self._base_cache = {}

    def _remember(self, rid, o):
        self.hist.setdefault(rid, []).append(o)

    def per_serving_target(self, n_main_slots_week, n_bf_week):
        return self.S["budget"] / max(1, n_main_slots_week + 0.45 * n_bf_week) / self.S["persons"]

    def base(self, slot, weekend, month, per):
        key = (slot, weekend, month, round(per, 2))
        if key in self._base_cache:
            return self._base_cache[key]
        S, out = self.S, []
        pool = self.bfs if slot == "frueh" else self.mains
        for r in pool:
            w = 1 + 1.6 * style_match(r, S, self.mult)
            if r["id"] in S["favorites"]:
                w *= 2
            if r["months"] is not None:
                w *= (2.5 if "saison" in S["styles"] else 1.5) if month in r["months"] else 0.08
            if "suess" in r["s"]:
                w *= (1 if "suess" in S["styles"] else 0.15) * (0.5 if slot == "abend" else 1)
            if slot != "frueh":
                if not weekend and r["t"] > 45:
                    w *= 0.35
                if weekend and r["t"] >= 35:
                    w *= 1.3
                if slot == "mittag" and not weekend and r["t"] > 30:
                    w *= 0.6
            w *= kcal_fit(r, S, slot)
            out.append(w)
        self._base_cache[key] = out
        return out

    def marginal(self, rid, need, fridge, servings):
        """Mehrkosten, wenn dieses Gericht dazukommt – angebrochene Packungen werden mitgerechnet."""
        m = 0.0
        for iid, q, pack, price in self.buy[rid]:
            have = need.get(iid, 0) - (fridge.get(iid, 0) if fridge else 0)
            before = math.ceil(have / pack - 1e-9) if have > 0 else 0
            after_q = have + q * servings
            after = math.ceil(after_q / pack - 1e-9) if after_q > 0 else 0
            if after > before:
                m += (after - before) * price
        return m

    def cost_factor(self, rid, need, fridge, servings, per):
        target = per * servings
        m = self.marginal(rid, need, fridge, servings)
        if m <= target:
            return min(1.8, (target / max(m, 0.15 * target)) ** 0.5)  # Restverwertung wird belohnt
        return (target / m) ** (3 if self.cheap else 2)

    def gap_factor(self, rid, o, local, cooldown):
        best = None
        for x in self.hist.get(rid, ()):
            g = abs(o - x)
            best = g if best is None or g < best else best
        for x in local.get(rid, ()):
            g = abs(o - x)
            best = g if best is None or g < best else best
        if best is None or best >= cooldown:
            return 1.0
        # innerhalb der Sperrfrist praktisch ausgeschlossen – außer es gibt nichts anderes,
        # dann gewinnt das Gericht, das am längsten her ist
        return 1e-4 * (0.05 + best / cooldown) ** 2

    def pick(self, pool, weights, rng):
        tot = sum(weights)
        if tot <= 0:
            return pool[rng.randrange(len(pool))]
        x = rng.random() * tot
        for r, w in zip(pool, weights):
            x -= w
            if x <= 0:
                return r
        return pool[-1]

    def plan_week(self, units, bf_slots, week_rows_fixed, first_week, trials):
        """units: Liste von Slot-Listen [(date, slot), ...]; liefert die beste Variante."""
        S, rng = self.S, self.rng
        if not units and not bf_slots:
            return [], []
        n_main = sum(len(u) for u in units)
        per = self.per_serving_target(n_main, len(bf_slots))
        fixed_set, fixed_need = set(), {}
        for row in week_rows_fixed:
            fixed_set |= self.main_sets.get(row["recipe_id"], frozenset())
            if not row.get("cooked") and row["cook_portions"] and row["recipe_id"] in self.buy:
                for iid, q, _p, _c in self.buy[row["recipe_id"]]:
                    fixed_need[iid] = fixed_need.get(iid, 0) + q * row["cook_portions"]
        fridge = S["fridge"] if first_week else {}
        p = S["persons"]
        best, best_score = None, -1e18
        for _ in range(trials):
            local, wset, chosen, need = {}, set(fixed_set), [], dict(fixed_need)
            prev = None
            for u in units:
                d, slot = u[0]
                o = d.toordinal()
                servings = p * len(u)
                base = self.base(slot, d.weekday() >= 5, d.month, per)
                ws = []
                for r, b in zip(self.mains, base):
                    if b <= 0:
                        ws.append(0)
                        continue
                    w = b * self.gap_factor(r["id"], o, local, self.cooldown)
                    w /= 1 + 0.8 * self.uses.get(r["id"], 0)
                    w *= self.cost_factor(r["id"], need, fridge, servings, per)
                    ms = self.main_sets[r["id"]]
                    if wset:
                        w *= 1 + 0.15 * len(ms & wset)
                    if fridge:
                        w *= 1 + 0.6 * sum(1 for i in ms if fridge.get(i, 0) > 0)
                    if prev is not None:
                        if main_cuisine(r) and main_cuisine(r) == main_cuisine(prev):
                            w *= 0.55
                        if r["prot"] != ["veggie"] and set(r["prot"]) & set(prev["prot"]):
                            w *= 0.6
                    ws.append(w)
                r = self.pick(self.mains, ws, rng)
                local.setdefault(r["id"], []).append(o)
                wset |= self.main_sets[r["id"]]
                for iid, q, _p, _c in self.buy[r["id"]]:
                    need[iid] = need.get(iid, 0) + q * servings
                chosen.append((u, r))
                prev = r
            bf_choice = []
            if bf_slots and self.bfs:
                d0 = bf_slots[0][0]
                base = self.base("frueh", False, d0.month, per)
                want = 3 if len(bf_slots) >= 6 else 2
                picks = []
                for _k in range(min(want, len(self.bfs))):
                    ws = []
                    for r, b in zip(self.bfs, base):
                        if r in picks:
                            ws.append(0)
                            continue
                        w = b * self.gap_factor(r["id"], d0.toordinal(), {}, self.bf_cooldown)
                        w *= 1 + 0.3 * len(self.main_sets[r["id"]] & wset)
                        w *= self.cost_factor(r["id"], need, fridge, p * len(bf_slots) / want, per * 0.45)
                        ws.append(w)
                    pk = self.pick(self.bfs, ws, rng)
                    picks.append(pk)
                    wset |= self.main_sets[pk["id"]]
                    for iid, q, _p, _c in self.buy[pk["id"]]:
                        need[iid] = need.get(iid, 0) + q * p * len(bf_slots) / want
                bf_choice = [(sl, picks[i % len(picks)]) for i, sl in enumerate(bf_slots)]
            sc = self.score(chosen, bf_choice, week_rows_fixed, fridge)
            if sc > best_score:
                best_score, best = sc, (chosen, bf_choice)
        return best

    def score(self, chosen, bf_choice, fixed_rows, fridge):
        S, p = self.S, self.S["persons"]
        needs = {}
        for u, r in chosen:
            for iid, q in eff_ings(r, S):
                needs[iid] = needs.get(iid, 0) + q * p * len(u)
        for _sl, r in bf_choice:
            for iid, q in eff_ings(r, S):
                needs[iid] = needs.get(iid, 0) + q * p
        for row in fixed_rows:
            if not row.get("cooked") and row["cook_portions"]:
                for iid, q in eff_ings(RBY[row["recipe_id"]], S):
                    needs[iid] = needs.get(iid, 0) + q * row["cook_portions"]
        total = shopping_items(S, needs, self.mult, fridge)["total"]
        over = max(0, total - S["budget"])
        st = sum(style_match(r, S, self.mult) for _u, r in chosen)
        ids = len({r["id"] for _u, r in chosen})
        cz = len({main_cuisine(r) for _u, r in chosen if main_cuisine(r)})
        kd = 0
        if S["kcal"]:
            for u, r in chosen:
                tg = S["kcal"] * KCAL_SHARE[S["meals"]].get(u[0][1], .35)
                kd += abs(kcal_of(r, S) - tg) / tg * len(u)
        rep = sum(1 for u, r in chosen if self.gap_factor(r["id"], u[0][0].toordinal(), {}, self.cooldown) < 1)
        return st + ids + cz * 0.6 - over * 5 - total * 0.06 - kd * 3 - rep * 3

    def commit(self, chosen, bf_choice):
        for u, r in chosen:
            self._remember(r["id"], u[0][0].toordinal())
            self.uses[r["id"]] = self.uses.get(r["id"], 0) + 1
        for (d, _s), r in bf_choice:
            self._remember(r["id"], d.toordinal())


def plan_slots(S, start, n_days, fixed_keys):
    mains, bfs = [], []
    for i in range(n_days):
        d = start + timedelta(days=i)
        if d.weekday() not in S["days"]:
            continue
        for m in MEAL_SLOTS[S["meals"]]:
            if (d2s(d), m) in fixed_keys:
                continue
            (bfs if m == "frueh" else mains).append((d, m))
    return mains, bfs


def build_units(slots, mealprep):
    if not mealprep:
        return [[s] for s in slots]
    out, i = [], 0
    while i < len(slots):
        a = slots[i]
        b = slots[i + 1] if i + 1 < len(slots) else None
        if b and (b[0] - a[0]).days <= 1:
            out.append([a, b])
            i += 2
        else:
            out.append([a])
            i += 1
    return out


def generate(S, existing_rows, start, weeks, today=None, seed=None, days=None):
    """Plant `weeks` Wochen (oder genau `days` Tage) ab `start` neu. Gekochte Mahlzeiten bleiben erhalten.

    Rückgabe: (neue_zeilen, info). Die Aufrufer ersetzen alle ungekochten Zeilen im Zeitraum durch neue_zeilen.
    """
    today = today or date.today()
    n_days = max(1, min(7 * MAX_WEEKS, int(days))) if days else 7 * max(1, min(MAX_WEEKS, int(weeks)))
    weeks = math.ceil(n_days / 7)
    end = start + timedelta(days=n_days)
    s_start, s_end = d2s(start), d2s(end)
    inside = [r for r in existing_rows if s_start <= r["date"] < s_end]
    fixed = [r for r in inside if r.get("cooked")]
    outside = [r for r in existing_rows if not (s_start <= r["date"] < s_end)]
    rng = random.Random(seed)
    P = _Planner(S, outside + fixed, today, rng)
    info = {"cooldown": P.cooldown, "eligible": len(P.mains), "eligible_breakfast": len(P.bfs), "weeks": weeks}
    if not S["days"]:
        return [], dict(info, error="Bitte wähle mindestens einen Tag, an dem du zuhause isst.")
    if not P.mains:
        return [], dict(info, error="Mit diesen Einstellungen passt leider kein Gericht. Wähle mehr Küchengeräte "
                                    "oder Proteinquellen aus oder entferne ein paar blockierte Zutaten.")
    fixed_keys = {(r["date"], r["slot"]) for r in fixed}
    trials = max(8, min(60, 240 // weeks))
    p = S["persons"]
    rows = []
    mealprep = "mealprep" in S["styles"]
    this_monday = monday(today)
    for w in range(weeks):
        ws = start + timedelta(days=7 * w)
        mains, bfs = plan_slots(S, ws, min(7, n_days - 7 * w), fixed_keys)
        units = build_units(mains, mealprep)
        wk_fixed = [r for r in fixed if d2s(ws) <= r["date"] < d2s(ws + timedelta(days=7))]
        first = monday(ws) <= this_monday < monday(ws) + timedelta(days=7) or (w == 0 and ws >= today)
        chosen, bf_choice = P.plan_week(units, bfs, wk_fixed, first, trials)
        P.commit(chosen, bf_choice)
        for u, r in chosen:
            for k, (d, slot) in enumerate(u):
                rows.append({"date": d2s(d), "slot": slot, "recipe_id": r["id"], "portions": p,
                             "cook_portions": p * len(u) if k == 0 else 0, "leftover": 1 if k else 0, "cooked": 0})
        for (d, slot), r in bf_choice:
            rows.append({"date": d2s(d), "slot": slot, "recipe_id": r["id"], "portions": p, "cook_portions": p,
                         "leftover": 0, "cooked": 0})
    info["few_recipes"] = len(P.mains) < 10
    if P.mains and len(P.mains) < len(MEAL_SLOTS[S["meals"]]) * 7:
        info["few_recipes"] = True
    if "frueh" in MEAL_SLOTS[S["meals"]] and not P.bfs:
        info["no_breakfast"] = True
    return sort_rows(rows), info


def alternatives(S, all_rows, date_s, slot, exclude=None, limit=None, seed=None):
    """Gewichtete Vorschlagsliste für einen einzelnen Platz (für „Anderes Gericht“)."""
    rng = random.Random(seed)
    others = [r for r in all_rows if not (r["date"] == date_s and r["slot"] == slot)]
    P = _Planner(S, others, date.today(), rng)
    pool = P.bfs if slot == "frueh" else P.mains
    if not pool:
        return []
    d = s2d(date_s)
    per = P.per_serving_target(7 * P.slots_per_day, 7 if slot == "frueh" else 0)
    base = P.base(slot, d.weekday() >= 5, d.month, per)
    cd = P.bf_cooldown if slot == "frueh" else P.cooldown
    wk = [r for r in others if monday(s2d(r["date"])) == monday(d)]
    need = {}
    for row in wk:
        if not row.get("cooked") and row["cook_portions"] and row["recipe_id"] in P.buy:
            for iid, q, _p, _c in P.buy[row["recipe_id"]]:
                need[iid] = need.get(iid, 0) + q * row["cook_portions"]
    fridge = S["fridge"] if monday(d) == monday(date.today()) else {}
    if slot == "frueh":
        per *= 0.45
    scored = []
    for r, b in zip(pool, base):
        if exclude and r["id"] in exclude:
            continue
        w = b * P.gap_factor(r["id"], d.toordinal(), {}, cd) * P.cost_factor(r["id"], need, fridge, S["persons"], per)
        scored.append((w, r))
    return scored if limit is None else sorted(scored, key=lambda x: -x[0])[:limit]


def pick_swap(S, all_rows, date_s, slot, current, seed=None):
    sc = alternatives(S, all_rows, date_s, slot, exclude={current}, seed=seed)
    if not sc:
        return None
    rng = random.Random(seed)
    tot = sum(w for w, _ in sc)
    x = rng.random() * tot
    for w, r in sc:
        x -= w
        if x <= 0:
            return r["id"]
    return sc[-1][1]["id"]


# ---------- Einkauf ----------
def needs_for(S, rows, from_date=None):
    needs = {}
    for row in rows:
        if row.get("cooked") or not row["cook_portions"]:
            continue
        if from_date and row["date"] < from_date:
            continue
        r = RBY.get(row["recipe_id"])
        if not r:
            continue
        for iid, q in eff_ings(r, S):
            needs[iid] = needs.get(iid, 0) + q * row["cook_portions"]
    return needs


def shopping_items(S, needs, mult, fridge):
    items, have, from_fridge, total = [], [], [], 0.0
    for iid, q in needs.items():
        g = INGS[iid]
        if iid in S["pantry"]:
            have.append(iid)
            continue
        rem = q - (fridge.get(iid, 0) if fridge else 0)
        if rem <= 1e-6:
            from_fridge.append(iid)
            continue
        packs = max(1, math.ceil(rem / g["pack"] - 1e-6))
        price = packs * g["price"] * mult
        total += price
        items.append({"id": iid, "need": rem, "packs": packs, "price": round(price, 2), "rest": packs * g["pack"] - rem})
    return {"items": items, "have": have, "fromFridge": from_fridge, "total": round(total, 2)}


def week_rows(rows, week_monday):
    a, b = d2s(week_monday), d2s(week_monday + timedelta(days=7))
    return [r for r in rows if a <= r["date"] < b]


def shopping_for_week(S, rows, week_monday, today=None, store=None):
    """Einkaufsliste einer Woche. Der Vorrat wird chronologisch ab heute verteilt:
    zuerst auf die laufende Woche, dann auf die folgenden – so wird nichts doppelt gezählt."""
    today = today or date.today()
    store = store or current_store(S)
    mult = STORE_MULT[store]
    this_monday = monday(today)
    t = d2s(today)
    if week_monday < this_monday:
        needs = needs_for(S, week_rows(rows, week_monday))
        res = shopping_items(S, needs, mult, {})
        res["mode"] = "past"
    else:
        fridge = dict(S["fridge"])
        w = this_monday
        while w < week_monday:
            for iid, q in needs_for(S, week_rows(rows, w), t).items():
                if iid in fridge:
                    fridge[iid] = max(0, fridge[iid] - q)
            w += timedelta(days=7)
        needs = needs_for(S, week_rows(rows, week_monday), t)
        res = shopping_items(S, needs, mult, fridge)
        res["mode"] = "current" if week_monday == this_monday else "future"
    res["needs"] = needs
    res["store"] = store
    res["compare"] = sorted(([s, shopping_items(S, needs, STORE_MULT[s], {} if res["mode"] == "past" else fridge_for_compare(S, rows, week_monday, today))["total"]]
                             for s in S["stores"]), key=lambda x: x[1])
    return res


def fridge_for_compare(S, rows, week_monday, today):
    fridge = dict(S["fridge"])
    w, t = monday(today), d2s(today)
    while w < week_monday:
        for iid, q in needs_for(S, week_rows(rows, w), t).items():
            if iid in fridge:
                fridge[iid] = max(0, fridge[iid] - q)
        w += timedelta(days=7)
    return fridge


def grouped_items(items):
    groups = []
    for cat in CATEGORY_ORDER:
        lst = sorted((it for it in items if INGS[it["id"]]["cat"] == cat), key=lambda it: INGS[it["id"]]["name"])
        if lst:
            groups.append((cat, lst))
    return groups


# ---------- Kochen & Vorrat ----------
def apply_cook(S, row, undo=False):
    """Zieht beim Kochen die Zutaten aus dem Vorrat ab (bzw. legt sie beim Rückgängig-Machen zurück)."""
    r = RBY.get(row["recipe_id"])
    if not r or not row["cook_portions"]:
        return  # Reste vom Vortag: nichts abzubuchen, nichts zu zählen
    for iid, q in eff_ings(r, S):
        if iid in S["pantry"]:
            continue
        cur = S["fridge"].get(iid, 0)
        nv = cur + q * row["cook_portions"] if undo else max(0, cur - q * row["cook_portions"])
        if nv <= 1e-6:
            S["fridge"].pop(iid, None)
        else:
            S["fridge"][iid] = round(nv, 3)
    lg = S["cooklog"].get(r["id"], {"n": 0, "last": None})
    if undo:
        lg["n"] = max(0, lg["n"] - 1)
        if lg["n"]:
            S["cooklog"][r["id"]] = lg
        else:
            S["cooklog"].pop(r["id"], None)
    else:
        lg["n"] += 1
        lg["last"] = row["date"]
        S["cooklog"][r["id"]] = lg


def fridge_step(g):
    return (50 if g["pack"] >= 500 else 25) if g["unit"] in ("g", "ml") else 1


# ---------- Formatierung für Nachrichten ----------
def fmt_qty(q, u):
    if u in ("g", "ml"):
        if q >= 1000:
            return f"{round(q / 100) / 10:g}".replace(".", ",") + (" kg" if u == "g" else " l")
        v = round(q) if q < 20 else round(q / 5) * 5
        return f"{v} {u}"
    r = round(q * 4) / 4 or 0.25
    w, f = int(r), r - int(r)
    fs = {0: "", 0.25: "¼", 0.5: "½", 0.75: "¾"}[f]
    lab = {"Zehe": "Zehen" if q > 1 else "Zehe"}.get(u, u)
    return f"{w if w else ''}{fs or ('' if w else '0')} {lab}"


def eur(n):
    return f"{n:.2f}".replace(".", ",") + " €"


def store_name(s):
    return STORE_NAME.get(s, s)
