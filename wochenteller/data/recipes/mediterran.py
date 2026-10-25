from . import R

# ---------- Mediterran & Orient ----------
R("ofengemuese-feta", "Ofengemüse mit Feta", "🫑", "medi leicht", 40, "BA",
  {"kartoffeln": 200, "zucchini": .5, "paprika": .5, "rotezwiebel": .5, "feta": 75, "olivenoel": 1.5, "oregano": .5, "knoblauch": 1},
  ["Backrohr auf 200 °C Umluft vorheizen (Airfryer: 190 °C).",
   "{kartoffeln} in Spalten, {zucchini} und {paprika} in große Stücke, {rotezwiebel} in Achtel schneiden.",
   "Mit {olivenoel}, {oregano}, angedrücktem {knoblauch} und Salz mischen und auf einem Blech verteilen – nicht zu eng, sonst dünstet es statt zu rösten.",
   "Ca. 25 Minuten rösten, einmal wenden.",
   "{feta} grob darüberbröseln und weitere 5–8 Minuten backen, bis er leicht Farbe nimmt."])

R("griechischer-salat", "Griechischer Salat mit Brot", "🥗", "medi leicht schnell", 10, "",
  {"gurke": .5, "tomaten": 150, "paprika": .25, "feta": 75, "rotezwiebel": .25, "oliven": 25, "olivenoel": 1, "essig": .5, "oregano": .25, "brot": 70},
  ["{gurke} und {tomaten} in grobe Stücke schneiden, {paprika} in Streifen, {rotezwiebel} in feine Ringe.",
   "Gemüse mit {oliven} in eine Schüssel geben, mit Salz, {essig} und {olivenoel} marinieren.",
   "{feta} als Block oder in groben Stücken darauflegen und mit {oregano} bestreuen.",
   "Mit {brot} servieren."], season="5-9")

R("couscous-salat", "Couscous-Salat mit Kichererbsen", "🥗", "orient medi leicht schnell", 15, "WH",
  {"couscous": 70, "kichererbsen": 80, "gurke": .3, "cherry": 80, "feta": 40, "zitrone": .5, "olivenoel": 1.5, "kraeuter": .25, "kreuzk": .25},
  ["{couscous} mit der gleichen Menge kochendem, gesalzenem Wasser übergießen, zudecken und 5 Minuten quellen lassen. Mit einer Gabel auflockern.",
   "{gurke} und {cherry} würfeln, {kichererbsen} abspülen, {kraeuter} hacken.",
   "Saft von {zitrone} mit {olivenoel}, {kreuzk}, Salz und Pfeffer verrühren.",
   "Alles mischen und {feta} darüberbröseln. Schmeckt auch am nächsten Tag als Mittagessen."])

R("blech-huhn-gemuese", "Huhn & Gemüse vom Blech", "🍗", "medi protein leicht familie", 40, "BA",
  {"huhn": 140, "zucchini": .5, "paprika": .5, "kartoffeln": 150, "olivenoel": 1, "paprikap": 1, "knoblauch": 1, "zitrone": .25, "oregano": .25},
  ["Backrohr auf 200 °C Umluft vorheizen.",
   "{kartoffeln} in kleine Spalten schneiden (sie brauchen am längsten), mit etwas Öl und Salz aufs Blech geben und 10 Minuten vorbacken.",
   "{huhn}, {zucchini} und {paprika} in mundgerechte Stücke schneiden.",
   "Mit {olivenoel}, gepresstem {knoblauch}, {paprikap}, {oregano} und Salz mischen.",
   "Zu den Erdäpfeln aufs Blech geben und weitere ca. 20 Minuten garen, bis das Huhn durch ist (Airfryer: insgesamt 20 Minuten bei 190 °C, zwischendurch schütteln).",
   "Mit Saft von {zitrone} beträufeln."])

R("rote-rueben-salat", "Rote-Rüben-Salat mit Feta & Walnüssen", "🥗", "medi leicht schnell", 10, "",
  {"rotebete": 150, "feta": 50, "nuesse": 15, "rucola": 30, "olivenoel": 1, "essig": .5, "honig": 5, "brot": 60},
  ["{rotebete} in Spalten schneiden (Handschuhe schützen vor roten Fingern).",
   "{olivenoel}, {essig}, {honig}, Salz und Pfeffer verrühren.",
   "{rucola} auf Tellern verteilen, Rote Rüben darauf anrichten und mit Dressing beträufeln.",
   "{feta} und grob gehackte {nuesse} darüberstreuen. Mit {brot} servieren."])

R("thunfisch-bohnen-salat", "Thunfisch-Bohnen-Salat", "🥗", "medi leicht protein schnell", 15, "H",
  {"thunfisch": 75, "bohnenw": 80, "eier": 1, "tomaten": 100, "gurke": .3, "rotezwiebel": .25, "olivenoel": 1, "essig": .5, "brot": 50},
  ["{eier} 9 Minuten hart kochen, abschrecken und schälen.",
   "{tomaten} und {gurke} würfeln, {rotezwiebel} fein schneiden.",
   "Mit abgespülten {bohnenw} und abgetropftem {thunfisch} mischen.",
   "Mit {olivenoel}, {essig}, Salz und Pfeffer marinieren.",
   "Ei vierteln, darauflegen und mit {brot} servieren."])

R("halloumi-bulgur", "Halloumi mit Ofengemüse & Bulgur", "🧀", "medi orient", 35, "BA H",
  {"halloumi": 90, "zucchini": .4, "paprika": .5, "rotezwiebel": .4, "bulgur": 60, "olivenoel": 1.5, "zitrone": .25, "kraeuter": .25, "kreuzk": .25},
  ["Backrohr auf 200 °C vorheizen. {zucchini}, {paprika} und {rotezwiebel} in Stücke schneiden, mit der Hälfte des {olivenoel}, {kreuzk} und Salz mischen und 20 Minuten rösten.",
   "{bulgur} mit der doppelten Menge gesalzenem Wasser aufkochen und zugedeckt 10 Minuten quellen lassen.",
   "{halloumi} in 1 cm dicke Scheiben schneiden und in einer Pfanne ohne Fett je Seite 2 Minuten goldbraun braten.",
   "Bulgur mit Saft von {zitrone}, restlichem Öl und gehackter {kraeuter} mischen.",
   "Mit Gemüse und Halloumi anrichten."])

R("gyros-pfanne", "Gyros-Pfanne mit Tzatziki & Reis", "🥙", "medi protein familie", 30, "H",
  {"schnitzel": 140, "rotezwiebel": .5, "paprikap": 1, "oregano": .5, "knoblauch": 1.5, "oel": 1, "joghurt": 90, "gurke": .25, "reis": 70, "kreuzk": .25},
  ["{reis} mit der doppelten Menge Salzwasser aufkochen und zugedeckt 15 Minuten quellen lassen.",
   "Für das Tzatziki {gurke} grob raspeln, salzen, 5 Minuten ziehen lassen und kräftig ausdrücken. Mit {joghurt}, der Hälfte vom gepressten {knoblauch} und Salz verrühren.",
   "{schnitzel} in dünne Streifen schneiden und mit {paprikap}, {oregano}, {kreuzk}, restlichem Knoblauch, Salz und 1 TL Öl marinieren.",
   "Restliches {oel} sehr heiß werden lassen und das Fleisch portionsweise 3–4 Minuten scharf anbraten.",
   "{rotezwiebel} in Ringe schneiden, kurz mitbraten.",
   "Mit Reis und Tzatziki servieren."])

R("souvlaki-hendl", "Souvlaki-Hendl mit Zitronenerdäpfeln", "🍢", "medi protein", 45, "BA H",
  {"huhn": 150, "zitrone": .5, "oregano": .5, "knoblauch": 1, "olivenoel": 1.5, "kartoffeln": 200, "joghurt": 60, "gurke": .2, "tomaten": 80},
  ["{huhn} in große Würfel schneiden und mit Saft von der Hälfte der {zitrone}, {oregano}, gepresstem {knoblauch}, der Hälfte des {olivenoel} und Salz mindestens 15 Minuten marinieren.",
   "Backrohr auf 220 °C vorheizen. {kartoffeln} in Spalten schneiden, mit restlichem Öl, restlichem Zitronensaft, Oregano und Salz mischen und ca. 35 Minuten knusprig backen.",
   "Fleisch auf Spieße stecken (oder lose lassen) und in einer heißen Pfanne rundum 8 Minuten braten.",
   "{joghurt} mit geraspelter {gurke} und Salz verrühren.",
   "Mit Erdäpfeln, Joghurt-Dip und {tomaten} servieren."])

R("moussaka-pfanne", "Moussaka-Auflauf", "🍆", "medi familie", 60, "B H",
  {"melanzani": .6, "faschiert": 110, "tomdose": 150, "zwiebel": .5, "knoblauch": 1, "zimt": .1, "oregano": .25, "milch": 100, "mehl": 8, "butter": 8, "reibkaese": 25, "olivenoel": 1},
  ["Backrohr auf 200 °C vorheizen. {melanzani} in 1 cm Scheiben schneiden, mit {olivenoel} bepinseln, salzen und auf einem Blech 15 Minuten vorbacken.",
   "{zwiebel} und {knoblauch} hacken und anschwitzen, {faschiert} krümelig anbraten. {tomdose}, {zimt} und {oregano} dazugeben und 10 Minuten köcheln.",
   "Für die Béchamel {butter} schmelzen, {mehl} einrühren, mit {milch} aufgießen und unter Rühren 3 Minuten dicklich köcheln. Mit Salz und Muskat würzen.",
   "Melanzani und Fleischsauce in eine Form schichten, Béchamel darüber verteilen und mit {reibkaese} bestreuen.",
   "Hitze auf 180 °C reduzieren und ca. 25 Minuten goldbraun backen. 10 Minuten rasten lassen."])

R("spanische-tortilla", "Spanische Tortilla mit Salat", "🥔", "medi guenstig", 35, "H",
  {"kartoffeln": 220, "eier": 2.5, "zwiebel": .5, "olivenoel": 2, "salat": .25, "tomaten": 60},
  ["{kartoffeln} schälen und in dünne Scheiben schneiden, {zwiebel} in feine Streifen.",
   "{olivenoel} in einer beschichteten Pfanne erhitzen und Erdäpfel mit Zwiebel bei mittlerer Hitze zugedeckt ca. 15 Minuten weich garen (nicht braun braten). Salzen.",
   "{eier} kräftig verquirlen und salzen. Die warmen Erdäpfel untermischen und 5 Minuten ziehen lassen.",
   "Die Masse zurück in die geölte Pfanne geben und bei kleiner Hitze 6 Minuten stocken lassen.",
   "Mithilfe eines Tellers wenden und weitere 3 Minuten braten.",
   "Lauwarm in Stücken mit {salat} und {tomaten} servieren."])

R("paella-huhn", "Paella mit Huhn & Erbsen", "🥘", "medi protein familie", 45, "H",
  {"reis": 80, "huhn": 110, "paprika": .5, "erbsen": 50, "zwiebel": .5, "knoblauch": 1, "tomdose": 60, "paprikap": 1, "bruehe": 1, "olivenoel": 1, "zitrone": .25},
  ["{huhn} würfeln, salzen und in {olivenoel} in einer großen Pfanne rundum 5 Minuten anbraten. Herausnehmen.",
   "{zwiebel}, {knoblauch} und {paprika} würfeln und im Bratfett 4 Minuten anbraten.",
   "{paprikap} und {reis} kurz mitrösten, {tomdose} einrühren.",
   "Mit {=250 ml} heißem Wasser und {bruehe} aufgießen, Huhn verteilen und bei mittlerer Hitze ohne Umrühren ca. 18 Minuten garen.",
   "Nach 12 Minuten {erbsen} darüberstreuen. Am Ende darf der Boden leicht ansetzen (das ist die begehrte Kruste).",
   "Mit Zitronenspalten von {zitrone} servieren."])

R("gefuellte-zucchini", "Gefüllte Zucchini mit Bulgur & Feta", "🥒", "medi orient leicht", 45, "B H",
  {"zucchini": 1, "bulgur": 40, "feta": 50, "tomdose": 100, "zwiebel": .25, "knoblauch": .5, "kraeuter": .25, "olivenoel": 1, "kreuzk": .25},
  ["Backrohr auf 200 °C vorheizen. {zucchini} längs halbieren und mit einem Löffel aushöhlen. Fruchtfleisch hacken.",
   "{bulgur} mit der doppelten Menge Salzwasser 10 Minuten quellen lassen.",
   "{zwiebel}, {knoblauch} und Zucchini-Fruchtfleisch in {olivenoel} 4 Minuten braten, mit {kreuzk} würzen.",
   "Mit Bulgur, der Hälfte des zerbröselten {feta} und gehackter {kraeuter} mischen.",
   "{tomdose} gesalzen in eine Form geben, gefüllte Zucchini daraufsetzen und mit restlichem Feta bestreuen.",
   "Ca. 25 Minuten backen, bis die Zucchini weich sind."], season="6-10")

R("fisch-tomate-oliven", "Fisch in Tomatensauce mit Oliven", "🐟", "medi protein leicht", 30, "H",
  {"weissfisch": 150, "tomdose": 150, "oliven": 25, "zwiebel": .5, "knoblauch": 1, "olivenoel": 1, "kartoffeln": 200, "kraeuter": .25, "thymian": .25},
  ["{kartoffeln} schälen und in Salzwasser 20 Minuten kochen.",
   "{zwiebel} und {knoblauch} hacken und in {olivenoel} 3 Minuten anschwitzen.",
   "{tomdose}, {thymian} und halbierte {oliven} dazugeben und 8 Minuten köcheln.",
   "{weissfisch} (aufgetaut) salzen, in die Sauce legen und zugedeckt bei kleiner Hitze 8–10 Minuten gar ziehen lassen, bis er sich leicht zerteilen lässt.",
   "Mit gehackter {kraeuter} bestreuen und mit den Erdäpfeln servieren."])

R("linsensalat-feta", "Lauwarmer Linsensalat mit Feta", "🥗", "medi leicht protein", 30, "H",
  {"linsenbraun": 70, "karotten": 60, "rotezwiebel": .25, "feta": 50, "rucola": 30, "essig": 1, "olivenoel": 1.5, "senf": 5, "thymian": .25},
  ["{linsenbraun} abspülen und in ungesalzenem Wasser mit {thymian} ca. 20 Minuten bissfest kochen. Abseihen.",
   "{karotten} in kleine Würfel schneiden und die letzten 5 Minuten mitkochen.",
   "{essig}, {senf}, {olivenoel}, Salz und Pfeffer verrühren und mit den warmen Linsen mischen.",
   "Fein gehackte {rotezwiebel} untermischen und 10 Minuten ziehen lassen.",
   "Auf {rucola} anrichten und {feta} darüberbröseln."])

R("ofenlachs-fenchel", "Ofenlachs mit Fenchel & Erdäpfeln", "🐟", "medi protein leicht", 40, "BA",
  {"lachs": 125, "fenchel": .5, "kartoffeln": 180, "zitrone": .3, "olivenoel": 1, "dill": .25},
  ["Backrohr auf 200 °C vorheizen.",
   "{kartoffeln} in Spalten, {fenchel} in dünne Spalten schneiden. Mit {olivenoel} und Salz mischen und 20 Minuten rösten.",
   "{lachs} (aufgetaut) salzen, auf das Gemüse legen und mit Zitronenscheiben von {zitrone} belegen.",
   "Weitere 12–15 Minuten garen, bis der Lachs innen gerade nicht mehr glasig ist.",
   "Mit gehackter {dill} bestreuen."])

R("ratatouille", "Ratatouille mit Reis", "🍅", "medi leicht", 45, "H",
  {"zucchini": .5, "melanzani": .4, "paprika": .5, "tomdose": 150, "zwiebel": .5, "knoblauch": 1, "thymian": .5, "olivenoel": 1.5, "reis": 70, "basilikum": .2},
  ["{reis} mit der doppelten Menge Salzwasser aufkochen und 15 Minuten zugedeckt quellen lassen.",
   "{melanzani}, {zucchini} und {paprika} in 2 cm Würfel schneiden.",
   "{olivenoel} erhitzen und die Melanzani 5 Minuten anbraten, dann Paprika und Zucchini weitere 5 Minuten mitbraten.",
   "Gehackte {zwiebel} und {knoblauch} dazugeben, kurz mitbraten, dann {tomdose} und {thymian} einrühren.",
   "Zugedeckt ca. 20 Minuten schmoren, bis das Gemüse weich ist. Salzen und pfeffern.",
   "Mit Reis und {basilikum} servieren."])

R("quinoa-halloumi-bowl", "Quinoa-Bowl mit Halloumi", "🥗", "medi leicht protein", 25, "H",
  {"quinoa": 60, "halloumi": 70, "gurke": .3, "cherry": 80, "avocado": .5, "zitrone": .25, "olivenoel": 1, "rucola": 25},
  ["{quinoa} in einem Sieb heiß abspülen und mit der doppelten Menge Salzwasser 15 Minuten köcheln, dann 5 Minuten ziehen lassen.",
   "{gurke} und {cherry} würfeln, {avocado} in Spalten schneiden.",
   "{halloumi} in Scheiben schneiden und ohne Fett je Seite 2 Minuten goldbraun braten.",
   "Saft von {zitrone} mit {olivenoel}, Salz und Pfeffer verrühren und mit der Quinoa mischen.",
   "Alles mit {rucola} in Schüsseln anrichten."])

R("ofenkuerbis-feta", "Ofenkürbis mit Feta & Couscous", "🎃", "medi orient leicht", 40, "BA WH",
  {"kuerbis": .35, "feta": 50, "couscous": 60, "rotezwiebel": .3, "olivenoel": 1.5, "honig": 5, "zimt": .1, "kreuzk": .25, "kraeuter": .25},
  ["Backrohr auf 200 °C vorheizen.",
   "{kuerbis} in Spalten schneiden, {rotezwiebel} in Achtel. Mit {olivenoel}, {kreuzk}, {zimt} und Salz mischen und ca. 25 Minuten rösten.",
   "Die letzten 5 Minuten mit {honig} beträufeln und {feta} darüberbröseln.",
   "{couscous} mit gleicher Menge kochendem Salzwasser übergießen und 5 Minuten quellen lassen.",
   "Couscous mit gehackter {kraeuter} auflockern und mit dem Kürbis anrichten."], season="9-12")

R("shakshuka", "Shakshuka mit Brot", "🍳", "orient leicht", 25, "H",
  {"eier": 2, "tomdose": 200, "paprika": .5, "zwiebel": .5, "knoblauch": 1, "kreuzk": .5, "paprikap": .5, "brot": 80, "olivenoel": 1, "kraeuter": .25, "feta": 20},
  ["{zwiebel}, {paprika} und {knoblauch} würfeln und in {olivenoel} bei mittlerer Hitze 6 Minuten weich dünsten.",
   "{kreuzk} und {paprikap} 30 Sekunden mitrösten.",
   "{tomdose} dazugeben, salzen und ca. 10 Minuten einkochen, bis die Sauce dicklich ist.",
   "Mit einem Löffel Mulden formen und die {eier} hineinschlagen.",
   "Zugedeckt bei kleiner Hitze ca. 6 Minuten stocken lassen – das Eiweiß soll fest, das Eigelb noch weich sein.",
   "Mit {feta}, gehackter {kraeuter} und {brot} servieren."])

R("rote-linsen-suppe", "Rote-Linsen-Suppe", "🥣", "orient leicht guenstig", 30, "H",
  {"linsen": 70, "karotten": 80, "zwiebel": .5, "kokos": 50, "tommark": 10, "kreuzk": .5, "bruehe": 1, "zitrone": .25, "oel": .5},
  ["{zwiebel} und {karotten} würfeln und in {oel} 4 Minuten anschwitzen.",
   "{tommark} und {kreuzk} 1 Minute mitrösten.",
   "{linsen} abspülen, mit {bruehe} und {=350 ml} Wasser dazugeben und ca. 20 Minuten köcheln, bis die Linsen zerfallen.",
   "{kokos} einrühren und nach Wunsch pürieren.",
   "Mit Saft von {zitrone}, Salz und Pfeffer abschmecken."])

R("falafel-wraps", "Falafel-Wraps", "🧆", "orient", 35, "AB X",
  {"kichererbsen": 120, "mehl": 15, "zwiebel": .25, "knoblauch": 1, "kreuzk": .5, "kraeuter": .25, "oel": 1, "tortilla": 2, "joghurt": 50, "salat": .2, "tomaten": 60},
  ["{kichererbsen} abtropfen lassen und sehr gut trocken tupfen.",
   "Mit {zwiebel}, {knoblauch}, {kraeuter}, {kreuzk}, {mehl} und Salz im Mixer grob pürieren – es sollen noch kleine Stücke bleiben.",
   "Walnussgroße Bällchen formen, leicht flach drücken und mit {oel} bepinseln.",
   "Im Airfryer 12 Minuten bei 200 °C backen, nach der Hälfte wenden (Backrohr: 20 Minuten bei 200 °C).",
   "{tortilla} kurz erwärmen, mit {joghurt} bestreichen und mit {salat}, {tomaten} und Falafel füllen."])

R("suesskartoffel-bowl", "Süßkartoffel-Bowl mit Kichererbsen", "🥙", "orient leicht", 35, "BA HR",
  {"suesskart": 200, "kichererbsen": 100, "reis": 60, "avocado": .5, "salat": .2, "joghurt": 40, "oel": 1, "kreuzk": .5, "zitrone": .2},
  ["Backrohr auf 200 °C vorheizen.",
   "{suesskart} in 2 cm Würfel schneiden, mit abgetropften {kichererbsen}, {oel}, {kreuzk} und Salz mischen.",
   "Auf einem Blech ca. 25 Minuten rösten, bis die Kichererbsen knusprig sind.",
   "{reis} kochen.",
   "{joghurt} mit Saft von {zitrone} und Salz verrühren.",
   "Reis, Süßkartoffeln, Kichererbsen, {salat} und {avocado} in Schüsseln anrichten und mit dem Joghurt beträufeln."])

R("bulgur-pfanne", "Bulgur-Gemüse-Pfanne mit Feta", "🥘", "orient schnell", 25, "H",
  {"bulgur": 70, "zucchini": .5, "paprika": .5, "tomdose": 100, "feta": 50, "zwiebel": .5, "olivenoel": 1, "kreuzk": .25, "kraeuter": .2},
  ["{zwiebel}, {zucchini} und {paprika} würfeln und in {olivenoel} 5 Minuten anbraten.",
   "{bulgur}, {tomdose}, {kreuzk} und {=150 ml} Wasser dazugeben, salzen.",
   "Zugedeckt bei kleiner Hitze 12 Minuten quellen lassen.",
   "Mit einer Gabel auflockern, {feta} darüberbröseln und mit {kraeuter} bestreuen."])

R("ofenkarfiol-joghurt", "Ofenkarfiol mit Joghurt & Couscous", "🥦", "orient leicht", 35, "BA WH",
  {"karfiol": .4, "couscous": 60, "joghurt": 80, "kreuzk": .5, "olivenoel": 1.5, "zitrone": .25, "knoblauch": .5, "nuesse": 10},
  ["Backrohr auf 220 °C vorheizen.",
   "{karfiol} in Röschen teilen, mit {olivenoel}, {kreuzk} und Salz mischen und ca. 25 Minuten rösten, bis die Ränder dunkelbraun sind.",
   "{couscous} mit gleicher Menge kochendem Salzwasser übergießen und 5 Minuten quellen lassen.",
   "{joghurt} mit geriebenem {knoblauch}, Saft von {zitrone} und Salz verrühren.",
   "Couscous anrichten, Karfiol darauf verteilen, mit Joghurt beträufeln und mit gehackten {nuesse} bestreuen."])

R("huhn-couscous-tajine", "Hühner-Couscous mit Gemüse", "🍲", "orient protein", 50, "H",
  {"huhnkeule": 250, "couscous": 60, "karotten": 70, "zucchini": .3, "kichererbsen": 60, "zwiebel": .5, "zimt": .25, "kreuzk": .5, "paprikap": .5, "bruehe": 1, "oel": 1, "kraeuter": .25},
  ["{huhnkeule} salzen und in {oel} in einem Topf rundum goldbraun anbraten. Herausnehmen.",
   "{zwiebel} würfeln und im Bratfett anschwitzen. {zimt}, {kreuzk} und {paprikap} kurz mitrösten.",
   "{karotten} in dicke Scheiben schneiden, mit {bruehe} und {=250 ml} Wasser dazugeben. Keulen hineinlegen und zugedeckt 25 Minuten schmoren.",
   "{zucchini} in Stücke und abgespülte {kichererbsen} dazugeben und weitere 10 Minuten garen.",
   "{couscous} mit gleicher Menge kochendem Salzwasser übergießen und 5 Minuten quellen lassen.",
   "Couscous mit Huhn, Gemüse und Sauce anrichten und mit {kraeuter} bestreuen."])

R("kofta-bulgur", "Kofta-Laibchen mit Joghurt & Bulgur", "🧆", "orient protein", 35, "H",
  {"rindfasch": 130, "zwiebel": .3, "kraeuter": .25, "kreuzk": .5, "zimt": .1, "knoblauch": .5, "bulgur": 60, "joghurt": 70, "gurke": .25, "oel": 1, "tomaten": 80},
  ["{bulgur} mit der doppelten Menge Salzwasser aufkochen und zugedeckt 10 Minuten quellen lassen.",
   "{rindfasch} mit fein geriebener {zwiebel}, gehackter {kraeuter}, {kreuzk}, {zimt}, gepresstem {knoblauch}, Salz und Pfeffer gut verkneten.",
   "Längliche, fingerdicke Laibchen formen.",
   "In {oel} bei mittlerer bis hoher Hitze rundum 6–8 Minuten braten.",
   "{joghurt} mit gewürfelter {gurke} und Salz verrühren.",
   "Mit Bulgur, Joghurt und {tomaten} servieren."])

R("mujaddara", "Mujaddara – Linsenreis mit Röstzwiebeln", "🍚", "orient guenstig", 45, "H",
  {"linsenbraun": 50, "reis": 50, "zwiebel": 1.5, "oel": 2, "kreuzk": .5, "joghurt": 70, "gurke": .3, "zitrone": .2},
  ["{linsenbraun} abspülen und in {=400 ml} Wasser 15 Minuten vorkochen.",
   "{zwiebel} in feine Ringe schneiden und in {oel} bei mittlerer Hitze ca. 20 Minuten unter Rühren dunkelgoldbraun und knusprig rösten. Die Hälfte herausnehmen.",
   "{reis} und {kreuzk} zu den restlichen Zwiebeln in den Topf geben und kurz rösten.",
   "Linsen samt Kochwasser dazugeben, salzen und zugedeckt ca. 15 Minuten garen, bis alles Wasser aufgesogen ist.",
   "{gurke} würfeln und mit {joghurt}, Saft von {zitrone} und Salz mischen.",
   "Linsenreis mit den knusprigen Zwiebeln bestreuen und mit dem Gurkenjoghurt servieren."])

R("gefuellte-melanzani", "Gefüllte Melanzani mit Tomaten & Feta", "🍆", "orient medi", 50, "B H",
  {"melanzani": .8, "tomdose": 150, "zwiebel": .5, "knoblauch": 1, "feta": 50, "kraeuter": .25, "olivenoel": 2, "zimt": .1, "brot": 50},
  ["Backrohr auf 200 °C vorheizen. {melanzani} längs halbieren, Fruchtfleisch rautenförmig einschneiden, mit der Hälfte des {olivenoel} bepinseln, salzen und 20 Minuten mit der Schnittfläche nach oben backen.",
   "{zwiebel} und {knoblauch} hacken und im restlichen Öl 5 Minuten weich dünsten.",
   "{tomdose} und {zimt} dazugeben und 10 Minuten einkochen. Salzen.",
   "Das weiche Fruchtfleisch der Melanzani mit einem Löffel etwas eindrücken und die Tomatenmasse daraufgeben.",
   "{feta} darüberbröseln und weitere 15 Minuten backen.",
   "Mit {kraeuter} bestreuen und mit {brot} servieren."])

R("hummus-bowl", "Hummus-Bowl mit Ofengemüse", "🥙", "orient leicht", 35, "X BA",
  {"kichererbsen": 120, "zitrone": .3, "knoblauch": .5, "olivenoel": 2, "kreuzk": .25, "karotten": 80, "paprika": .5, "rotezwiebel": .3, "fladenbrot": .25, "sesam": 5},
  ["Backrohr auf 200 °C vorheizen. {karotten} in Stifte, {paprika} in Streifen, {rotezwiebel} in Spalten schneiden, mit der Hälfte des {olivenoel} und Salz mischen und 20 Minuten rösten.",
   "{kichererbsen} abtropfen lassen (etwas Flüssigkeit aufheben).",
   "Mit Saft von {zitrone}, {knoblauch}, {kreuzk}, restlichem Olivenöl, Salz und 2–3 EL Kichererbsenwasser im Mixer sehr cremig pürieren.",
   "{sesam} in einer trockenen Pfanne goldbraun rösten.",
   "Hummus in Schüsseln streichen, Gemüse darauf verteilen, mit Sesam bestreuen und mit warmem {fladenbrot} servieren."])

R("spinat-boerek", "Spinat-Feta-Börek", "🥧", "orient", 45, "B H",
  {"blaetterteig": .5, "spinat": 120, "feta": 60, "eier": .5, "zwiebel": .25, "knoblauch": .5, "joghurt": 60, "salat": .25},
  ["Backrohr auf 200 °C vorheizen.",
   "{zwiebel} und {knoblauch} fein hacken und anschwitzen. Aufgetauten, gut ausgedrückten {spinat} dazugeben und 3 Minuten dünsten.",
   "Etwas abkühlen lassen und mit zerbröseltem {feta}, der Hälfte vom verquirlten {eier}, Pfeffer und wenig Salz mischen.",
   "{blaetterteig} ausrollen, Füllung in einem Streifen der Länge nach daraufgeben, einrollen und zur Schnecke legen.",
   "Mit restlichem Ei bestreichen und ca. 25–30 Minuten goldbraun backen.",
   "Mit {joghurt} und {salat} servieren."])
