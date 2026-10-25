from . import R

# ---------- Mexikanisch ----------
R("chili-sin-carne", "Chili sin Carne", "🌶️", "mex leicht guenstig", 35, "H",
  {"kidney": 120, "mais": 70, "tomdose": 200, "zwiebel": .5, "knoblauch": 1, "paprika": .5, "kreuzk": .5, "paprikap": 1, "chiliflocken": .1, "reis": 80, "oel": 1, "sauerrahm": 30},
  ["{reis} mit der doppelten Menge Salzwasser 15 Minuten quellen lassen.",
   "{zwiebel}, {knoblauch} und {paprika} würfeln und in {oel} 5 Minuten anbraten.",
   "{kreuzk}, {paprikap} und {chiliflocken} 30 Sekunden mitrösten.",
   "{tomdose}, abgespülte {kidney} und {mais} dazugeben, salzen und ca. 20 Minuten köcheln, bis das Chili dicklich ist.",
   "Mit einem Klecks {sauerrahm} und dem Reis servieren."],
  tip="Ein Stück dunkle Schokolade in der Sauce gibt Tiefe.")

R("chili-con-carne", "Chili con Carne", "🌶️", "mex protein familie", 40, "H",
  {"rindfasch": 125, "kidney": 100, "mais": 50, "tomdose": 200, "zwiebel": .5, "knoblauch": 1, "kreuzk": .5, "paprikap": 1, "chiliflocken": .1, "reis": 70, "oel": 1},
  ["{reis} kochen.",
   "{rindfasch} in {oel} bei hoher Hitze krümelig braten, bis es braun ist.",
   "Gehackte {zwiebel} und {knoblauch} 3 Minuten mitbraten, {kreuzk}, {paprikap} und {chiliflocken} kurz mitrösten.",
   "{tomdose}, {kidney} und {mais} einrühren, salzen und zugedeckt 25 Minuten köcheln.",
   "Abschmecken und mit Reis servieren."])

R("huehner-wraps", "Hühner-Wraps", "🌯", "mex protein schnell", 20, "HA",
  {"tortilla": 2, "huhn": 120, "salat": .25, "tomaten": 80, "mais": 40, "sauerrahm": 40, "paprikap": .5, "kreuzk": .25, "oel": .5, "limette": .25},
  ["{huhn} in Streifen schneiden und mit {paprikap}, {kreuzk}, Salz und {oel} mischen.",
   "In einer heißen Pfanne 6–8 Minuten braten, bis es durch ist (Airfryer: 10 Minuten bei 200 °C). Mit Saft von {limette} beträufeln.",
   "{salat} in Streifen schneiden, {tomaten} würfeln.",
   "{tortilla} in einer trockenen Pfanne kurz erwärmen.",
   "Mit {sauerrahm} bestreichen, mit Huhn, Salat, Tomaten und {mais} füllen und fest einrollen."])

R("bohnen-quesadillas", "Bohnen-Quesadillas", "🫓", "mex schnell", 20, "HA",
  {"tortilla": 2, "kidney": 80, "mais": 40, "reibkaese": 50, "paprika": .5, "kreuzk": .25, "salat": .2, "sauerrahm": 30},
  ["{kidney} abspülen und mit einer Gabel grob zerdrücken. Mit {kreuzk} und Salz würzen.",
   "{paprika} fein würfeln.",
   "Eine Hälfte jeder {tortilla} mit Bohnenmus bestreichen, mit {mais}, Paprika und {reibkaese} belegen und zuklappen.",
   "In einer Pfanne ohne Fett bei mittlerer Hitze je Seite 3 Minuten braten, bis sie knusprig sind und der Käse schmilzt (Airfryer: 6 Minuten bei 190 °C).",
   "In Dreiecke schneiden und mit {sauerrahm} und {salat} servieren."])

R("taco-bowl", "Taco-Bowl", "🌮", "mex protein", 25, "H",
  {"rindfasch": 110, "reis": 60, "kidney": 60, "mais": 50, "tomaten": 80, "salat": .25, "sauerrahm": 30, "kreuzk": .5, "paprikap": .5, "limette": .25, "avocado": .3},
  ["{reis} kochen und mit Saft von {limette} und Salz mischen.",
   "{rindfasch} mit {kreuzk} und {paprikap} krümelig braten, salzen. {kidney} abgespült 2 Minuten mitwärmen.",
   "{tomaten} würfeln, {salat} in Streifen schneiden, {avocado} in Würfel.",
   "Alles in Schüsseln anrichten, {mais} dazugeben und mit {sauerrahm} servieren."])

R("bohnen-burrito", "Bohnen-Burrito", "🌯", "mex guenstig", 25, "H",
  {"tortilla": 2, "reis": 50, "kidney": 100, "mais": 50, "paprika": .3, "tomaten": 60, "avocado": .3, "kreuzk": .5, "reibkaese": 25, "oel": .5},
  ["{reis} kochen.",
   "{paprika} würfeln und in {oel} 3 Minuten anbraten. Abgespülte {kidney} und {kreuzk} dazugeben, salzen und leicht zerdrücken.",
   "{tomaten} und {avocado} würfeln.",
   "{tortilla} erwärmen und in die Mitte Reis, Bohnen, {mais}, Tomaten, Avocado und {reibkaese} geben.",
   "Seiten einschlagen, fest einrollen und mit der Naht nach unten in einer Pfanne 2 Minuten anbraten."])

R("enchiladas", "Überbackene Enchiladas", "🌯", "mex familie protein", 40, "B H",
  {"tortilla": 2, "huhn": 100, "kidney": 60, "passata": 120, "reibkaese": 40, "zwiebel": .3, "kreuzk": .5, "paprikap": .5, "sauerrahm": 30},
  ["Backrohr auf 200 °C vorheizen.",
   "{huhn} klein würfeln und mit gehackter {zwiebel}, {kreuzk} und {paprikap} 5 Minuten anbraten. {kidney} dazugeben und salzen.",
   "{passata} mit Salz und etwas Kreuzkümmel würzen, ein Drittel in eine Auflaufform streichen.",
   "{tortilla} mit der Füllung belegen, einrollen und eng in die Form legen.",
   "Restliche Passata darübergießen und mit {reibkaese} bestreuen.",
   "Ca. 20 Minuten überbacken und mit {sauerrahm} servieren."])

R("ofenkartoffel-bohnen", "Ofenkartoffel mit Bohnen & Käse", "🥔", "mex guenstig schnell", 20, "MBA",
  {"kartoffeln": 300, "kidney": 80, "reibkaese": 30, "sauerrahm": 30, "fzwiebel": .25, "kreuzk": .25},
  ["{kartoffeln} waschen, mehrmals mit einer Gabel einstechen und in der Mikrowelle auf voller Stufe 8–10 Minuten garen, nach der Hälfte wenden (Backrohr: 45 Minuten bei 200 °C).",
   "{kidney} abspülen und mit {kreuzk} und Salz kurz erwärmen.",
   "Erdäpfel längs aufschneiden, etwas auseinanderdrücken und salzen.",
   "Bohnen und {reibkaese} darauf verteilen und 1–2 Minuten weitergaren, bis der Käse schmilzt.",
   "Mit {sauerrahm} und {fzwiebel} servieren."])

R("fajitas", "Hühner-Fajitas", "🌮", "mex protein familie", 25, "H",
  {"huhn": 130, "paprika": 1, "zwiebel": .5, "tortilla": 2, "sauerrahm": 40, "limette": .25, "paprikap": 1, "kreuzk": .5, "oel": 1, "avocado": .3},
  ["{huhn} in Streifen schneiden und mit {paprikap}, {kreuzk}, Salz und der Hälfte des {oel} mischen.",
   "{paprika} und {zwiebel} in Streifen schneiden.",
   "Eine Pfanne sehr heiß werden lassen und das Huhn 4 Minuten scharf anbraten. Herausnehmen.",
   "Restliches Öl, Paprika und Zwiebel 4–5 Minuten braten, bis sie Röstspuren haben, aber noch Biss.",
   "Huhn zurückgeben und mit Saft von {limette} beträufeln.",
   "Mit erwärmten {tortilla}, {sauerrahm} und zerdrückter {avocado} am Tisch selbst füllen."])

R("mex-reis-topf", "Mexikanischer Reis-Bohnen-Topf", "🍲", "mex guenstig leicht", 30, "H",
  {"reis": 70, "kidney": 80, "mais": 50, "tomdose": 120, "paprika": .5, "zwiebel": .5, "kreuzk": .5, "paprikap": .5, "bruehe": 1, "oel": 1, "reibkaese": 25, "limette": .25},
  ["{zwiebel} und {paprika} würfeln und in {oel} 4 Minuten anbraten.",
   "{reis}, {kreuzk} und {paprikap} 1 Minute mitrösten.",
   "{tomdose}, {bruehe} und {=180 ml} Wasser dazugeben, aufkochen und zugedeckt 15 Minuten bei kleiner Hitze garen.",
   "Abgespülte {kidney} und {mais} unterheben und 5 Minuten zugedeckt ziehen lassen.",
   "Mit Saft von {limette} abschmecken und mit {reibkaese} bestreuen."])

R("suesskartoffel-tacos", "Süßkartoffel-Bohnen-Tacos", "🌮", "mex leicht", 30, "BA H",
  {"suesskart": 150, "kidney": 70, "tortilla": 2, "weisskraut": 50, "limette": .3, "joghurt": 40, "kreuzk": .5, "paprikap": .5, "oel": 1, "koriander": .2},
  ["Backrohr auf 210 °C vorheizen. {suesskart} in 1,5 cm Würfel schneiden, mit {oel}, {kreuzk}, {paprikap} und Salz mischen und 20 Minuten rösten.",
   "{weisskraut} sehr fein schneiden und mit Saft von {limette} und Salz verkneten.",
   "{kidney} abspülen und kurz erwärmen.",
   "{tortilla} in einer trockenen Pfanne erwärmen.",
   "Mit Süßkartoffeln, Bohnen, Kraut und {joghurt} füllen und mit {koriander} bestreuen."])

R("tortilla-suppe", "Tortilla-Suppe mit Huhn", "🍲", "mex protein leicht", 30, "H",
  {"huhn": 100, "tomdose": 150, "mais": 40, "kidney": 50, "zwiebel": .5, "knoblauch": 1, "kreuzk": .5, "bruehe": 1, "tortilla": .5, "avocado": .3, "limette": .25, "oel": 1},
  ["{zwiebel} und {knoblauch} hacken und in {oel} 3 Minuten anschwitzen, {kreuzk} kurz mitrösten.",
   "{tomdose}, {bruehe} und {=350 ml} Wasser dazugeben und aufkochen.",
   "{huhn} im Ganzen hineinlegen und 15 Minuten leise köcheln. Herausnehmen und mit zwei Gabeln zerzupfen.",
   "Fleisch, {mais} und abgespülte {kidney} zurück in die Suppe geben und mit Saft von {limette} und Salz abschmecken.",
   "{tortilla} in Streifen schneiden und in einer trockenen Pfanne knusprig rösten.",
   "Suppe mit Tortilla-Streifen und {avocado}-Würfeln servieren."])

R("chili-mac", "Chili-Käse-Nudeln aus einem Topf", "🧀", "mex familie", 30, "H",
  {"nudeln": 100, "rindfasch": 90, "kidney": 50, "passata": 150, "zwiebel": .3, "kreuzk": .5, "paprikap": .5, "reibkaese": 40, "bruehe": 1},
  ["{rindfasch} mit gehackter {zwiebel} krümelig braten, {kreuzk} und {paprikap} kurz mitrösten.",
   "{passata}, {bruehe} und {=250 ml} Wasser dazugeben und aufkochen.",
   "{nudeln} (kurze Sorte) roh dazugeben und unter häufigem Rühren ca. 12 Minuten garen, bis die Nudeln weich und die Sauce dick ist.",
   "{kidney} abgespült unterrühren.",
   "{reibkaese} unterrühren, bis er schmilzt, und sofort servieren."])

R("fisch-tacos", "Fisch-Tacos mit Krautsalat", "🐟", "mex protein", 30, "HA",
  {"weissfisch": 130, "tortilla": 2, "weisskraut": 60, "limette": .5, "sauerrahm": 40, "paprikap": .5, "kreuzk": .25, "mehl": 10, "oel": 1, "koriander": .2},
  ["{weissfisch} auftauen, trocken tupfen, in Streifen schneiden und mit {paprikap}, {kreuzk} und Salz würzen. In {mehl} wenden.",
   "{weisskraut} sehr fein schneiden und mit der Hälfte vom Saft der {limette} und Salz verkneten.",
   "{sauerrahm} mit restlichem Limettensaft verrühren.",
   "Fisch in {oel} je Seite 2–3 Minuten knusprig braten (Airfryer: 10 Minuten bei 200 °C).",
   "{tortilla} erwärmen, mit Kraut, Fisch und Limetten-Sauerrahm füllen und mit {koriander} bestreuen."])

# ---------- Familienküche & International ----------
R("burger-pommes", "Burger mit Ofenpommes", "🍔", "familie protein", 35, "H BA",
  {"rindfasch": 140, "burgerbun": 1, "salat": .15, "tomaten": 60, "kaesesch": 20, "gurkerl": 20, "rotezwiebel": .2, "pommes": 150, "senf": 5, "tommark": 5},
  ["Backrohr laut Packung vorheizen und {pommes} auf einem Blech ca. 20 Minuten knusprig backen (Airfryer: 15 Minuten).",
   "{rindfasch} mit Salz und Pfeffer locker zu flachen Laibchen formen (etwas größer als das Brötchen, sie schrumpfen). In die Mitte eine kleine Mulde drücken.",
   "Laibchen in einer sehr heißen Pfanne je Seite ca. 3 Minuten braten. Nach dem Wenden {kaesesch} darauflegen.",
   "{burgerbun} aufschneiden und mit der Schnittfläche kurz in der Pfanne rösten.",
   "{senf} mit {tommark} und etwas Wasser zu einer Burgersauce verrühren.",
   "Brötchen mit Sauce, {salat}, Laibchen, {tomaten}, {gurkerl} und {rotezwiebel} belegen. Mit Pommes servieren."])

R("veggie-burger", "Bohnenburger mit Ofenpommes", "🍔", "familie", 40, "H BA",
  {"kidney": 100, "hafer": 25, "eier": .5, "zwiebel": .2, "kreuzk": .25, "paprikap": .5, "burgerbun": 1, "salat": .15, "tomaten": 60, "pommes": 150, "joghurt": 30, "oel": 1},
  ["{pommes} im Backrohr oder Airfryer laut Packung knusprig backen.",
   "{kidney} abspülen, gut abtropfen lassen und mit einer Gabel fein zerdrücken.",
   "Mit {hafer}, {eier}, fein gehackter {zwiebel}, {kreuzk}, {paprikap} und Salz verkneten. 10 Minuten quellen lassen.",
   "Flache Laibchen formen und in {oel} bei mittlerer Hitze je Seite 4 Minuten knusprig braten.",
   "{burgerbun} rösten, mit {joghurt}, {salat}, Laibchen und {tomaten} belegen."])

R("mac-cheese-brokkoli", "Mac and Cheese mit Brokkoli", "🧀", "familie", 30, "H",
  {"nudeln": 110, "brokkoli": .3, "milch": 150, "butter": 10, "mehl": 10, "reibkaese": 50, "senf": 3},
  ["{nudeln} (am besten kurze Makkaroni) in Salzwasser kochen, die letzten 4 Minuten {brokkoli} in kleinen Röschen mitkochen. Abseihen.",
   "{butter} in einem Topf schmelzen, {mehl} einrühren und 1 Minute anschwitzen.",
   "{milch} nach und nach unter ständigem Rühren dazugießen und 3 Minuten dicklich köcheln.",
   "Vom Herd nehmen, {reibkaese} und {senf} einrühren, bis eine glatte Sauce entsteht. Mit Salz, Pfeffer und Muskat würzen.",
   "Nudeln und Brokkoli unterheben. Wer mag, überbackt das Ganze noch 10 Minuten bei 220 °C."])

R("chicken-nuggets", "Hühnernuggets mit Kartoffelspalten", "🍗", "familie protein", 40, "AB",
  {"huhn": 140, "eier": .5, "broesel": 30, "paprikap": .5, "kartoffeln": 220, "oel": 1, "joghurt": 50, "tommark": 5, "honig": 3},
  ["{kartoffeln} in Spalten schneiden, mit der Hälfte des {oel}, Salz und Paprikapulver mischen und im Airfryer 20 Minuten bei 200 °C garen (Backrohr: 35 Minuten bei 220 °C).",
   "{huhn} in mundgerechte Stücke schneiden und salzen.",
   "{broesel} mit {paprikap} mischen. Huhn durch verquirltes {eier} ziehen und in den Bröseln wenden.",
   "Mit restlichem Öl beträufeln und 10–12 Minuten bei 200 °C knusprig backen, nach der Hälfte wenden.",
   "{joghurt} mit Salz verrühren, {tommark} mit {honig} und einem Schuss Wasser zu Ketchup verrühren.",
   "Nuggets mit Spalten und den beiden Dips servieren."])

R("shepherds-pie", "Shepherd’s Pie", "🥧", "familie protein", 60, "B H",
  {"faschiert": 120, "karotten": 60, "erbsen": 50, "zwiebel": .5, "tommark": 10, "bruehe": .5, "thymian": .25, "kartoffeln": 250, "milch": 60, "butter": 10, "reibkaese": 20},
  ["{kartoffeln} schälen und in Salzwasser 15 Minuten weich kochen, dann mit warmer {milch} und {butter} zu Püree stampfen.",
   "Backrohr auf 200 °C vorheizen.",
   "{zwiebel} und {karotten} würfeln und mit dem {faschiert} krümelig anbraten.",
   "{tommark} und {thymian} einrühren, mit {bruehe} und {=100 ml} Wasser aufgießen und 10 Minuten köcheln. {erbsen} dazugeben.",
   "Fleisch in eine Form geben, Püree darauf verstreichen, mit einer Gabel Rillen ziehen und mit {reibkaese} bestreuen.",
   "Ca. 25 Minuten backen, bis die Oberfläche goldbraun ist."])

R("fish-chips", "Fish & Chips aus dem Ofen", "🐟", "familie protein", 35, "BA",
  {"weissfisch": 150, "mehl": 10, "eier": .5, "broesel": 30, "pommes": 180, "erbsen": 80, "zitrone": .25, "joghurt": 40, "gurkerl": 15, "oel": 1},
  ["{pommes} im Backrohr oder Airfryer laut Packung backen.",
   "{weissfisch} auftauen, trocken tupfen, salzen und in Stücke schneiden.",
   "In {mehl}, verquirltem {eier} und {broesel} panieren, mit {oel} beträufeln.",
   "Bei 200 °C ca. 15 Minuten knusprig backen (Airfryer: 10 Minuten).",
   "{erbsen} in Salzwasser 4 Minuten kochen und grob zerdrücken, mit Salz und etwas Butter abschmecken.",
   "{joghurt} mit fein gehackten {gurkerl} verrühren. Alles mit {zitrone} servieren."])

R("caesar-salat", "Hühner-Caesar-Salat", "🥗", "familie protein leicht", 25, "H",
  {"huhn": 130, "salat": .5, "parmesan": 20, "toast": 40, "joghurt": 50, "senf": 5, "knoblauch": .5, "zitrone": .25, "olivenoel": 1.5},
  ["{huhn} salzen, pfeffern und in der Hälfte des {olivenoel} je Seite 5 Minuten braten, bis es durch ist. Kurz rasten lassen und in Scheiben schneiden.",
   "{toast} in Würfel schneiden und im restlichen Öl goldbraun rösten.",
   "{joghurt} mit {senf}, geriebenem {knoblauch}, Saft von {zitrone}, der Hälfte vom geriebenen {parmesan}, Salz und Pfeffer zu einem Dressing verrühren.",
   "{salat} (am besten Römersalat) in Streifen schneiden und mit dem Dressing mischen.",
   "Mit Huhn, Croûtons und restlichem Parmesan anrichten."])

R("lauch-speck-quiche", "Lauch-Speck-Quiche", "🥧", "familie", 50, "B",
  {"blaetterteig": .4, "lauch": .5, "speck": 30, "eier": 1, "obers": 60, "reibkaese": 25, "salat": .25},
  ["Backrohr auf 200 °C vorheizen. Eine Tarte- oder Auflaufform mit dem {blaetterteig} auslegen, den Boden mehrmals mit einer Gabel einstechen.",
   "{lauch} in feine Ringe schneiden und mit {speck} 5 Minuten andünsten.",
   "{eier} mit {obers}, {reibkaese}, Salz, Pfeffer und Muskat verquirlen.",
   "Lauch und Speck auf dem Teig verteilen und mit der Eiermasse übergießen.",
   "Ca. 30 Minuten backen, bis die Füllung gestockt und goldbraun ist.",
   "Mit {salat} servieren."])

R("gemuese-quiche", "Brokkoli-Frischkäse-Quiche", "🥧", "familie leicht", 50, "B",
  {"blaetterteig": .4, "brokkoli": .3, "cherry": 50, "eier": 1, "frischkaese": 40, "milch": 50, "reibkaese": 20, "salat": .25},
  ["Backrohr auf 200 °C vorheizen. Form mit {blaetterteig} auslegen und den Boden einstechen.",
   "{brokkoli} in kleine Röschen teilen und 3 Minuten in Salzwasser blanchieren.",
   "{eier}, {frischkaese} und {milch} glatt verquirlen, mit Salz, Pfeffer und Muskat würzen.",
   "Brokkoli und halbierte {cherry} verteilen, Guss darübergießen und mit {reibkaese} bestreuen.",
   "Ca. 30 Minuten goldbraun backen. Mit {salat} servieren."])

R("tomatensuppe-toast", "Tomatensuppe mit Käsetoast", "🍅", "familie schnell", 25, "H X",
  {"tomdose": 200, "passata": 100, "zwiebel": .5, "knoblauch": 1, "bruehe": .5, "obers": 30, "olivenoel": 1, "zucker": 3, "toast": 60, "kaesesch": 30, "butter": 5, "basilikum": .2},
  ["{zwiebel} und {knoblauch} hacken und in {olivenoel} 4 Minuten anschwitzen.",
   "{tomdose}, {passata}, {bruehe}, {zucker} und {=150 ml} Wasser dazugeben und 12 Minuten köcheln.",
   "Fein pürieren, {obers} einrühren und mit Salz und Pfeffer abschmecken.",
   "{toast} mit {kaesesch} belegen, zuklappen, außen dünn mit {butter} bestreichen und in einer Pfanne je Seite 2 Minuten goldbraun braten, bis der Käse schmilzt (oder im Toaster).",
   "Suppe mit {basilikum} bestreuen und mit den Käsetoasts zum Eintunken servieren."])

R("brokkolicremesuppe", "Brokkolicremesuppe mit Croûtons", "🥦", "familie leicht", 25, "H X",
  {"brokkoli": .5, "kartoffeln": 80, "zwiebel": .25, "bruehe": 1, "frischkaese": 25, "toast": 30, "butter": 10},
  ["{brokkoli} in Röschen teilen, den Strunk schälen und würfeln. {kartoffeln} und {zwiebel} würfeln.",
   "Zwiebel in der Hälfte der {butter} anschwitzen, Gemüse kurz mitdünsten.",
   "Mit {=350 ml} Wasser und {bruehe} aufgießen und 12 Minuten weich kochen.",
   "{frischkaese} dazugeben und fein pürieren. Mit Salz, Pfeffer und Muskat abschmecken.",
   "{toast} würfeln und in restlicher Butter goldbraun rösten. Über die Suppe streuen."])

R("zucchinicremesuppe", "Zucchinicremesuppe mit Feta", "🥒", "medi leicht", 25, "H X",
  {"zucchini": .8, "kartoffeln": 60, "zwiebel": .25, "knoblauch": .5, "bruehe": 1, "feta": 30, "olivenoel": 1, "brot": 50},
  ["{zucchini}, {kartoffeln} und {zwiebel} würfeln.",
   "Mit {knoblauch} in {olivenoel} 4 Minuten anschwitzen.",
   "{=350 ml} Wasser und {bruehe} angießen und 12 Minuten köcheln.",
   "Fein pürieren und mit Salz und Pfeffer abschmecken.",
   "Mit zerbröseltem {feta} und {brot} servieren."], season="6-9")

R("hot-dogs-krautsalat", "Hot Dogs mit Krautsalat", "🌭", "familie schnell", 20, "H",
  {"wuerstel": 2, "semmeln": 1, "weisskraut": 80, "karotten": 30, "joghurt": 30, "senf": 10, "gurkerl": 20, "rotezwiebel": .2, "essig": .5},
  ["{weisskraut} fein hobeln, {karotten} raspeln, mit Salz kräftig durchkneten.",
   "{joghurt} mit {essig}, einer Prise Zucker und Pfeffer verrühren und mit dem Kraut mischen.",
   "{wuerstel} 5 Minuten in heißem Wasser ziehen lassen.",
   "{semmeln} (oder Hot-Dog-Weckerl) einschneiden und kurz aufbacken.",
   "Mit Würstel, {senf}, gehackten {gurkerl}, {rotezwiebel} und Krautsalat füllen."])

R("zitronen-hendl", "Zitronen-Hendl mit Ofengemüse", "🍋", "medi protein familie", 50, "BA",
  {"huhnkeule": 280, "zitrone": .5, "knoblauch": 1.5, "thymian": .5, "kartoffeln": 180, "karotten": 80, "rotezwiebel": .5, "olivenoel": 1},
  ["Backrohr auf 200 °C Umluft vorheizen.",
   "{kartoffeln} und {karotten} in Stücke, {rotezwiebel} in Spalten schneiden. Mit der Hälfte des {olivenoel}, Salz und {thymian} auf einem Blech mischen.",
   "{huhnkeule} mit restlichem Öl, Salz, gepresstem {knoblauch} und Abrieb von {zitrone} einreiben und auf das Gemüse legen.",
   "Zitrone in Spalten dazulegen und ca. 45 Minuten braten, bis die Haut knusprig ist.",
   "Vor dem Servieren die gebratenen Zitronenspalten über Huhn und Gemüse ausdrücken."])

R("raeuchertofu-erdaepfel", "Räuchertofu-Kraut-Pfanne mit Erdäpfeln", "🥔", "oesterr leicht", 35, "H",
  {"raeuchertofu": 100, "kartoffeln": 200, "weisskraut": 120, "zwiebel": .5, "kuemmel": .25, "paprikap": .5, "oel": 1.5, "schnittlauch": .2},
  ["{kartoffeln} in der Schale 15 Minuten vorkochen, schälen und würfeln (oder Reste nehmen).",
   "{raeuchertofu} würfeln und in der Hälfte des {oel} knusprig braten. Herausnehmen.",
   "Erdäpfel im restlichen Öl 8 Minuten goldbraun braten.",
   "{weisskraut} in Streifen und {zwiebel} in Ringen dazugeben und 6 Minuten mitbraten. Mit {kuemmel}, {paprikap} und Salz würzen.",
   "Tofu untermischen und mit {schnittlauch} bestreuen."])

R("quinoa-gemuese-pfanne", "Quinoa-Gemüse-Pfanne", "🥗", "leicht medi", 30, "H",
  {"quinoa": 70, "zucchini": .4, "paprika": .5, "mais": 40, "kidney": 60, "zwiebel": .3, "kreuzk": .25, "bruehe": 1, "olivenoel": 1, "limette": .25, "kraeuter": .2},
  ["{quinoa} in einem Sieb heiß abspülen.",
   "{zwiebel}, {zucchini} und {paprika} würfeln und in {olivenoel} 4 Minuten anbraten.",
   "Quinoa und {kreuzk} kurz mitrösten, {bruehe} und {=150 ml} Wasser dazugeben.",
   "Zugedeckt 15 Minuten bei kleiner Hitze garen.",
   "Abgespülte {kidney} und {mais} unterheben, mit Saft von {limette} und {kraeuter} abschmecken."])

R("schupfnudel-gemuese", "Schupfnudel-Gemüsepfanne", "🥕", "oesterr schnell", 20, "H",
  {"schupfnudeln": 200, "karotten": 60, "zucchini": .3, "erbsen": 50, "zwiebel": .3, "butter": 10, "sauerrahm": 30, "schnittlauch": .2},
  ["{karotten} in dünne Scheiben, {zucchini} in Halbmonde, {zwiebel} in Streifen schneiden.",
   "{schupfnudeln} in {butter} bei mittlerer Hitze 5 Minuten goldbraun braten. An den Rand schieben.",
   "Karotten und Zwiebel 3 Minuten mitbraten, dann Zucchini und {erbsen} weitere 3 Minuten.",
   "Salzen, pfeffern, mit {sauerrahm} und {schnittlauch} servieren."])

R("griessbrei-beeren", "Grießkoch mit Beeren", "🥣", "oesterr suess schnell", 15, "H",
  {"milch": 280, "gries": 45, "zucker": 12, "vanillezucker": .5, "butter": 5, "beeren": 80, "zimt": .25},
  ["{milch} mit {vanillezucker}, {zucker}, {butter} und einer Prise Salz aufkochen.",
   "{gries} einrieseln lassen und unter Rühren 3 Minuten köcheln, bis er dick wird.",
   "Vom Herd nehmen und 2 Minuten nachquellen lassen.",
   "{beeren} kurz erwärmen.",
   "Grießkoch mit Beeren und {zimt} servieren."])
