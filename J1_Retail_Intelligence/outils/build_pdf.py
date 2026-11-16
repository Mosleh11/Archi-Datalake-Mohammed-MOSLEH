"""Convertit les .md de sources_md/ en PDF (Markdown -> HTML -> Edge headless)"""
import os, subprocess, markdown

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(racine, "sources_md")
edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

uc1 = "01_UC01_besoin_exploration"
uc2 = "02_UC02_architecture"
docs = {
    "cadrage_metier": uc1, "questions_decisionnelles": uc1, "qualification_donnees": uc1, "limites_hypotheses": uc1,
    "comparaison_architectures": uc2, "architecture_cible": uc2, "schema_flux": uc2,
    "positionnement_composants": uc2, "gouvernance": uc2, "local_vers_azure": uc2,
}

css = """
@page { size: A4 landscape; margin: 12mm; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; line-height: 1.4; color: #111; }
h1 { font-size: 20px; border-bottom: 2px solid #305496; padding-bottom: 4px; }
h2 { font-size: 15px; color: #305496; margin-top: 18px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; page-break-inside: auto; }
tr { page-break-inside: avoid; }
th, td { border: 1px solid #999; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #dce6f5; }
code { background: #f1f1f1; padding: 0 2px; }
img { max-width: 100%; }
"""

for nom, dossier in docs.items():
    texte = open(os.path.join(src, nom + ".md"), encoding="utf-8").read()
    html = markdown.markdown(texte, extensions=["tables", "fenced_code"]).replace("\\|", "|")
    page = f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{nom}</title><style>{css}</style></head><body>{html}</body></html>'
    tmp = os.path.join(src, f"_{nom}.html")
    open(tmp, "w", encoding="utf-8").write(page)
    pdf = os.path.join(racine, dossier, nom + ".pdf")
    subprocess.run([edge, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                    "file:///" + tmp.replace("\\", "/").replace(" ", "%20")], check=True, capture_output=True, timeout=120)
    os.remove(tmp)
    print("pdf", dossier + "/" + nom + ".pdf", os.path.getsize(pdf))
