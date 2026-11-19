"""Assemble UC08_analyse_visualisation.pdf et UC07_architecture_Azure.pdf a partir de sources_md/ et des resultats CSV (Markdown -> HTML -> Edge via Selenium)"""
import base64, csv, os, re, markdown

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(racine, "sources_md")
images = {}
for dossier in ("visualisations", "architecture"):
    for f in os.listdir(os.path.join(racine, dossier)):
        if f.endswith(".png"):
            images[f] = os.path.join(racine, dossier, f)


def lire(nom):
    return open(os.path.join(src, nom), encoding="utf-8").read()


def lire_csv(nom):
    return list(csv.DictReader(open(os.path.join(racine, "preuves", "uc08", "resultats", nom), encoding="utf-8")))


def tableau(entetes, lignes):
    out = ["| " + " | ".join(entetes) + " |", "|" + "---|" * len(entetes)]
    for l in lignes:
        out.append("| " + " | ".join(str(x).replace("|", "/") for x in l) + " |")
    return "\n".join(out)


def milliers(v):
    try:
        return f"{int(float(v)):,}".replace(",", " ") if float(v) == int(float(v)) else str(v).replace(".", ",")
    except ValueError:
        return v


inv = lire_csv("inventaire_jeux.csv")
kpi = lire_csv("kpi.csv")
stats = lire_csv("statistiques.csv")
rep = lire_csv("repartitions.csv")
remplace = {
    "{{TABLE_INVENTAIRE}}": tableau(["Jeu", "Zone", "Format", "Granularité", "Lignes", "Colonnes"],
                                    [[r["jeu"], r["zone"], r["format"], r["granularite"], milliers(r["lignes"]), r["colonnes"]] for r in inv]),
    "{{TABLE_KPI}}": "**Valeurs calculées (`preuves/uc08/resultats/kpi.csv`)**\n\n" + tableau(["KPI", "Nom", "Valeur", "Unité", "Périmètre"],
                                    [[r["kpi"], r["nom"], milliers(r["valeur"]), r["unite"], r["perimetre"]] for r in kpi]),
    "{{TABLE_STATS}}": tableau(["Jeu", "Colonne", "Valeurs", "Manquantes", "Min", "Max", "Moyenne", "Médiane", "Écart-type"],
                               [[r["jeu"], r["colonne"], milliers(r["valeurs"]), milliers(r["manquantes"]), r["min"], r["max"], str(r["moyenne"]).replace(".", ","), r["mediane"], str(r["ecart_type"]).replace(".", ",")] for r in stats]),
    "{{TABLE_REPARTITIONS}}": tableau(["Variable", "Valeur", "Clients", "Part (%)"],
                                      [[r["colonne"], r["valeur"], milliers(r["nb_clients"]), str(r["part_pct"]).replace(".", ",")] for r in rep]),
}


def doc(nom):
    s = lire(nom)
    for k, v in remplace.items():
        s = s.replace(k, v)
    def img(m):
        chemin = images[m.group(2)]
        return f"![{m.group(1)}](data:image/png;base64,{base64.b64encode(open(chemin, 'rb').read()).decode()})"
    return re.sub(r"!\[([^\]]*)\]\(IMG:([^)]+)\)", img, s)


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
code, pre { background: #f1f1f1; padding: 0 2px; }
img { max-width: 100%; max-height: 520px; display: block; margin: 8px auto; page-break-inside: avoid; }
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options


def pdf(nom, fichiers):
    html = markdown.markdown((chr(10) * 2).join(doc(f) for f in fichiers), extensions=["tables", "fenced_code"]).replace(chr(92) + "|", "|")
    page = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{nom}</title><style>{css}</style></head><body>{html}</body></html>'
    tmp = os.path.join(src, f"_{nom}.html")
    open(tmp, "w", encoding="utf-8").write(page)
    opt = Options(); opt.add_argument("--headless=new")
    nav = webdriver.Edge(options=opt)  # l'appel direct a msedge --print-to-pdf ne produit plus de fichier
    nav.get("file:///" + tmp.replace(chr(92), "/").replace(" ", "%20"))
    r = nav.execute_cdp_cmd("Page.printToPDF", {"landscape": True, "printBackground": True, "preferCSSPageSize": True, "displayHeaderFooter": False})
    sortie = os.path.join(racine, nom + ".pdf")
    open(sortie, "wb").write(base64.b64decode(r["data"]))
    nav.quit()
    os.remove(tmp)
    print(nom, os.path.getsize(sortie))


pdf("UC08_analyses_visualisations", ["UC08_01_environnement.md", "UC08_02_inventaire_kpi.md", "UC08_03_statistiques.md", "UC08_04_analyses.md", "UC08_05_visualisations.md", "UC08_06_synthese.md"])
pdf("UC07_architecture_azure", ["UC07_01_parcours.md", "UC07_02_architecture.md", "UC07_03_adls.md", "UC07_04_securite.md", "UC07_05_simulation.md"])

# livrables du dossier architecture/ : organisation ADLS (markdown) et matrice des permissions (pdf)
import shutil
shutil.copy(os.path.join(src, "UC07_03_adls.md"), os.path.join(racine, "architecture", "organisation_adls.md"))
pdf_dest = os.path.join(racine, "architecture")
pdf("matrice_permissions", ["UC07_04_securite.md"])
shutil.move(os.path.join(racine, "matrice_permissions.pdf"), os.path.join(pdf_dest, "matrice_permissions.pdf"))
