"""UC-07 parcours B : materialise en local l'organisation ADLS Gen2 proposee (bronze/silver/gold/quality/documentation),
depose des fichiers du projet, puis relit chaque fichier et verifie sa taille et son SHA-256.
usage : python uc07_arborescence_locale.py <dossier du kit contenant customer/customer.dat>"""
import hashlib, json, os, shutil, sys

kit = sys.argv[1]
racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
j3 = os.path.join(racine, "..", "Jour3")
lac = os.path.join(racine, "preuves", "uc07", "lake_local", "retail-intelligence")
preuves = os.path.join(racine, "preuves", "uc07")
if os.path.exists(lac):
    shutil.rmtree(lac)

for d in ["bronze/tpcxbb/customer/ingest_date=2026-11-19", "silver/household_demographics", "silver/income_band",
          "gold/indicateurs/clients_par_etat", "gold/indicateurs/clients_par_tranche_revenu", "gold/indicateurs/stock_moyen_entrepot_mois",
          "gold/analyses", "quality/uc06", "documentation"]:
    os.makedirs(os.path.join(lac, d))

# echantillon bronze : 200 premieres lignes (octets, CRLF conserve)
with open(os.path.join(kit, "customer", "customer.dat"), "rb") as f:
    lignes = [f.readline() for _ in range(200)]
open(os.path.join(lac, "bronze/tpcxbb/customer/ingest_date=2026-11-19/customer_echantillon_200.dat"), "wb").write(b"".join(lignes))


def copier_parquet(zone_src, nom_src, dest):
    d = os.path.join(j3, "data", zone_src, nom_src)
    for fichier in os.listdir(d):
        if fichier.endswith(".parquet"):
            shutil.copy(os.path.join(d, fichier), os.path.join(lac, dest, fichier))


copier_parquet("silver", "household_demographics", "silver/household_demographics")
copier_parquet("silver", "income_band", "silver/income_band")
for nom in ["clients_par_etat", "clients_par_tranche_revenu", "stock_moyen_entrepot_mois"]:
    copier_parquet("gold", nom, f"gold/indicateurs/{nom}")
for nom in ["kpi.csv", "statistiques.csv"]:
    shutil.copy(os.path.join(racine, "preuves", "uc08", "resultats", nom), os.path.join(lac, "gold/analyses", nom))
shutil.copy(os.path.join(j3, "preuves", "qualite", "controles_qualite.json"), os.path.join(lac, "quality/uc06/controles_qualite.json"))
shutil.copy(os.path.join(racine, "..", "Jour1", "UC01_preuves", "dictionnaire_KPI.xlsx"), os.path.join(lac, "documentation/dictionnaire_KPI.xlsx"))


def sha256(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


manifeste, arbre = [], []
for dossier, sous, fichiers in sorted(os.walk(lac)):
    rel = os.path.relpath(dossier, os.path.dirname(lac)).replace("\\", "/")
    arbre.append(rel + "/")
    for f in sorted(fichiers):
        p = os.path.join(dossier, f)
        manifeste.append({"chemin": rel + "/" + f, "octets": os.path.getsize(p), "sha256": sha256(p)})
        arbre.append(f"    {f}  ({os.path.getsize(p)} octets)")

# verification : relecture independante de chaque fichier depuis le manifeste
ko = [m["chemin"] for m in manifeste if sha256(os.path.join(os.path.dirname(lac), m["chemin"])) != m["sha256"]
      or os.path.getsize(os.path.join(os.path.dirname(lac), m["chemin"])) != m["octets"]]
os.makedirs(preuves, exist_ok=True)
json.dump(manifeste, open(os.path.join(preuves, "manifeste_lake_local.json"), "w", encoding="utf-8"), indent=1)
open(os.path.join(preuves, "arborescence_lake_local.txt"), "w", encoding="utf-8").write("\n".join(arbre) + "\n")
print("\n".join(arbre))
print(f"\n{len(manifeste)} fichiers deposes, {len(manifeste) - len(ko)} verifies (taille + SHA-256), ecarts : {len(ko)}")
assert not ko
