from . import R

F = "f"

R("overnight-oats-beeren", "Overnight Oats mit Beeren", "🫐", "leicht", 5, "",
  {"hafer": 50, "joghurt": 100, "milch": 50, "beeren": 60, "honig": 5},
  ["Am Vorabend {hafer} mit {joghurt}, {milch} und {honig} in einem Glas verrühren.",
   "Zugedeckt über Nacht in den Kühlschrank stellen.",
   "Morgens mit {beeren} (sie tauen über Nacht mit auf, wenn du sie gleich darauf gibst) toppen."], type=F)

R("vegane-oats", "Vegane Overnight Oats", "🫐", "leicht", 5, "",
  {"hafer": 50, "hafermilch": 180, "beeren": 60, "banane": .5},
  ["{hafer} mit {hafermilch} verrühren und über Nacht im Kühlschrank quellen lassen.",
   "Morgens {banane} in Scheiben schneiden.",
   "Mit Banane und {beeren} toppen."], type=F)

R("ruehrei-brot", "Rührei mit Schnittlauch & Brot", "🍳", "protein", 10, "H",
  {"eier": 2, "brot": 70, "butter": 10, "schnittlauch": .2},
  ["{eier} mit einer Prise Salz verquirlen.",
   "{butter} bei mittlerer Hitze schmelzen, Eier hineingeben und mit einem Pfannenwender langsam vom Rand zur Mitte schieben.",
   "Vom Herd nehmen, solange das Rührei noch leicht glänzt – es gart nach.",
   "Mit {schnittlauch} bestreuen und mit {brot} servieren."], type=F)

R("porridge-banane", "Porridge mit Banane", "🥣", "", 10, "HM",
  {"hafer": 50, "milch": 200, "banane": 1, "zimt": .25},
  ["{hafer} mit {milch} und einer Prise Salz aufkochen (oder 2 Minuten in der Mikrowelle, zwischendurch umrühren).",
   "Unter Rühren 3 Minuten cremig quellen lassen.",
   "{banane} in Scheiben darauf verteilen und mit {zimt} bestreuen."], type=F)

R("apfel-porridge", "Apfel-Zimt-Porridge", "🍎", "leicht", 10, "HM",
  {"hafer": 50, "milch": 200, "apfel": .5, "zimt": .25, "nuesse": 10},
  ["{apfel} grob raspeln.",
   "{hafer}, {milch}, Apfel, {zimt} und eine Prise Salz aufkochen und unter Rühren 3 Minuten köcheln.",
   "Mit gehackten {nuesse} bestreuen."], type=F)

R("birnen-porridge", "Birnen-Porridge mit Honig", "🍐", "leicht", 10, "HM",
  {"hafer": 50, "milch": 200, "birne": .5, "honig": 5, "zimt": .1},
  ["{birne} in kleine Würfel schneiden.",
   "Mit {hafer}, {milch} und {zimt} aufkochen und 3 Minuten köcheln.",
   "Mit {honig} beträufeln."], type=F)

R("joghurt-apfel-nuss", "Joghurt mit Apfel & Walnüssen", "🍎", "leicht", 5, "",
  {"joghurt": 150, "apfel": 1, "nuesse": 15, "honig": 5},
  ["{apfel} entkernen und würfeln.",
   "{joghurt} in eine Schüssel geben und mit {honig} beträufeln.",
   "Apfel und grob gehackte {nuesse} darüberstreuen."], type=F)

R("avocado-brot", "Avocado-Brot mit Tomate", "🥑", "leicht", 5, "T",
  {"brot": 80, "avocado": .5, "zitrone": .15, "tomaten": 50, "chiliflocken": .05},
  ["{brot} toasten.",
   "{avocado} mit Saft von {zitrone}, Salz und Pfeffer zerdrücken.",
   "Aufs Brot streichen, mit {tomaten}-Scheiben belegen und mit {chiliflocken} bestreuen."], type=F)

R("avocado-ei-toast", "Avocado-Toast mit Ei", "🥑", "protein", 12, "H",
  {"brot": 70, "avocado": .5, "eier": 1, "zitrone": .15},
  ["{eier} 7 Minuten wachsweich kochen, abschrecken und schälen.",
   "{brot} toasten.",
   "{avocado} mit Saft von {zitrone} und Salz zerdrücken, aufstreichen und das halbierte Ei darauflegen. Mit Pfeffer bestreuen."], type=F)

R("hafer-pancakes", "Bananen-Hafer-Pancakes", "🥞", "", 15, "H",
  {"hafer": 50, "banane": 1, "eier": 1, "milch": 50, "oel": .5, "beeren": 40},
  ["{banane} mit einer Gabel zerdrücken und mit {hafer}, {eier} und {milch} verrühren. 5 Minuten quellen lassen.",
   "Eine beschichtete Pfanne mit wenig {oel} auf mittlere Hitze bringen.",
   "Kleine Pancakes (je 2 EL Teig) hineingeben und je Seite ca. 2 Minuten goldbraun braten.",
   "Mit {beeren} servieren."], type=F)

R("erdnuss-smoothie", "Erdnuss-Bananen-Smoothie", "🥤", "protein", 5, "X",
  {"hafermilch": 250, "banane": 1, "hafer": 30, "erdnussb": 15},
  ["Alle Zutaten – {hafermilch}, {banane}, {hafer} und {erdnussb} – in den Mixer geben.",
   "30 Sekunden fein mixen.",
   "Sofort trinken."], type=F)

R("tofu-ruehrei", "Tofu-Rührei mit Brot", "🍳", "protein", 10, "H",
  {"tofu": 100, "brot": 70, "curry": .25, "fzwiebel": .25, "oel": .5},
  ["{tofu} mit einer Gabel grob zerbröseln.",
   "In {oel} 4 Minuten anbraten, mit {curry} (für die Farbe), Salz und Pfeffer würzen.",
   "Mit {fzwiebel} bestreuen und mit {brot} servieren."], type=F)

R("topfen-beeren", "Topfen mit Beeren", "🍓", "protein leicht", 5, "",
  {"topfen": 125, "beeren": 80, "hafer": 20, "honig": 5},
  ["{topfen} mit einem Schuss Wasser und {honig} cremig rühren.",
   "Aufgetaute {beeren} daraufgeben.",
   "Mit {hafer} bestreuen."], type=F)

R("skyr-bowl", "Skyr-Bowl mit Banane", "🥣", "protein leicht", 5, "",
  {"skyr": 200, "banane": .5, "nuesse": 10},
  ["{skyr} in eine Schüssel geben.",
   "{banane} in Scheiben darauf verteilen.",
   "Mit gehackten {nuesse} bestreuen."], type=F)

R("kaesetoast", "Käsetoast mit Tomate", "🥪", "", 5, "TBA",
  {"toast": 60, "kaesesch": 30, "tomaten": 50},
  ["{toast} mit {kaesesch} belegen.",
   "Im Toaster (Toasttasche), Backrohr oder Airfryer toasten, bis der Käse schmilzt.",
   "Mit {tomaten}-Scheiben servieren."], type=F)

R("spiegelei-brot", "Spiegelei auf Vollkornbrot", "🍳", "protein", 10, "H",
  {"eier": 2, "brot": 70, "oel": .5, "tomaten": 50},
  ["{eier} in {oel} bei mittlerer Hitze braten, bis das Eiweiß fest ist, salzen.",
   "{brot} in Scheiben schneiden.",
   "Spiegeleier auf das Brot legen und mit {tomaten} servieren."], type=F)

R("bircher-muesli", "Bircher-Müsli", "🍏", "leicht", 10, "",
  {"hafer": 50, "milch": 150, "apfel": .5, "nuesse": 10, "zitrone": .1},
  ["{hafer} mit {milch} verrühren und mindestens 10 Minuten (oder über Nacht) quellen lassen.",
   "{apfel} grob reiben, mit Saft von {zitrone} mischen und unterrühren.",
   "Mit gehackten {nuesse} bestreuen."], type=F)

R("beeren-smoothie", "Beeren-Smoothie", "🥤", "leicht", 5, "X",
  {"joghurt": 150, "beeren": 100, "banane": .5},
  ["{joghurt}, {beeren} und {banane} mit einem Schuss Wasser in den Mixer geben.",
   "Fein mixen.",
   "Sofort trinken."], type=F)

R("smoothie-bowl", "Smoothie-Bowl", "🍓", "leicht", 8, "X",
  {"beeren": 120, "banane": 1, "joghurt": 80, "hafer": 20, "nuesse": 5},
  ["{beeren} (gefroren) mit der Hälfte der {banane} und {joghurt} im Mixer dickcremig mixen.",
   "In eine Schüssel füllen.",
   "Mit Scheiben der restlichen Banane, {hafer} und gehackten {nuesse} toppen."], type=F)

R("semmel-ei", "Semmel mit Ei & Schnittlauch", "🥚", "protein", 12, "H",
  {"semmeln": 1, "eier": 1, "butter": 5, "schnittlauch": .15, "tomaten": 40},
  ["{eier} 9 Minuten hart kochen, abschrecken, schälen und in Scheiben schneiden.",
   "{semmeln} aufschneiden und mit {butter} bestreichen.",
   "Mit Ei und {tomaten} belegen, salzen und mit {schnittlauch} bestreuen."], type=F)

R("marmeladesemmel", "Butter-Marmelade-Semmel", "🥐", "", 3, "",
  {"semmeln": 1, "butter": 10, "marmelade": 25, "milch": 150},
  ["{semmeln} aufschneiden.",
   "Mit {butter} und {marmelade} bestreichen.",
   "Dazu ein Glas {milch} oder Kaffee."], type=F)

R("frischkaese-gurke", "Frischkäse-Brot mit Gurke", "🥒", "leicht", 5, "",
  {"brot": 70, "frischkaese": 30, "gurke": .2, "schnittlauch": .1},
  ["{brot} mit {frischkaese} bestreichen.",
   "{gurke} in dünne Scheiben schneiden und darauflegen.",
   "Salzen, pfeffern und mit {schnittlauch} bestreuen."], type=F)

R("raeucherlachs-brot", "Räucherlachs-Brot", "🐟", "protein", 5, "",
  {"brot": 70, "raeucherlachs": 40, "frischkaese": 25, "dill": .1, "zitrone": .1},
  ["{brot} mit {frischkaese} bestreichen.",
   "Mit {raeucherlachs} belegen.",
   "Mit {dill} und ein paar Tropfen von {zitrone} vollenden."], type=F)

R("liptauer-brot", "Topfenaufstrich auf Brot", "🌶️", "protein leicht", 8, "",
  {"topfen": 70, "brot": 70, "paprikap": .25, "schnittlauch": .15, "zwiebel": .1, "gurke": .15},
  ["{topfen} mit {paprikap}, fein gehackter {zwiebel}, Salz und Pfeffer cremig verrühren.",
   "{brot} damit bestreichen.",
   "Mit {schnittlauch} bestreuen und {gurke}-Scheiben dazu reichen."], type=F)

R("erdnuss-bananen-toast", "Erdnussbutter-Bananen-Toast", "🍌", "protein", 5, "T",
  {"toast": 60, "erdnussb": 20, "banane": .5},
  ["{toast} toasten.",
   "Mit {erdnussb} bestreichen.",
   "{banane} in Scheiben darauflegen."], type=F)

R("french-toast", "French Toast mit Beeren", "🍞", "", 15, "H",
  {"toast": 60, "eier": 1, "milch": 50, "zimt": .25, "butter": 8, "beeren": 60, "honig": 5},
  ["{eier} mit {milch}, {zimt} und einer Prise Salz verquirlen.",
   "{toast} darin von beiden Seiten kurz einweichen.",
   "In {butter} bei mittlerer Hitze je Seite 2 Minuten goldbraun braten.",
   "Mit {beeren} und {honig} servieren."], type=F)

R("schinken-kaese-omelett", "Omelett mit Schinken & Käse", "🍳", "protein", 10, "H",
  {"eier": 2, "schinken": 30, "reibkaese": 20, "butter": 5, "schnittlauch": .1},
  ["{eier} mit Salz und Pfeffer verquirlen.",
   "{butter} in einer Pfanne schmelzen, Eier eingießen und bei mittlerer Hitze stocken lassen.",
   "Gewürfelten {schinken} und {reibkaese} auf eine Hälfte streuen, zuklappen und 1 Minute ziehen lassen.",
   "Mit {schnittlauch} bestreuen."], type=F)

R("joghurt-orange", "Joghurt mit Orange & Haferflocken", "🍊", "leicht", 5, "",
  {"joghurt": 150, "orange": 1, "hafer": 25, "honig": 5},
  ["{orange} schälen und in Stücke schneiden.",
   "{hafer} in einer trockenen Pfanne kurz goldbraun rösten (optional).",
   "{joghurt} mit Orange, Haferflocken und {honig} anrichten."], type=F, season="11-4")

R("gemuese-wrap-frueh", "Frühstückswrap mit Rührei", "🌯", "protein", 12, "H",
  {"tortilla": 1, "eier": 2, "paprika": .25, "reibkaese": 15, "oel": .3},
  ["{paprika} fein würfeln und in {oel} 2 Minuten anbraten.",
   "{eier} verquirlen, salzen, dazugeben und zu Rührei stocken lassen.",
   "{tortilla} erwärmen, mit Rührei und {reibkaese} füllen und einrollen."], type=F)
