from . import R

# Rein pflanzliche Gerichte (Honig/Butter/Milch werden für Veganer ohnehin automatisch ersetzt).
R("suesskartoffel-chili", "Süßkartoffel-Chili", "🌶️", "mex leicht guenstig", 40, "H",
  {"suesskart": 150, "kidney": 100, "mais": 50, "tomdose": 200, "zwiebel": .5, "knoblauch": 1, "kreuzk": .5, "paprikap": 1, "chiliflocken": .1, "oel": 1, "limette": .25, "koriander": .2, "reis": 50},
  ["{reis} kochen.",
   "{zwiebel} und {knoblauch} hacken und in {oel} 4 Minuten anschwitzen. {kreuzk}, {paprikap} und {chiliflocken} 30 Sekunden mitrösten.",
   "{suesskart} schälen, in 1,5 cm Würfel schneiden und kurz mitbraten.",
   "{tomdose} und {=150 ml} Wasser dazugeben, salzen und zugedeckt 15 Minuten köcheln, bis die Süßkartoffeln weich sind.",
   "Abgespülte {kidney} und {mais} unterrühren und weitere 5 Minuten köcheln.",
   "Mit Saft von {limette} abschmecken und mit {koriander} und Reis servieren."])

R("tofu-gulasch", "Räuchertofu-Gulasch mit Erdäpfeln", "🍲", "oesterr protein", 40, "H",
  {"raeuchertofu": 120, "zwiebel": 1, "paprika": .5, "paprikap": 2, "tommark": 15, "kuemmel": .25, "majoran": .25, "kartoffeln": 200, "oel": 1.5, "essig": .5},
  ["{raeuchertofu} in Würfel schneiden und in der Hälfte des {oel} rundum knusprig braten. Herausnehmen.",
   "{zwiebel} fein schneiden und im restlichen Öl ca. 10 Minuten goldbraun rösten.",
   "{tommark} und {paprikap} kurz einrühren, sofort mit {essig} und {=300 ml} Wasser ablöschen.",
   "{paprika} in Stücken, {kuemmel} und {majoran} dazugeben, salzen und 15 Minuten sämig köcheln.",
   "Inzwischen {kartoffeln} schälen und in Salzwasser 20 Minuten kochen.",
   "Tofu zurück in den Saft geben, 5 Minuten ziehen lassen und mit den Erdäpfeln servieren."])

R("linsen-shepherds-pie", "Linsen-Shepherd’s-Pie", "🥧", "familie leicht", 60, "B H",
  {"linsenbraun": 60, "karotten": 70, "zwiebel": .5, "champignons": 60, "tomdose": 100, "tommark": 10, "thymian": .25, "bruehe": 1, "kartoffeln": 250, "hafermilch": 60, "olivenoel": 1.5},
  ["{kartoffeln} schälen, in Salzwasser 15 Minuten weich kochen und mit warmer {hafermilch}, der Hälfte des {olivenoel}, Salz und Muskat zu Püree stampfen.",
   "{linsenbraun} abspülen und in {=300 ml} Wasser mit {bruehe} ca. 20 Minuten weich kochen.",
   "Backrohr auf 200 °C vorheizen. {zwiebel}, {karotten} und {champignons} würfeln und im restlichen Öl 6 Minuten braten.",
   "{tommark} kurz mitrösten, {tomdose}, {thymian} und die Linsen samt restlicher Flüssigkeit dazugeben und 5 Minuten dicklich köcheln.",
   "In eine Form füllen, Püree darauf verstreichen und mit einer Gabel Rillen ziehen.",
   "Ca. 25 Minuten backen, bis die Oberfläche goldbraun ist."])

R("pilz-stroganoff", "Pilz-Stroganoff mit Nudeln", "🍄", "familie schnell", 25, "H",
  {"champignons": 200, "zwiebel": .5, "paprikap": 1, "senf": 5, "kokos": 80, "mehl": 5, "gurkerl": 30, "kraeuter": .25, "nudeln": 110, "oel": 1},
  ["{nudeln} in reichlich Salzwasser bissfest kochen.",
   "{champignons} in Scheiben schneiden, {zwiebel} in Streifen.",
   "Pilze in {oel} bei hoher Hitze 6 Minuten braten, bis sie Farbe haben. Zwiebel 2 Minuten mitbraten.",
   "{paprikap} und {mehl} darüberstäuben, kurz rühren, dann {kokos}, {senf} und {=60 ml} Wasser einrühren und 3 Minuten köcheln.",
   "{gurkerl} in feine Streifen schneiden und unterheben. Salzen und pfeffern.",
   "Mit den Nudeln und gehackter {kraeuter} servieren."])

R("gemuese-paella", "Gemüse-Paella", "🥘", "medi leicht", 40, "H",
  {"reis": 85, "paprika": .5, "gruenebohnen": 60, "erbsen": 40, "tomdose": 80, "zwiebel": .5, "knoblauch": 1, "paprikap": 1, "bruehe": 1, "olivenoel": 1.5, "zitrone": .25},
  ["{zwiebel}, {knoblauch} und {paprika} würfeln und in {olivenoel} in einer großen Pfanne 5 Minuten braten.",
   "{gruenebohnen} in Stücken 3 Minuten mitbraten.",
   "{paprikap} und {reis} 1 Minute mitrösten, {tomdose} einrühren.",
   "Mit {=260 ml} heißem Wasser und {bruehe} aufgießen, glatt streichen und ohne Umrühren ca. 18 Minuten bei mittlerer Hitze garen.",
   "Nach 12 Minuten {erbsen} darüberstreuen. Zum Schluss darf der Boden leicht ansetzen.",
   "Mit Zitronenspalten von {zitrone} servieren."])

R("bohnen-tacos", "Bohnen-Tacos mit Avocado-Salsa", "🌮", "mex schnell", 20, "H",
  {"kidney": 120, "tortilla": 2, "avocado": .5, "tomaten": 80, "rotezwiebel": .25, "limette": .5, "kreuzk": .5, "paprikap": .5, "salat": .15, "oel": .5},
  ["{kidney} abspülen und mit {kreuzk}, {paprikap}, {oel}, Salz und 2 EL Wasser in einer Pfanne 4 Minuten erwärmen, dabei grob zerdrücken.",
   "{avocado} und {tomaten} würfeln, {rotezwiebel} fein hacken und mit Saft von {limette} und Salz zu einer Salsa mischen.",
   "{tortilla} in einer trockenen Pfanne kurz erwärmen.",
   "Mit Bohnen, {salat} in Streifen und Salsa füllen."])

R("erdnuss-tofu-curry", "Erdnuss-Tofu-Curry", "🥜", "asia protein", 30, "H",
  {"tofu": 130, "erdnussb": 25, "kokos": 100, "brokkoli": .3, "karotten": 50, "curry": 1, "soja": 1, "limette": .25, "reis": 70, "oel": 1, "erdnuesse": 10},
  ["{reis} kochen.",
   "{tofu} würfeln und in {oel} rundum goldbraun braten.",
   "{curry} kurz mitrösten, dann {kokos}, {erdnussb}, {soja} und {=80 ml} Wasser einrühren.",
   "{brokkoli} in Röschen und {karotten} in Scheiben dazugeben und 8 Minuten köcheln.",
   "Mit Saft von {limette} abschmecken, mit gehackten {erdnuesse} bestreuen und mit Reis servieren."])

R("tofu-nudeln-wok", "Gebratene Nudeln mit Tofu & Wokgemüse", "🥡", "asia schnell", 20, "H",
  {"nudeln": 100, "tofu": 100, "wokgemuese": 150, "soja": 2, "ingwer": 5, "knoblauch": 1, "oel": 1, "sesam": 3, "chiliflocken": .1},
  ["{nudeln} bissfest kochen und abseihen.",
   "{tofu} würfeln und in der Hälfte des {oel} knusprig braten. Herausnehmen.",
   "Restliches Öl sehr heiß werden lassen und {wokgemuese} 5 Minuten braten.",
   "Nudeln, Tofu, gepressten {knoblauch}, geriebenen {ingwer}, {soja} und {chiliflocken} dazugeben und 2 Minuten durchschwenken.",
   "Mit {sesam} bestreuen."])

R("aloo-matar", "Erdäpfel-Erbsen-Curry", "🥔", "indisch guenstig leicht", 30, "H",
  {"kartoffeln": 200, "erbsen": 80, "tomdose": 120, "zwiebel": .5, "ingwer": 5, "knoblauch": 1, "curry": 1, "kreuzk": .5, "oel": 1, "koriander": .2, "fladenbrot": .2},
  ["{kartoffeln} schälen und in 2 cm Würfel schneiden.",
   "{kreuzk} in {oel} 30 Sekunden rösten, dann gehackte {zwiebel}, {ingwer} und {knoblauch} 4 Minuten anbraten.",
   "{curry} einrühren, Erdäpfel und {tomdose} dazugeben, mit {=150 ml} Wasser aufgießen und salzen.",
   "Zugedeckt ca. 15 Minuten köcheln, bis die Erdäpfel weich sind.",
   "{erbsen} dazugeben und 4 Minuten mitgaren.",
   "Mit {koriander} bestreuen und mit warmem {fladenbrot} servieren."])

R("quinoa-chili", "Quinoa-Chili", "🌶️", "mex leicht protein", 35, "H",
  {"quinoa": 40, "kidney": 100, "tomdose": 200, "mais": 40, "paprika": .5, "zwiebel": .5, "knoblauch": 1, "kreuzk": .5, "paprikap": 1, "oel": 1, "avocado": .3},
  ["{quinoa} heiß abspülen.",
   "{zwiebel}, {knoblauch} und {paprika} würfeln und in {oel} 4 Minuten anbraten, Gewürze ({kreuzk}, {paprikap}) kurz mitrösten.",
   "Quinoa, {tomdose} und {=200 ml} Wasser dazugeben, salzen und 15 Minuten köcheln.",
   "Abgespülte {kidney} und {mais} dazugeben und weitere 5 Minuten köcheln, bis die Quinoa weich ist.",
   "Mit {avocado}-Würfeln servieren."])

R("tofu-schnitzel", "Tofuschnitzel mit Erdäpfelsalat", "🥢", "oesterr protein", 45, "H",
  {"tofu": 150, "mehl": 30, "broesel": 40, "senf": 5, "paprikap": .25, "oel": 3, "kartoffeln": 220, "zwiebel": .25, "essig": 1, "bruehe": .5, "zitrone": .25},
  ["Erdäpfelsalat vorbereiten: {kartoffeln} kochen, schälen, in Scheiben schneiden und mit {=80 ml} heißem Wasser, {bruehe}, {essig}, 1 EL Öl, fein gehackter {zwiebel}, Salz und Pfeffer marinieren.",
   "{tofu} gut ausdrücken und in 1 cm dicke Scheiben schneiden. Salzen und mit {paprikap} würzen.",
   "Die Hälfte vom {mehl} mit {senf} und so viel Wasser verrühren, dass ein dickflüssiger Teig entsteht.",
   "Tofu in restlichem Mehl, dann im Teig und zuletzt in {broesel} wenden.",
   "In {oel} je Seite 3 Minuten goldbraun herausbacken.",
   "Mit Erdäpfelsalat und {zitrone} servieren."])

R("brokkoli-erdnuss-reis", "Brokkoli-Erdnuss-Reispfanne", "🥦", "asia schnell guenstig", 25, "H",
  {"reis": 80, "brokkoli": .4, "karotten": 50, "erdnuesse": 20, "soja": 1.5, "ingwer": 5, "knoblauch": 1, "oel": 1, "fzwiebel": .3, "limette": .25},
  ["{reis} kochen (oder Reste vom Vortag nehmen).",
   "{brokkoli} in kleine Röschen, {karotten} in Scheiben schneiden.",
   "{oel} sehr heiß werden lassen und das Gemüse 5 Minuten braten.",
   "Reis, gepressten {knoblauch} und geriebenen {ingwer} dazugeben und 3 Minuten mitbraten.",
   "Mit {soja} und Saft von {limette} würzen und mit gehackten {erdnuesse} und {fzwiebel} bestreuen."])

R("polenta-pilzragout", "Polenta mit Pilzragout", "🍄", "ital", 30, "H",
  {"polenta": 70, "champignons": 180, "tomdose": 100, "zwiebel": .5, "knoblauch": 1, "thymian": .25, "bruehe": 1, "olivenoel": 2, "kraeuter": .2},
  ["{champignons} vierteln und in der Hälfte des {olivenoel} bei hoher Hitze 6 Minuten braten.",
   "Gehackte {zwiebel} und {knoblauch} 2 Minuten mitbraten, {tomdose} und {thymian} dazugeben und 10 Minuten köcheln.",
   "{=300 ml} Wasser mit {bruehe} aufkochen, {polenta} einrieseln lassen und 5–10 Minuten unter Rühren köcheln.",
   "Restliches Olivenöl unter die Polenta rühren.",
   "Mit dem Pilzragout und {kraeuter} servieren."])

R("spinat-kichererbsen-pasta", "Pasta mit Kichererbsen, Spinat & Zitrone", "🍝", "ital leicht schnell", 20, "H",
  {"nudeln": 110, "kichererbsen": 80, "spinat": 100, "knoblauch": 1.5, "zitrone": .3, "chiliflocken": .1, "olivenoel": 1.5},
  ["{nudeln} bissfest kochen.",
   "Gehackten {knoblauch} und {chiliflocken} in {olivenoel} 1 Minute anschwitzen.",
   "Abgespülte {kichererbsen} 4 Minuten mitbraten, bis sie leicht knusprig sind.",
   "Aufgetauten {spinat} dazugeben und 3 Minuten dünsten.",
   "Nudeln mit einer halben Tasse Nudelwasser, Abrieb und Saft von {zitrone} untermischen und salzen."])

R("schupfnudeln-tofu-kraut", "Schupfnudeln mit Kraut & Räuchertofu", "🥬", "oesterr", 25, "H",
  {"schupfnudeln": 200, "weisskraut": 150, "raeuchertofu": 70, "zwiebel": .3, "kuemmel": .25, "oel": 1.5},
  ["{raeuchertofu} würfeln und in der Hälfte des {oel} knusprig braten. Herausnehmen.",
   "{weisskraut} in feine Streifen schneiden und mit {zwiebel} im restlichen Öl 8 Minuten braten, mit {kuemmel} und Salz würzen.",
   "{schupfnudeln} dazugeben und weitere 6 Minuten goldbraun mitbraten.",
   "Tofu untermischen und pfeffern."])

R("gefuellte-paprika-vegan", "Gefüllte Paprika mit Reis & Bohnen", "🫑", "mex familie", 50, "B H",
  {"paprika": 1.5, "reis": 45, "kidney": 70, "mais": 40, "tomdose": 150, "zwiebel": .5, "kreuzk": .5, "paprikap": .5, "olivenoel": 1, "kraeuter": .2},
  ["Backrohr auf 190 °C vorheizen. {reis} in Salzwasser 10 Minuten vorkochen und abseihen.",
   "{zwiebel} hacken und in {olivenoel} anschwitzen, {kreuzk} und {paprikap} kurz mitrösten.",
   "Reis, abgespülte {kidney}, {mais} und 2 EL der Tomaten untermischen, salzen.",
   "Von den {paprika} einen Deckel abschneiden, entkernen und füllen.",
   "Restliche {tomdose} gesalzen in eine Form geben, Paprika hineinsetzen, Deckel auflegen und ca. 35 Minuten backen.",
   "Mit {kraeuter} bestreuen."])

R("rote-rueben-risotto", "Rote-Rüben-Risotto", "🟣", "ital", 35, "H",
  {"reis": 85, "rotebete": 120, "zwiebel": .5, "bruehe": 2, "olivenoel": 1.5, "zitrone": .2, "nuesse": 10, "thymian": .25},
  ["{=350 ml} Wasser mit {bruehe} aufkochen und heiß halten.",
   "{rotebete} fein würfeln (ein Viertel pürieren oder fein reiben – das färbt das Risotto).",
   "Fein gehackte {zwiebel} in {olivenoel} anschwitzen, {reis} glasig rühren.",
   "Nach und nach die heiße Brühe dazugießen und unter Rühren ca. 18 Minuten garen. Nach 10 Minuten die Rote Rübe und {thymian} dazugeben.",
   "Mit Abrieb von {zitrone}, Salz und Pfeffer abschmecken und mit gehackten {nuesse} bestreuen."])

R("gemuese-couscous", "Warmer Gemüse-Couscous mit Kichererbsen", "🍲", "orient schnell", 25, "WH",
  {"couscous": 70, "kichererbsen": 100, "zucchini": .4, "karotten": 60, "rotezwiebel": .3, "kreuzk": .5, "zimt": .1, "olivenoel": 1.5, "zitrone": .25, "kraeuter": .25},
  ["{couscous} mit gleicher Menge kochendem Salzwasser übergießen und 5 Minuten quellen lassen.",
   "{karotten} in dünne Scheiben, {zucchini} in Würfel, {rotezwiebel} in Streifen schneiden.",
   "Gemüse in {olivenoel} 6 Minuten braten, {kreuzk} und {zimt} kurz mitrösten.",
   "Abgespülte {kichererbsen} dazugeben und erwärmen.",
   "Mit Couscous, Saft von {zitrone} und gehackter {kraeuter} mischen."])

R("zucchini-reispfanne", "Zucchini-Tomaten-Reispfanne", "🍅", "medi leicht guenstig", 30, "H",
  {"reis": 75, "zucchini": .5, "tomdose": 120, "zwiebel": .5, "knoblauch": 1, "paprikap": .5, "bruehe": 1, "olivenoel": 1, "basilikum": .2},
  ["{zwiebel}, {knoblauch} und {zucchini} würfeln und in {olivenoel} 5 Minuten anbraten.",
   "{reis} und {paprikap} kurz mitrösten.",
   "{tomdose}, {bruehe} und {=180 ml} Wasser dazugeben, aufkochen und zugedeckt 18 Minuten bei kleiner Hitze garen.",
   "5 Minuten ruhen lassen, auflockern und mit {basilikum} servieren."])

R("kichererbsen-kokos-suppe", "Kichererbsen-Kokos-Suppe mit Spinat", "🥣", "indisch leicht schnell", 25, "H",
  {"kichererbsen": 100, "kokos": 80, "tomdose": 100, "spinat": 60, "zwiebel": .5, "ingwer": 5, "curry": 1, "bruehe": 1, "limette": .25, "oel": .5, "fladenbrot": .2},
  ["{zwiebel} und {ingwer} hacken und in {oel} anschwitzen, {curry} kurz mitrösten.",
   "{tomdose}, {kokos}, {bruehe} und {=300 ml} Wasser dazugeben.",
   "Abgespülte {kichererbsen} dazugeben und 10 Minuten köcheln.",
   "{spinat} einrühren und 3 Minuten ziehen lassen.",
   "Mit Saft von {limette} abschmecken und mit {fladenbrot} servieren."])

R("bratkartoffeln-bohnen", "Bratkartoffeln mit Bohnen & Ajvar", "🥔", "oesterr guenstig", 30, "H",
  {"kartoffeln": 250, "bohnenw": 80, "zwiebel": .5, "ajvar": 40, "paprikap": .5, "oel": 1.5, "kraeuter": .2, "gurke": .3},
  ["{kartoffeln} in der Schale 20 Minuten kochen (oder Reste verwenden), schälen und in Scheiben schneiden.",
   "Erdäpfel in {oel} bei mittlerer bis hoher Hitze ca. 10 Minuten knusprig braten.",
   "{zwiebel} in Streifen und abgespülte {bohnenw} dazugeben und 4 Minuten mitbraten. Mit {paprikap} und Salz würzen.",
   "Mit {ajvar}, gehackter {kraeuter} und {gurke}-Scheiben servieren."])

R("linsen-kokos-dal-spinat", "Grünes Linsen-Dal mit Spinat", "🍛", "indisch leicht guenstig", 30, "H",
  {"linsen": 70, "spinat": 100, "kokos": 60, "zwiebel": .5, "knoblauch": 1, "ingwer": 5, "kreuzk": .5, "curry": .5, "zitrone": .25, "oel": 1, "reis": 60},
  ["{reis} kochen.",
   "{kreuzk} in {oel} 30 Sekunden rösten, gehackte {zwiebel}, {knoblauch} und {ingwer} 4 Minuten mitbraten, {curry} einrühren.",
   "Abgespülte {linsen} und {=300 ml} Wasser dazugeben und 15 Minuten köcheln.",
   "{spinat} und {kokos} einrühren und weitere 5 Minuten köcheln.",
   "Mit Saft von {zitrone} und Salz abschmecken."])

# ---------- vegane Frühstücke ----------
R("erdnuss-oats", "Erdnuss-Overnight-Oats", "🥜", "protein", 5, "",
  {"hafer": 50, "hafermilch": 160, "erdnussb": 15, "banane": .5},
  ["{hafer} mit {hafermilch} und {erdnussb} verrühren.",
   "Über Nacht im Kühlschrank quellen lassen.",
   "Morgens mit {banane}-Scheiben toppen."], type="f")

R("tofu-wrap-frueh", "Tofu-Frühstückswrap", "🌯", "protein", 12, "H",
  {"tortilla": 1, "tofu": 80, "paprika": .25, "spinat": 30, "curry": .25, "oel": .3},
  ["{tofu} zerbröseln, {paprika} würfeln.",
   "Beides in {oel} 4 Minuten braten, {spinat} kurz mitdünsten und mit {curry} und Salz würzen.",
   "In eine erwärmte {tortilla} füllen und einrollen."], type="f")

R("apfel-zimt-oats-vegan", "Apfel-Zimt-Oats mit Walnüssen", "🍏", "leicht", 5, "",
  {"hafer": 50, "hafermilch": 160, "apfel": .5, "zimt": .25, "nuesse": 10},
  ["{apfel} grob reiben und mit {hafer}, {hafermilch} und {zimt} verrühren.",
   "Über Nacht oder mindestens 15 Minuten quellen lassen.",
   "Mit gehackten {nuesse} bestreuen."], type="f")
