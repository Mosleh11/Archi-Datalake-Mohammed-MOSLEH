"""Assemble UC06_traitements_PySpark.pdf a partir de sources_md/ et des resultats JSON/CSV (Markdown -> HTML -> Edge via Selenium)"""
import base64, csv, json, os, statistics, markdown

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(racine, "sources_md")
P = os.path.join(racine, "preuves")


def lire(nom):
    return open(os.path.join(src, nom), encoding="utf-8").read()


def charger(chemin):
    return json.load(open(os.path.join(P, chemin), encoding="utf-8"))


def tableau(entetes, lignes):
    out = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for l in lignes:
        out.append("| " + " | ".join(str(x).replace("|", "/") for x in l) + " |")
    return "\n".join(out)


def milliers(n):
    return f"{n:,}".replace(",", " ")


def csv_gold(nom):
    return list(csv.DictReader(open(os.path.join(P, "silver_gold", f"gold_{nom}.csv"), encoding="utf-8")))


# ---- tableaux generes depuis les resultats
stats = charger("transformations/nettoyage_stats.json")
lignes = []
for t, v in stats.items():
    autres = ", ".join(f"{k} = {x}" for k, x in v.items() if k not in ("lignes_brutes", "lignes_silver", "lignes_rejetees", "echecs_conversion"))
    lignes.append([t, milliers(v["lignes_brutes"]), milliers(v["lignes_silver"]), v["lignes_rejetees"], sum(v["echecs_conversion"].values()), autres])
t_nettoyage = tableau(["Table", "Lignes brutes", "Lignes Silver", "Rejetées", "Échecs de conversion", "Autres compteurs"], lignes)

jo = charger("transformations/jointures.json")
t_jointures = tableau(["Jointure (gauche → droite)", "Lignes avant", "Lignes après", "Clé gauche nulle", "Orphelins (clé non rapprochée)"],
                      [[f"{j['gauche']} → {j['droite']}", milliers(j["lignes_avant"]), milliers(j["lignes_apres"]), j["cle_gauche_nulle"], j["orphelins"]] for j in jo])

cf = charger("parquet/comparaison_formats.json")
taille_csv = cf["formats"][0]["taille_octets"]
t_formats = tableau(["Format", "Taille (octets)", "% du CSV", "Lignes relues", "Colonnes relues en texte (sur %d)" % cf["formats"][0]["colonnes"], "Temps d'agrégation (s, médiane de 3)"],
                    [[f["format"], milliers(f["taille_octets"]), round(100 * f["taille_octets"] / taille_csv), milliers(f["lignes_relues"]), f["colonnes_string"], f["temps_agregation_s"]] for f in cf["formats"]])
relecture = (f"{milliers(cf['lignes_source'])} lignes relues (source : {milliers(cf['lignes_source'])}), schéma identique à la source : "
             f"{'oui' if cf['parquet_meme_schema'] else 'NON'}, lignes différentes : {cf['parquet_lignes_differentes']} ; "
             f"lecture de 2 colonnes seulement : {cf['parquet_2_colonnes_s']} s.")

q = charger("qualite/controles_qualite.json")
ok, ko, nv = (sum(r["statut"] == s for r in q) for s in ("OK", "ANOMALIE", "NON VERIFIABLE"))
synthese = f"**{len(q)} contrôles : {ok} OK, {ko} anomalie(s), {nv} non vérifiable(s).**"
t_qualite = tableau(["Famille", "Cible", "Règle", "Mesure", "Attendu", "Statut", "Remarque"],
                    [[r["famille"], r["cible"], r["regle"], "" if r["mesure"] is None else milliers(r["mesure"]), r["attendu"], r["statut"], r["remarque"]] for r in q])

etat = csv_gold("clients_par_etat")
tranche = csv_gold("clients_par_tranche_revenu")
stock = csv_gold("stock_moyen_entrepot_mois")
g1 = "**clients_par_etat** (" + str(len(etat)) + " lignes, 8 premiers états) :\n\n" + tableau(["État", "Clients", "Part (%)"], [[r["etat"], r["nb_clients"], r["part_pct"]] for r in etat[:8]])
g2 = "**clients_par_tranche_revenu** (" + str(len(tranche)) + " lignes) :\n\n" + tableau(["Tranche", "Clients", "Part (%)"], [[r["tranche"], r["nb_clients"], r["part_pct"]] for r in tranche])
par_ent = {}
for r in stock:
    par_ent.setdefault(r["inv_warehouse_sk"], []).append(float(r["stock_moyen"]))
g3 = "**stock_moyen_entrepot_mois** (" + str(len(stock)) + " lignes ; résumé par entrepôt, un entrepôt = 56 mois) :\n\n" + tableau(
    ["Entrepôt", "Mois", "Stock moyen min", "Stock moyen max", "Moyenne des mois"],
    [[e, len(v), min(v), max(v), round(statistics.mean(v), 2)] for e, v in sorted(par_ent.items())])
t_gold = g1 + "\n\n" + g2 + "\n\n" + g3

remplace = {"{{TABLE_NETTOYAGE}}": t_nettoyage, "{{TABLE_JOINTURES}}": t_jointures, "{{TABLE_GOLD}}": t_gold, "{{TABLE_FORMATS}}": t_formats,
            "{{PARQUET_RELECTURE}}": relecture, "{{SYNTHESE_QUALITE}}": synthese, "{{TABLE_QUALITE}}": t_qualite}


def doc(nom):
    s = lire(nom)
    for k, v in remplace.items():
        s = s.replace(k, v)
    return s


annexe = "# Annexe – Preuves et reproduction\n\n" + open(os.path.join(P, "README.md"), encoding="utf-8").read().split("\n", 2)[2]
parties = [doc("UC06_environnement.md"), doc("UC06_inventaire.md"), doc("UC06_exploration.md"), doc("UC06_nettoyage.md"),
           doc("UC06_transformations.md"), doc("UC06_parquet.md"), doc("UC06_qualite.md"), annexe]

css = """
@page { size: A4 landscape; margin: 12mm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; line-height: 1.4; color: #111; }
h1 { font-size: 20px; border-bottom: 2px solid #305496; padding-bottom: 4px; page-break-before: always; }
h1:first-child { page-break-before: avoid; }
h2 { font-size: 15px; color: #305496; margin-top: 18px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #dce6f5; }
code { background: #f1f1f1; padding: 0 2px; }
"""
html = markdown.markdown((chr(10) * 2).join(parties), extensions=["tables", "fenced_code"]).replace(chr(92) + "|", "|")
page = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>UC06_traitements_PySpark</title><style>{css}</style></head><body>{html}</body></html>'
tmp = os.path.join(src, "_UC06.html")
open(tmp, "w", encoding="utf-8").write(page)

from selenium import webdriver
from selenium.webdriver.edge.options import Options
opt = Options(); opt.add_argument("--headless=new")
nav = webdriver.Edge(options=opt)  # l'appel direct a msedge --print-to-pdf ne produit plus de fichier
nav.get("file:///" + tmp.replace(chr(92), "/").replace(" ", "%20"))
r = nav.execute_cdp_cmd("Page.printToPDF", {"landscape": True, "printBackground": True, "preferCSSPageSize": True, "displayHeaderFooter": False})
pdf = os.path.join(racine, "UC06_traitements_PySpark.pdf")
open(pdf, "wb").write(base64.b64decode(r["data"]))
nav.quit()
os.remove(tmp)
print("pdf", os.path.getsize(pdf))
