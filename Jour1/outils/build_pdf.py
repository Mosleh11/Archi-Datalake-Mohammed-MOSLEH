"""Assemble UC01_besoin_donnees.pdf et UC02_architecture.pdf (sources_md -> HTML -> Edge headless)"""
import os, subprocess, markdown
from openpyxl import load_workbook

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(racine, "sources_md")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def lire(chemin):
    return open(chemin, encoding="utf-8").read()


def tableau(chemin_xlsx, feuille, colonnes):
    ws = load_workbook(chemin_xlsx)[feuille]
    lignes = list(ws.iter_rows(values_only=True))
    idx = [lignes[0].index(c) for c in colonnes]
    out = ["| " + " | ".join(colonnes) + " |", "|" + "---|" * len(colonnes)]
    for l in lignes[1:]:
        out.append("| " + " | ".join(str(l[i] if l[i] is not None else "").replace("|", "/") for i in idx) + " |")
    return "\n".join(out)


def sec(nom):
    return lire(os.path.join(src, nom + ".md"))


p1 = os.path.join(racine, "UC01_preuves")
kpi = "# UC-01 – KPI retenus\n\nDétail complet (sources, colonnes, limites) : `UC01_preuves/dictionnaire_KPI.xlsx`.\n\n" + tableau(
    os.path.join(p1, "dictionnaire_KPI.xlsx"), "KPI",
    ["ID", "Nom", "Définition métier", "Formule", "Unité", "Périmètre / granularité", "Calculable avec le zip reçu ?"])
rel = "# UC-01 – Relations entre les tables\n\n" + tableau(
    os.path.join(p1, "inventaire_sources.xlsx"), "Relations",
    ["Colonne source", "Table cible", "Lignes", "Valeurs vides", "Sans correspondance", "Statut"])
annexe1 = "# Annexe – Preuves UC-01\n\n" + sec("../UC01_preuves/README").split("\n", 2)[2]
annexe2 = "# Annexe – Preuves UC-02\n\n" + sec("../UC02_preuves/README").split("\n", 2)[2]

docs = {
    "UC01_besoin_donnees": [sec("cadrage_metier"), sec("questions_decisionnelles"), kpi, sec("qualification_donnees"),
                            rel, sec("limites_hypotheses"), annexe1],
    "UC02_architecture": [sec("comparaison_architectures"), sec("architecture_cible"), sec("schema_flux"),
                          sec("positionnement_composants"), sec("gouvernance"), sec("local_vers_azure"), annexe2],
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
img { max-width: 100%; }
"""

for nom, parties in docs.items():
    texte = "\n\n".join(parties)
    html = markdown.markdown(texte, extensions=["tables", "fenced_code"]).replace(chr(92) + "|", "|")
    page = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{nom}</title><style>{css}</style></head><body>{html}</body></html>'
    tmp = os.path.join(src, f"_{nom}.html")
    open(tmp, "w", encoding="utf-8").write(page)
    pdf = os.path.join(racine, nom + ".pdf")
    subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    "file:///" + tmp.replace("\\", "/").replace(" ", "%20")], check=True, capture_output=True, timeout=180)
    os.remove(tmp)
    print("pdf", nom, os.path.getsize(pdf))
