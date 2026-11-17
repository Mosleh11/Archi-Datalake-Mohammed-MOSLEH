"""Assemble les PDF du Jour 2 a partir de sources_md/ (Markdown -> HTML -> Edge headless)"""
import base64, os, markdown

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(racine, "sources_md")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def lire(chemin):
    return open(os.path.join(src, chemin), encoding="utf-8").read()


def annexe(titre, chemin):
    return f"# Annexe – {titre}\n\n" + lire(chemin).split("\n", 2)[2]


docs = {
    "UC03_Hadoop_HDFS.pdf": [lire("UC03_environnement.md"), lire("UC03_inventaire.md"), lire("UC03_data_lake.md"),
                             lire("UC03_commandes.md"), annexe("Preuves UC-03", "../UC03_preuves/README.md")],
    "UC04_ingestion_NiFi.pdf": [lire("UC04_flux_nifi.md"), lire("UC04_provenance.md"), lire("tests_validation.md"),
                                lire("questions_recul.md"), annexe("Preuves UC-04", "../UC04_preuves/README.md")],
    "README_Jour2.pdf": [lire("../README.md")],
    "Complementaire/CO01_blocs_replication.pdf": [lire("Complementaire_CO01.md")],
    "Complementaire/CO02_convention_nommage.pdf": [lire("Complementaire_CO02.md")],
    "Complementaire/CO03_controle_integrite.pdf": [lire("Complementaire_CO03.md")],
    "Complementaire/CO04_supervision_nifi.pdf": [lire("Complementaire_CO04.md")],
    "Complementaire/CO05_procedure_reprise.pdf": [lire("CO05_reprise.md")],
}

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
img { max-width: 75%; max-height: 520px; display: block; margin: 6px 0; border: 1px solid #ccc; }
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options

opt = Options()
opt.add_argument("--headless=new")
opt.add_argument("--allow-file-access-from-files")
nav = webdriver.Edge(options=opt)  # Edge pilote par Selenium : l'appel direct a msedge --print-to-pdf ne produisait plus de fichier

for sortie, parties in docs.items():
    html = markdown.markdown((chr(10) * 2).join(parties), extensions=["tables", "fenced_code"]).replace(chr(92) + "|", "|")
    nom = os.path.basename(sortie)[:-4]
    page = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{nom}</title><style>{css}</style></head><body>{html}</body></html>'
    tmp = os.path.join(src, f"_{nom}.html")
    open(tmp, "w", encoding="utf-8").write(page)
    nav.get("file:///" + tmp.replace(chr(92), "/").replace(" ", "%20"))
    pdf = os.path.join(racine, sortie)
    r = nav.execute_cdp_cmd("Page.printToPDF", {"landscape": True, "printBackground": True, "preferCSSPageSize": True,
                                                "displayHeaderFooter": False})
    open(pdf, "wb").write(base64.b64decode(r["data"]))
    os.remove(tmp)
    print("pdf", sortie, os.path.getsize(pdf))
nav.quit()
