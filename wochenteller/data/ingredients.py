"""Zutatenkatalog.

Jede Zutat: Name (Einkaufsliste), Kategorie, Packungsgröße, Einheit, Preis pro Packung (Hofer-Niveau),
Tags (für Ernährung/Allergien), Kleinigkeit (wird bei Abneigung einfach weggelassen),
Packungstext, kcal pro Einheit, Einzahl-Name (für Kochschritte, optional).
"""

INGREDIENTS = {}


def I(id, name, cat, pack, unit, price, tags, minor, label, kcal, one=None):
    INGREDIENTS[id] = {
        "id": id, "name": name, "cat": cat, "pack": pack, "unit": unit, "price": price,
        "tags": tags.split() if tags else [], "minor": bool(minor), "packLabel": label,
        "kcal": kcal, "one": one or name,
    }


FL, KR, TK, KO, TR, BR, OG, GW = (
    "Fleisch & Fisch", "Kühlregal", "Tiefkühl", "Konserven", "Trockenware",
    "Brot & Gebäck", "Obst & Gemüse", "Gewürze & Öle",
)

# ---------- Fleisch & Fisch ----------
I("huhn", "Hühnerbrust", FL, 500, "g", 6.49, "huhn fleisch", 0, "500 g", 1.1)
I("huhnkeule", "Hühnerkeulen", FL, 1000, "g", 3.99, "huhn fleisch", 0, "1 kg", 1.6)
I("putenbrust", "Putenbrust", FL, 500, "g", 6.99, "huhn fleisch", 0, "500 g", 1.05)
I("faschiert", "Faschiertes gemischt", FL, 500, "g", 4.99, "rind schwein fleisch", 0, "500 g", 2.5)
I("rindfasch", "Rindfaschiertes", FL, 400, "g", 4.99, "rind fleisch", 0, "400 g", 2.2)
I("gulasch", "Rindsgulasch-Fleisch", FL, 500, "g", 8.49, "rind fleisch", 0, "500 g", 1.6)
I("schnitzel", "Schweinsschnitzel", FL, 500, "g", 5.49, "schwein fleisch", 0, "500 g", 1.2)
I("schweinsbraten", "Schweinsschulter", FL, 1000, "g", 7.49, "schwein fleisch", 0, "1 kg", 2.3)
I("bratwurst", "Bratwürstel", FL, 4, "Stk", 3.49, "schwein fleisch", 0, "4 Stk", 260, "Bratwürstel")
I("speck", "Speckwürfel", FL, 125, "g", 1.79, "schwein fleisch", 0, "125 g", 3.0)
I("lachs", "Lachsfilet (TK)", TK, 250, "g", 4.99, "fisch", 0, "250 g", 2.0)
I("weissfisch", "Seelachsfilet (TK)", TK, 400, "g", 3.99, "fisch", 0, "400 g", 0.8)
I("raeucherlachs", "Räucherlachs", KR, 100, "g", 2.99, "fisch", 0, "100 g", 1.8)
I("fischst", "Fischstäbchen (TK)", TK, 15, "Stk", 2.99, "fisch gluten", 0, "15 Stk", 50, "Fischstäbchen")
I("thunfisch", "Thunfisch in Wasser", KO, 150, "g", 1.49, "fisch", 0, "Dose", 1.1)
I("garnelen", "Garnelen (TK)", TK, 200, "g", 4.49, "schalentier", 0, "200 g", 0.8)

# ---------- Kühlregal ----------
I("schinken", "Kochschinken", KR, 150, "g", 1.59, "schwein fleisch", 0, "150 g", 1.1)
I("wuerstel", "Frankfurter Würstel", KR, 6, "Stk", 2.29, "schwein fleisch", 0, "6 Stk", 150, "Frankfurter")
I("kaesekrainer", "Käsekrainer", KR, 4, "Stk", 3.49, "schwein fleisch milch laktose", 0, "4 Stk", 270, "Käsekrainer")
I("leberkaese", "Leberkäse", KR, 400, "g", 2.99, "schwein fleisch", 0, "400 g", 2.9)
I("tofu", "Tofu natur", KR, 400, "g", 1.99, "soja tofu", 0, "400 g", 1.25)
I("raeuchertofu", "Räuchertofu", KR, 200, "g", 2.29, "soja tofu", 0, "200 g", 1.7)
I("eier", "Eier", KR, 10, "Stk", 2.99, "ei", 0, "10 Stk", 75, "Ei")
I("milch", "Milch", KR, 1000, "ml", 1.19, "milch laktose", 0, "1 l", 0.64)
I("butter", "Butter", KR, 250, "g", 2.79, "milch laktose", 0, "250 g", 7.4)
I("obers", "Schlagobers", KR, 250, "ml", 1.39, "milch laktose", 0, "250 ml", 3.4)
I("sauerrahm", "Sauerrahm", KR, 250, "g", 0.99, "milch laktose", 0, "250 g", 1.6)
I("cremefraiche", "Crème fraîche", KR, 200, "g", 1.49, "milch laktose", 0, "200 g", 2.9)
I("frischkaese", "Frischkäse natur", KR, 200, "g", 1.29, "milch laktose", 0, "200 g", 2.4)
I("joghurt", "Naturjoghurt", KR, 500, "g", 1.19, "milch laktose", 0, "500 g", 0.65)
I("skyr", "Skyr natur", KR, 450, "g", 1.49, "milch laktose", 0, "450 g", 0.63)
I("topfen", "Magertopfen", KR, 250, "g", 0.89, "milch laktose", 0, "250 g", 0.7)
I("ricotta", "Ricotta", KR, 250, "g", 1.49, "milch laktose", 0, "250 g", 1.4)
I("feta", "Feta", KR, 200, "g", 1.79, "milch laktose", 0, "200 g", 2.6)
I("halloumi", "Halloumi", KR, 225, "g", 2.99, "milch laktose", 0, "225 g", 3.2)
I("mozzarella", "Mozzarella", KR, 125, "g", 0.89, "milch laktose", 0, "125 g", 2.5)
I("reibkaese", "Reibkäse", KR, 200, "g", 1.99, "milch laktose", 0, "200 g", 3.6)
I("bergkaese", "Bergkäse", KR, 200, "g", 3.29, "milch laktose", 0, "200 g", 4.0)
I("kaesesch", "Käse in Scheiben", KR, 150, "g", 1.49, "milch laktose", 0, "150 g", 3.5)
I("parmesan", "Parmesan", KR, 100, "g", 2.29, "milch laktose", 0, "100 g", 4.0)
I("pizzateig", "Pizzateig (Kühlregal)", KR, 1, "Stk", 1.49, "gluten", 0, "400 g", 1040, "Pizzateig")
I("blaetterteig", "Blätterteig (Kühlregal)", KR, 1, "Stk", 1.49, "gluten milch laktose", 0, "275 g", 1100, "Blätterteig")
I("gnocchi", "Gnocchi", KR, 500, "g", 1.49, "gluten", 0, "500 g", 1.6)
I("spaetzle", "Spätzle (Kühlregal)", KR, 500, "g", 1.79, "gluten ei", 0, "500 g", 1.9)
I("schupfnudeln", "Schupfnudeln (Kühlregal)", KR, 500, "g", 1.79, "gluten", 0, "500 g", 1.6)
I("tortellini", "Käsetortellini (Kühlregal)", KR, 250, "g", 1.99, "gluten milch laktose ei", 0, "250 g", 2.8)
I("hafermilch", "Haferdrink", TR, 1000, "ml", 1.29, "gluten", 0, "1 l", 0.45)

# ---------- Trockenware ----------
I("nudeln", "Nudeln", TR, 500, "g", 0.99, "gluten", 0, "500 g", 3.55)
I("lasagne", "Lasagneblätter", TR, 500, "g", 1.49, "gluten", 0, "500 g", 3.6)
I("reis", "Reis", TR, 1000, "g", 1.79, "", 0, "1 kg", 3.5)
I("milchreis", "Milchreis (Rundkorn)", TR, 500, "g", 1.29, "", 0, "500 g", 3.5)
I("couscous", "Couscous", TR, 500, "g", 1.49, "gluten", 0, "500 g", 3.6)
I("bulgur", "Bulgur", TR, 500, "g", 1.49, "gluten", 0, "500 g", 3.5)
I("quinoa", "Quinoa", TR, 500, "g", 3.49, "", 0, "500 g", 3.7)
I("polenta", "Polenta", TR, 500, "g", 1.29, "", 0, "500 g", 3.6)
I("gries", "Weizengrieß", TR, 500, "g", 0.99, "gluten", 0, "500 g", 3.4)
I("reisnudeln", "Reisnudeln", TR, 250, "g", 1.99, "", 0, "250 g", 3.6)
I("mehl", "Mehl", TR, 1000, "g", 0.79, "gluten", 0, "1 kg", 3.5)
I("broesel", "Semmelbrösel", TR, 400, "g", 0.99, "gluten", 0, "400 g", 3.6)
I("hafer", "Haferflocken", TR, 500, "g", 0.89, "gluten", 0, "500 g", 3.7)
I("linsen", "Rote Linsen", TR, 500, "g", 1.79, "huelse", 0, "500 g", 3.4)
I("linsenbraun", "Berglinsen", TR, 500, "g", 1.99, "huelse", 0, "500 g", 3.3)
I("erdnussb", "Erdnussbutter", TR, 350, "g", 1.99, "erdnuss", 0, "Glas", 6.0)
I("erdnuesse", "Erdnüsse geröstet", TR, 200, "g", 1.49, "erdnuss", 0, "200 g", 6.0)
I("nuesse", "Walnüsse", TR, 200, "g", 2.99, "nuss", 0, "200 g", 6.5)
I("cashew", "Cashewkerne", TR, 200, "g", 2.99, "nuss", 0, "200 g", 5.8)
I("sesam", "Sesam", TR, 200, "g", 1.79, "", 1, "200 g", 5.7)
I("zucker", "Zucker", TR, 1000, "g", 1.19, "", 1, "1 kg", 4.0)
I("honig", "Honig", TR, 500, "g", 4.49, "honig", 0, "500 g", 3.0)
I("marmelade", "Marillenmarmelade", TR, 450, "g", 1.99, "", 0, "Glas", 2.5)

# glutenfreie Ersatzprodukte (werden bei „Glutenfrei“ automatisch eingesetzt)
I("nudeln_gf", "Glutenfreie Nudeln", TR, 500, "g", 2.49, "", 0, "500 g", 3.55)
I("mehl_gf", "Glutenfreies Mehl", TR, 1000, "g", 2.99, "", 0, "1 kg", 3.5)
I("broesel_gf", "Glutenfreie Brösel", TR, 200, "g", 2.49, "", 0, "200 g", 3.7)
I("hafer_gf", "Glutenfreie Haferflocken", TR, 500, "g", 2.99, "", 0, "500 g", 3.7)
I("tamari", "Tamari (glutenfreie Sojasauce)", GW, 16, "EL", 2.99, "soja", 0, "250 ml", 10)

# ---------- Brot & Gebäck ----------
I("knoedelbrot", "Knödelbrot", BR, 250, "g", 1.29, "gluten", 0, "250 g", 2.6)
I("tortilla", "Tortilla-Wraps", BR, 6, "Stk", 1.69, "gluten", 0, "6 Stk", 180, "Wrap")
I("brot", "Vollkornbrot", BR, 500, "g", 1.99, "gluten", 0, "500 g", 2.2)
I("toast", "Toastbrot", BR, 500, "g", 1.29, "gluten", 0, "500 g", 2.6)
I("brot_gf", "Glutenfreies Brot", BR, 400, "g", 3.49, "", 0, "400 g", 2.4)
I("semmeln", "Semmeln", BR, 6, "Stk", 1.49, "gluten", 0, "6 Stk", 150, "Semmel")
I("baguette", "Baguette", BR, 250, "g", 0.99, "gluten", 0, "250 g", 2.6)
I("burgerbun", "Burgerbrötchen", BR, 4, "Stk", 1.79, "gluten", 0, "4 Stk", 210, "Burgerbrötchen")
I("fladenbrot", "Fladenbrot", BR, 1, "Stk", 1.49, "gluten", 0, "400 g", 1000, "Fladenbrot")

# ---------- Obst & Gemüse ----------
I("kartoffeln", "Erdäpfel", OG, 2000, "g", 2.49, "", 0, "2 kg", 0.77)
I("suesskart", "Süßkartoffeln", OG, 1000, "g", 2.49, "", 0, "1 kg", 0.86)
I("zwiebel", "Zwiebeln", OG, 10, "Stk", 1.29, "", 1, "1 kg", 40, "Zwiebel")
I("rotezwiebel", "Rote Zwiebeln", OG, 5, "Stk", 1.29, "", 1, "500 g", 40, "rote Zwiebel")
I("knoblauch", "Knoblauch", OG, 30, "Zehe", 1.29, "", 1, "3 Knollen", 4)
I("karotten", "Karotten", OG, 1000, "g", 1.19, "", 0, "1 kg", 0.36)
I("paprika", "Paprika", OG, 3, "Stk", 1.99, "", 0, "3 Stk", 40, "Paprika")
I("zucchini", "Zucchini", OG, 2, "Stk", 1.49, "", 0, "2 Stk", 50, "Zucchini")
I("melanzani", "Melanzani", OG, 1, "Stk", 0.99, "", 0, "1 Stk", 70, "Melanzani")
I("brokkoli", "Brokkoli", OG, 1, "Stk", 1.49, "", 0, "1 Stk", 170, "Brokkoli")
I("karfiol", "Karfiol", OG, 1, "Stk", 1.99, "", 0, "1 Stk", 250, "Karfiol")
I("weisskraut", "Weißkraut", OG, 1000, "g", 0.99, "", 0, "1 Stk", 0.25)
I("rotkraut", "Rotkraut", OG, 1000, "g", 1.19, "", 0, "1 Stk", 0.3)
I("chinakohl", "Chinakohl", OG, 1, "Stk", 1.49, "", 0, "1 Stk", 120, "Chinakohl")
I("rosenkohl", "Kohlsprossen", OG, 500, "g", 1.99, "", 0, "500 g", 0.43)
I("kohlrabi", "Kohlrabi", OG, 1, "Stk", 0.89, "", 0, "1 Stk", 80, "Kohlrabi")
I("fenchel", "Fenchel", OG, 1, "Stk", 1.29, "", 0, "1 Stk", 75, "Fenchel")
I("sellerie", "Knollensellerie", OG, 1, "Stk", 1.29, "", 0, "1 Stk", 110, "Knollensellerie")
I("spargel", "Spargel", OG, 500, "g", 4.99, "", 0, "500 g", 0.2)
I("rotebete", "Rote Rüben (gekocht)", OG, 500, "g", 1.29, "", 0, "500 g", 0.4)
I("tomaten", "Tomaten", OG, 500, "g", 1.99, "", 0, "500 g", 0.18)
I("cherry", "Cherrytomaten", OG, 250, "g", 1.49, "", 0, "250 g", 0.2)
I("gurke", "Gurke", OG, 1, "Stk", 0.79, "", 0, "1 Stk", 50, "Gurke")
I("salat", "Blattsalat", OG, 1, "Stk", 1.29, "", 0, "1 Stk", 40, "Blattsalat")
I("rucola", "Rucola", OG, 125, "g", 1.49, "", 0, "125 g", 0.25)
I("champignons", "Champignons", OG, 250, "g", 1.69, "", 0, "250 g", 0.22)
I("lauch", "Lauch", OG, 1, "Stk", 0.99, "", 0, "1 Stk", 60, "Lauch")
I("kuerbis", "Hokkaido-Kürbis", OG, 1, "Stk", 1.99, "", 0, "1 Stk", 450, "Hokkaido-Kürbis")
I("avocado", "Avocados", OG, 2, "Stk", 1.99, "", 0, "2 Stk", 240, "Avocado")
I("zitrone", "Zitronen", OG, 5, "Stk", 1.29, "", 1, "500 g", 20, "Zitrone")
I("limette", "Limetten", OG, 4, "Stk", 1.29, "", 1, "4 Stk", 15, "Limette")
I("ingwer", "Ingwer", OG, 150, "g", 0.99, "", 1, "150 g", 0.8)
I("chili", "Chilischoten", OG, 5, "Stk", 0.99, "", 1, "50 g", 4, "Chilischote")
I("fzwiebel", "Frühlingszwiebeln", OG, 1, "Bund", 0.79, "", 1, "1 Bund", 30)
I("kraeuter", "Petersilie", OG, 1, "Bund", 0.99, "", 1, "1 Bund", 20)
I("schnittlauch", "Schnittlauch", OG, 1, "Bund", 0.99, "", 1, "1 Bund", 15)
I("basilikum", "Basilikum", OG, 1, "Bund", 1.79, "", 1, "1 Topf", 15)
I("koriander", "Koriander", OG, 1, "Bund", 1.29, "", 1, "1 Bund", 15)
I("dill", "Dille", OG, 1, "Bund", 0.99, "", 1, "1 Bund", 15)
I("banane", "Bananen", OG, 6, "Stk", 1.49, "", 0, "1 kg", 105, "Banane")
I("apfel", "Äpfel", OG, 6, "Stk", 1.99, "", 0, "1 kg", 80, "Apfel")
I("birne", "Birnen", OG, 5, "Stk", 1.99, "", 0, "1 kg", 90, "Birne")
I("orange", "Orangen", OG, 5, "Stk", 1.99, "", 0, "1 kg", 70, "Orange")

# ---------- Tiefkühl ----------
I("spinat", "Blattspinat (TK)", TK, 450, "g", 1.29, "", 0, "450 g", 0.25)
I("erbsen", "Erbsen (TK)", TK, 450, "g", 1.29, "", 0, "450 g", 0.8)
I("gruenebohnen", "Grüne Bohnen (TK)", TK, 450, "g", 1.49, "", 0, "450 g", 0.3)
I("wokgemuese", "Wokgemüse (TK)", TK, 450, "g", 1.79, "", 0, "450 g", 0.35)
I("pommes", "Backofen-Pommes (TK)", TK, 1000, "g", 2.29, "", 0, "1 kg", 1.5)
I("beeren", "Beerenmix (TK)", TK, 500, "g", 2.99, "", 0, "500 g", 0.5)

# ---------- Konserven ----------
I("kichererbsen", "Kichererbsen", KO, 240, "g", 0.89, "huelse", 0, "Dose", 1.2)
I("kidney", "Kidneybohnen", KO, 240, "g", 0.79, "huelse", 0, "Dose", 1.0)
I("bohnenw", "Weiße Bohnen", KO, 240, "g", 0.79, "huelse", 0, "Dose", 1.0)
I("linsendose", "Linsen (Dose)", KO, 265, "g", 0.99, "huelse", 0, "Dose", 1.0)
I("mais", "Mais", KO, 140, "g", 0.89, "", 0, "Dose", 0.85)
I("tomdose", "Gehackte Tomaten", KO, 400, "g", 0.69, "", 0, "Dose", 0.22)
I("passata", "Passierte Tomaten", KO, 500, "g", 0.79, "", 0, "500 g", 0.3)
I("tommark", "Tomatenmark", KO, 200, "g", 0.89, "", 1, "200 g", 0.8)
I("kokos", "Kokosmilch", KO, 400, "ml", 1.29, "", 0, "Dose", 1.8)
I("pesto", "Pesto Basilikum", KO, 190, "g", 1.69, "milch laktose nuss", 0, "Glas", 5.0)
I("oliven", "Oliven schwarz", KO, 150, "g", 1.49, "", 0, "Glas", 1.5)
I("ajvar", "Ajvar", KO, 350, "g", 1.99, "", 0, "Glas", 0.9)
I("sauerkraut", "Sauerkraut", KO, 500, "g", 1.29, "", 0, "500 g", 0.2)
I("gurkerl", "Essiggurkerl", KO, 330, "g", 1.49, "", 0, "Glas", 0.2)
I("apfelmus", "Apfelmus", KO, 700, "g", 1.29, "", 0, "Glas", 0.7)
I("currypaste", "Rote Currypaste", KO, 7, "EL", 1.99, "", 0, "Glas", 15)

# ---------- Gewürze & Öle ----------
I("soja", "Sojasauce", GW, 16, "EL", 1.49, "soja gluten", 0, "250 ml", 10)
I("bruehe", "Gemüsebrühe", GW, 40, "TL", 1.49, "", 1, "Glas", 10)
I("curry", "Currypulver", GW, 25, "TL", 1.29, "", 1, "Dose", 6)
I("paprikap", "Paprikapulver", GW, 25, "TL", 0.99, "", 1, "Dose", 6)
I("kreuzk", "Kreuzkümmel", GW, 20, "TL", 1.29, "", 1, "Dose", 8)
I("kuemmel", "Kümmel", GW, 20, "TL", 0.99, "", 1, "Dose", 8)
I("oregano", "Oregano", GW, 25, "TL", 0.99, "", 1, "Dose", 3)
I("majoran", "Majoran", GW, 25, "TL", 0.99, "", 1, "Dose", 3)
I("thymian", "Thymian", GW, 25, "TL", 0.99, "", 1, "Dose", 3)
I("zimt", "Zimt", GW, 25, "TL", 0.99, "", 1, "Dose", 6)
I("chiliflocken", "Chiliflocken", GW, 25, "TL", 1.49, "", 1, "Dose", 6)
I("vanillezucker", "Vanillezucker", GW, 10, "Pkg", 0.99, "", 1, "10 Pkg", 30)
I("backpulver", "Backpulver", GW, 10, "TL", 0.69, "", 1, "5 Pkg", 5)
I("senf", "Senf", GW, 200, "g", 0.99, "", 1, "Tube", 1.0)
I("essig", "Weißweinessig", GW, 33, "EL", 0.99, "", 1, "500 ml", 2)
I("oel", "Rapsöl", GW, 66, "EL", 2.49, "", 0, "1 l", 120)
I("olivenoel", "Olivenöl", GW, 33, "EL", 5.99, "", 0, "500 ml", 120)

CATEGORY_ORDER = [OG, BR, KR, FL, TK, TR, KO, GW]
PANTRY_ORDER = [GW, TR, KO, KR, OG, TK, BR, FL]
DEFAULT_PANTRY = ["oel", "olivenoel", "paprikap", "oregano", "kreuzk", "kuemmel", "curry", "bruehe",
                  "majoran", "thymian", "zimt", "zucker", "essig", "senf", "backpulver", "vanillezucker"]
