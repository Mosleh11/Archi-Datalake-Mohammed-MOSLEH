"""Génère les schémas SVG (besoins, architecture cible, flux) dans sources_md/img/"""
import os
from xml.sax.saxutils import escape

racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sortie = os.path.join(racine, "sources_md", "img")
os.makedirs(sortie, exist_ok=True)

VERT = ("#d9f2d9", "#2e7d32")
ORANGE = ("#ffe9c7", "#c77700")
GRIS = ("#eeeeee", "#777777")
BLEU = ("#dce8fb", "#1f4e9c")
BRONZE = ("#f3dfc6", "#8a5a1e")
ARGENT = ("#e6e9ee", "#5b6573")
OR = ("#fff3b8", "#a07d00")
ROSE = ("#fde2e2", "#a33")


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = []

    def box(self, x, y, w, h, lignes, couleur=BLEU, tirets=False, gras=False, taille=13):
        fill, stroke = couleur
        dash = ' stroke-dasharray="6,4"' if tirets else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>')
        if isinstance(lignes, str):
            lignes = [lignes]
        lh = taille + 3
        y0 = y + h / 2 - (len(lignes) - 1) * lh / 2 + taille / 3
        for i, l in enumerate(lignes):
            w_ = ' font-weight="bold"' if (gras and i == 0) else ""
            self.p.append(f'<text x="{x + w / 2}" y="{y0 + i * lh}" text-anchor="middle" font-size="{taille}"{w_}>{escape(l)}</text>')

    def texte(self, x, y, t, taille=13, gras=False, ancre="start"):
        g = ' font-weight="bold"' if gras else ""
        self.p.append(f'<text x="{x}" y="{y}" font-size="{taille}" text-anchor="{ancre}"{g}>{escape(t)}</text>')

    def fleche(self, x1, y1, x2, y2):
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#444" stroke-width="1.5" marker-end="url(#fl)"/>')

    def save(self, nom):
        defs = '<defs><marker id="fl" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#444"/></marker></defs>'
        s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
             f'font-family="Arial, Helvetica, sans-serif"><rect width="100%" height="100%" fill="white"/>{defs}' + "".join(self.p) + "</svg>")
        open(os.path.join(sortie, nom), "w", encoding="utf-8").write(s)


# ---------- 1. schéma des besoins ----------
lignes = [
    ("Direction commerciale", "Quels produits vendent le plus ?", "KPI-01, KPI-04", ["store_sales, web_sales, item"], GRIS, "absent du zip"),
    ("Direction générale", "Comment évoluent les ventes ?", "KPI-05", ["*_sales (absent) + date_dim (observé)"], ORANGE, "partiel"),
    ("Direction / resp. magasin", "Quels magasins performent ?", "KPI-01 par magasin", ["store_sales, store"], GRIS, "absent du zip"),
    ("Direction commerciale", "Quels volumes par canal ?", "KPI-01, 02, 03", ["store_sales, web_sales"], GRIS, "absent du zip"),
    ("Contrôleur de gestion", "Quel taux de remise ?", "KPI-06", ["store_sales, web_sales"], GRIS, "absent du zip"),
    ("Direction commerciale", "Quels produits sont retournés ?", "KPI-07", ["store_returns, web_returns"], GRIS, "absent du zip"),
    ("Responsable des stocks", "Quels niveaux de stock ?", "KPI-08", ["inventory (observé, tronqué)", "item, warehouse (absents)"], ORANGE, "partiel"),
    ("Direction commerciale", "Comment caractériser les clients ?", "KPI-09, KPI-10", ["customer, customer_address,", "customer_demographics, household_", "demographics, income_band"], VERT, "observé"),
    ("Direction commerciale", "Que font les visiteurs web ?", "(clics, pas des achats)", ["web_clickstreams"], GRIS, "absent du zip"),
]
H = 70 + len(lignes) * 62
s = Svg(1200, H)
s.texte(20, 28, "Schéma fonctionnel UC-01 : utilisateurs, questions, KPI et tables", 17, True)
for x, t in [(20, "Utilisateur"), (260, "Question décisionnelle"), (560, "KPI"), (770, "Tables (statut)")]:
    s.texte(x, 55, t, 13, True)
for i, (u, q, k, tabs, c, st) in enumerate(lignes):
    y = 65 + i * 62
    s.box(20, y, 210, 48, u, BLEU)
    s.box(260, y, 270, 48, q, BLEU)
    s.box(560, y, 180, 48, k, BLEU)
    s.box(770, y, 340, 48, tabs, c, tirets=(c == GRIS))
    s.texte(1120, y + 28, st, 11)
    s.fleche(230, y + 24, 260, y + 24); s.fleche(530, y + 24, 560, y + 24); s.fleche(740, y + 24, 770, y + 24)
s.box(20, H - 28, 14, 14, "", VERT); s.texte(40, H - 17, "observé dans les fichiers", 11)
s.box(220, H - 28, 14, 14, "", ORANGE); s.texte(240, H - 17, "partiellement observé", 11)
s.box(420, H - 28, 14, 14, "", GRIS, tirets=True); s.texte(440, H - 17, "absent du zip reçu (supposé / souhaité)", 11)
s.save("schema_besoins.svg")

# ---------- 2. architecture cible ----------
s = Svg(1250, 560)
s.texte(20, 28, "Architecture logique cible : Retail Intelligence Platform (batch)", 17, True)
cols = [(20, 170, "SOURCES"), (225, 150, "INGESTION"), (410, 170, "BRONZE"), (615, 190, "SILVER"), (840, 170, "GOLD"), (1045, 185, "EXPOSITION")]
for x, w, t in cols:
    s.texte(x + w / 2, 58, t, 13, True, "middle")
# sources
s.box(20, 70, 170, 110, ["TPCx-BB (.dat)", "7 tables observées :", "customer*, date_dim,", "household_dem., income_band,", "inventory"], VERT, gras=True, taille=11)
s.box(20, 190, 170, 80, ["TPCx-BB attendu", "(ventes, retours, item,", "store... absents du zip)"], GRIS, tirets=True, taille=11)
s.box(20, 280, 170, 70, ["Compléments éventuels", "(JSON, logs) : synthétiques,", "toujours séparés"], GRIS, tirets=True, taille=11)
# ingestion
s.box(225, 70, 150, 280, ["Apache NiFi", "", "dépôt des fichiers", "contrôle de présence", "ajout de la provenance", "(source, date, taille,", "somme de contrôle)", "", "Repli documenté :", "scripts Python + HDFS"], BLEU, gras=True, taille=11)
# bronze
s.box(410, 70, 170, 280, ["Stockage brut (HDFS)", "", "/datalake/bronze/", "  tpcxbb/<table>/", "  ingest_date=AAAA-MM-JJ/", "", "fichiers .dat tels que reçus", "(sans modification)", "", "+ manifeste de provenance", "Lecture seule"], BRONZE, gras=True, taille=11)
# silver
s.box(615, 70, 190, 280, ["Préparation et contrôle", "(Spark / PySpark)", "", "typage selon le DDL de la spec", "noms de colonnes ajoutés", "vides -> NULL", "contrôle de clés et jointures", "doublons, valeurs négatives", "rejets -> /silver/_rejets", "", "Parquet typé", "/datalake/silver/<table>/"], ARGENT, gras=True, taille=11)
# gold
s.box(840, 70, 170, 280, ["Données analytiques", "", "Parquet partitionné", "/datalake/gold/", "", "faits et dimensions", "(étoile, grain défini)", "agrégats de KPI", "par période / magasin /", "produit / canal"], OR, gras=True, taille=11)
# exposition
s.box(1045, 70, 185, 130, ["Exposition des KPI", "", "requêtes SQL / Spark", "tableaux de bord BI"], BLEU, gras=True, taille=11)
s.box(1045, 210, 185, 140, ["Consommateurs", "", "Direction, commercial,", "contrôle de gestion,", "stocks, équipe Data"], BLEU, taille=11)
for x1, x2 in [(190, 225), (375, 410), (580, 615), (805, 840), (1010, 1045)]:
    s.fleche(x1, 210, x2, 210)
# gouvernance
s.box(20, 380, 1210, 70, ["GOUVERNANCE : catalogue et dictionnaire de données | traçabilité (provenance, lineage) | rôles et droits d'accès par zone | masquage des données personnelles (nom, email, login) | règles de qualité"], ROSE, gras=False, taille=12)
s.box(20, 465, 1210, 55, ["SUPERVISION : journaux de chaque traitement | compteurs de lignes entrée/sortie | alertes sur rejets | suivi des volumes et des coûts"], ROSE, taille=12)
s.texte(20, 545, "Vert = observé dans le zip reçu ; gris pointillé = attendu mais non fourni ou facultatif (traité séparément).", 11)
s.save("architecture_cible.svg")

# ---------- 3. schéma des flux ----------
flux = [
    ("F1 Référentiels clients", ["customer, customer_address,", "customer_demographics,", "household_dem., income_band", ".dat | CRLF, sans en-tête"], ["Zone Silver", "contrôle clés / jointures,", "vides -> NULL, Parquet"], ["Gold", "dim_client"], "Direction, marketing", VERT),
    ("F2 Dates", ["date_dim", ".dat, 109 573 lignes"], ["Silver", "d_date en type date,", "contrôle de la plage"], ["Gold", "dim_date"], "Tous les KPI (axe temps)", VERT),
    ("F3 Stocks", ["inventory", ".dat, ~21,8 M lignes"], ["Silver", "contrôle semaine complète,", "quantité 0-1000, doublons"], ["Gold", "fait_stock (jour, article,", "entrepôt)"], "Responsable des stocks", ORANGE),
    ("F4 Ventes et retours", ["store_sales, web_sales,", "store_returns, web_returns,", "item, store (non fournis)"], ["Silver", "grain ticket/article,", "clés vers dimensions"], ["Gold", "fait_ventes, fait_retours,", "KPI-01 à 07"], "Direction, contrôle de gestion", GRIS),
    ("F5 Clics web (si fournis)", ["web_clickstreams,", "web_page (non fournis)"], ["Silver", "clics non nuls,", "sessions"], ["Gold", "fait_clics"], "Direction commerciale", GRIS),
]
s = Svg(1250, 80 + len(flux) * 120)
s.texte(20, 28, "Schéma des flux de données (batch) : source -> bronze -> silver -> gold -> consommateur", 17, True)
for x, w, t in [(20, 170, "Source / format"), (225, 130, "Ingestion"), (390, 130, "Bronze"), (555, 220, "Contrôles et transformations"), (810, 200, "Gold"), (1045, 185, "Consommateur")]:
    s.texte(x, 58, t, 13, True)
for i, (nom, src, silver, gold, cons, c) in enumerate(flux):
    y = 70 + i * 120
    s.texte(20, y + 8, nom, 12, True)
    t = c == GRIS
    s.box(20, y + 15, 170, 80, src, c, tirets=t, taille=11)
    s.box(225, y + 15, 130, 80, ["NiFi", "(batch)"], BLEU, tirets=t, taille=11)
    s.box(390, y + 15, 130, 80, ["Bronze", "brut + provenance"], BRONZE, tirets=t, taille=11)
    s.box(555, y + 15, 220, 80, silver, ARGENT, tirets=t, taille=11)
    s.box(810, y + 15, 200, 80, gold, OR, tirets=t, taille=11)
    s.box(1045, y + 15, 185, 80, cons, BLEU, tirets=t, taille=11)
    for x1, x2 in [(190, 225), (355, 390), (520, 555), (775, 810), (1010, 1045)]:
        s.fleche(x1, y + 55, x2, y + 55)
s.texte(20, 70 + len(flux) * 120 + 10, "Vert : flux testable avec le zip reçu ; orange : partiel (fichier tronqué) ; gris pointillé : tables non fournies, flux conçu mais non vérifié.", 11)
s.save("schema_flux.svg")
print("svg ok")
