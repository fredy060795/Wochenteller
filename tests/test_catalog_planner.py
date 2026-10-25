import unittest
from collections import Counter
from datetime import date, timedelta

from wochenteller import catalog, planner
from wochenteller.catalog import INGS, RBY, RECIPES

ALL = ["Herd", "Backrohr", "Airfryer", "Mikrowelle", "Wasserkocher", "Mixer", "Reiskocher", "Slow Cooker", "Toaster"]
MONDAY = date(2026, 10, 26)
TODAY = date(2026, 10, 24)


def profile(**kw):
    return planner.normalize_profile(dict(kw, appliances=kw.get("appliances", ["Herd", "Backrohr", "Airfryer", "Mixer", "Wasserkocher"])))


def gaps(rows):
    last, out = {}, []
    for r in rows:
        if r["slot"] == "frueh" or r["leftover"]:
            continue
        o = date.fromisoformat(r["date"]).toordinal()
        if r["recipe_id"] in last:
            out.append(o - last[r["recipe_id"]])
        last[r["recipe_id"]] = o
    return out


class CatalogTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(catalog.validate(), [])

    def test_size(self):
        mains = [r for r in RECIPES if r["type"] == "m"]
        self.assertGreaterEqual(len(mains), 200)
        self.assertGreaterEqual(len([r for r in RECIPES if r["type"] == "f"]), 30)

    def test_steps_are_detailed(self):
        for r in RECIPES:
            if r["type"] == "m":
                self.assertGreaterEqual(len(r["st"]), 4, r["id"])
                self.assertTrue(any(catalog.TOKEN_RE.search(s) for s in r["st"]), r["id"] + " ohne Mengenangaben")

    def test_timer_detection(self):
        self.assertEqual(catalog.step_timer("ca. 20 Minuten kochen"), 1200)
        self.assertEqual(catalog.step_timer("8–10 Minuten garen"), 480)
        self.assertEqual(catalog.step_timer("6–7 Stunden"), 6 * 3600)
        self.assertIsNone(catalog.step_timer("bei 200 °C backen"))


class PlannerTest(unittest.TestCase):
    def test_no_repeat_within_cooldown_six_months(self):
        for kw in [dict(meals="abend"), dict(meals="mittag_abend"), dict(meals="alle", diet="vegetarisch"),
                   dict(meals="mittag_abend", diet="vegan"), dict(meals="abend", styles=["mealprep"])]:
            S = profile(**kw)
            rows, info = planner.generate(S, [], MONDAY, 26, today=TODAY, seed=7)
            g = gaps(rows)
            self.assertTrue(g, kw)
            self.assertGreaterEqual(min(g), info["cooldown"], kw)
            self.assertGreaterEqual(info["cooldown"], 14 if kw.get("diet") == "vegan" else 30, kw)

    def test_history_is_respected_when_extending(self):
        S = profile(meals="abend")
        first, info = planner.generate(S, [], MONDAY, 4, today=TODAY, seed=1)
        second, _ = planner.generate(S, first, MONDAY + timedelta(days=28), 4, today=TODAY, seed=2)
        self.assertGreaterEqual(min(gaps(first + second)), info["cooldown"])

    def test_diets_and_allergies(self):
        S = profile(meals="alle", diet="vegan", allergies=["nuss"])
        rows, _ = planner.generate(S, [], MONDAY, 8, today=TODAY, seed=3)
        bad = {"fleisch", "fisch", "schalentier", "milch", "ei", "honig", "nuss"}
        for row in rows:
            for iid, _q in planner.eff_ings(RBY[row["recipe_id"]], S):
                self.assertFalse(set(INGS[iid]["tags"]) & bad, (row["recipe_id"], iid))

    def test_glutenfree_substitutes(self):
        S = profile(extras=["glutenfrei"])
        r = RBY["spaghetti-bolognese"]
        self.assertTrue(planner.eligible(r, S))
        ids = [i for i, _ in planner.eff_ings(r, S)]
        self.assertIn("nudeln_gf", ids)
        self.assertNotIn("nudeln", ids)

    def test_appliances(self):
        S = profile(appliances=["Herd"])
        rows, _ = planner.generate(S, [], MONDAY, 4, today=TODAY, seed=4)
        for row in rows:
            self.assertTrue(planner.can_cook(RBY[row["recipe_id"]], S), row["recipe_id"])

    def test_days_at_home(self):
        S = profile(days=[0, 2, 4])
        rows, _ = planner.generate(S, [], MONDAY, 2, today=TODAY, seed=5)
        self.assertTrue(rows)
        for row in rows:
            self.assertIn(date.fromisoformat(row["date"]).weekday(), [0, 2, 4])

    def test_partial_week(self):
        S = profile()
        rows, _ = planner.generate(S, [], MONDAY + timedelta(days=3), 1, today=TODAY, seed=5, days=4)
        self.assertEqual(sorted({r["date"] for r in rows}), [(MONDAY + timedelta(days=d)).isoformat() for d in range(3, 7)])

    def test_mealprep_pairs(self):
        S = profile(styles=["mealprep"], persons=2)
        rows, _ = planner.generate(S, [], MONDAY, 1, today=TODAY, seed=6)
        cooks = [r for r in rows if r["cook_portions"] == 4]
        lefts = [r for r in rows if r["leftover"]]
        self.assertTrue(cooks and lefts)
        for l in lefts:
            self.assertEqual(l["cook_portions"], 0)

    def test_cooked_rows_are_kept(self):
        S = profile()
        rows, _ = planner.generate(S, [], MONDAY, 1, today=TODAY, seed=8)
        rows[0]["cooked"] = 1
        new, _ = planner.generate(S, rows, MONDAY, 1, today=TODAY, seed=9)
        self.assertNotIn((rows[0]["date"], rows[0]["slot"]), {(r["date"], r["slot"]) for r in new})

    def test_budget_is_considered(self):
        cheap = profile(budget=25, persons=1)
        rich = profile(budget=150, persons=1)
        c1 = c2 = 0
        for seed in range(3):
            r1, _ = planner.generate(cheap, [], MONDAY, 1, today=TODAY, seed=seed)
            r2, _ = planner.generate(rich, [], MONDAY, 1, today=TODAY, seed=seed)
            c1 += planner.shopping_for_week(cheap, r1, MONDAY, today=TODAY)["total"]
            c2 += planner.shopping_for_week(rich, r2, MONDAY, today=TODAY)["total"]
        self.assertLess(c1, c2)
        self.assertLess(c1 / 3, 32)

    def test_shopping_fridge_not_counted_twice(self):
        S = profile()
        S["fridge"] = {"nudeln": 500}
        rows = [{"date": (MONDAY - timedelta(days=1)).isoformat(), "slot": "abend", "recipe_id": "aglio-olio", "portions": 4, "cook_portions": 4, "leftover": 0, "cooked": 0},
                {"date": MONDAY.isoformat(), "slot": "abend", "recipe_id": "aglio-olio", "portions": 4, "cook_portions": 4, "leftover": 0, "cooked": 0}]
        this_week = planner.shopping_for_week(S, rows, MONDAY - timedelta(days=7), today=TODAY)
        self.assertIn("nudeln", this_week["fromFridge"])
        next_week = planner.shopping_for_week(S, rows, MONDAY, today=TODAY)
        self.assertIn("nudeln", [i["id"] for i in next_week["items"]])

    def test_cook_and_undo(self):
        S = profile(persons=2)
        S["fridge"] = {"nudeln": 500, "speck": 125}
        row = {"date": MONDAY.isoformat(), "slot": "abend", "recipe_id": "carbonara", "portions": 2, "cook_portions": 2, "leftover": 0, "cooked": 0}
        planner.apply_cook(S, row)
        self.assertAlmostEqual(S["fridge"]["nudeln"], 260)
        self.assertAlmostEqual(S["fridge"]["speck"], 25)
        self.assertEqual(S["cooklog"]["carbonara"]["n"], 1)
        planner.apply_cook(S, row, undo=True)
        self.assertAlmostEqual(S["fridge"]["nudeln"], 500)
        self.assertNotIn("carbonara", S["cooklog"])

    def test_leftover_cook_does_not_touch_log(self):
        S = profile()
        S["cooklog"] = {"carbonara": {"n": 1, "last": "2026-10-20"}}
        planner.apply_cook(S, {"date": "2026-10-21", "slot": "mittag", "recipe_id": "carbonara", "portions": 1, "cook_portions": 0, "leftover": 1, "cooked": 0}, undo=True)
        self.assertEqual(S["cooklog"]["carbonara"]["n"], 1)

    def test_normalize_rejects_garbage(self):
        S = planner.normalize_profile({"persons": 99, "meals": "x", "days": [9, 1], "budget": -5, "stores": ["nope"],
                                       "notify": {"daily": {"time": "25:99", "channels": ["sms", "email"]}}})
        self.assertEqual(S["persons"], 12)
        self.assertEqual(S["meals"], "abend")
        self.assertEqual(S["days"], [1])
        self.assertEqual(S["budget"], 10)
        self.assertEqual(S["stores"], ["hofer"])
        self.assertEqual(S["notify"]["daily"]["time"], "16:00")
        self.assertEqual(S["notify"]["daily"]["channels"], ["email"])


if __name__ == "__main__":
    unittest.main()
