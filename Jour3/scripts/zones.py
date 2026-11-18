"""Inventaire des jeux Silver et Gold produits : fichiers Parquet, taille, lignes, schema, echantillon ; export CSV des petits Gold"""
import csv, os
from commun import *

spark = session("zones")


def taille(chemin):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(chemin) for f in fs if f.endswith(".parquet"))


for zone in ("silver", "gold"):
    print(f"\n########## {zone.upper()} ##########")
    for nom in sorted(os.listdir(f"{DATA}/{zone}")):
        chemin = f"{DATA}/{zone}/{nom}"
        if nom.startswith("_") or not os.path.isdir(chemin):
            continue
        df = spark.read.parquet(chemin)
        fichiers = [f for r, _, fs in os.walk(chemin) for f in fs if f.endswith(".parquet")]
        print(f"\n== {zone}/{nom} : {df.count()} lignes, {len(df.columns)} colonnes, {len(fichiers)} fichier(s) Parquet, {taille(chemin)} octets")
        df.printSchema()
        df.show(3, truncate=False)
        if zone == "gold":
            lignes = [r.asDict() for r in df.collect()]
            os.makedirs(f"{PREUVES}/silver_gold", exist_ok=True)
            with open(f"{PREUVES}/silver_gold/gold_{nom}.csv", "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=df.columns); w.writeheader(); w.writerows(lignes)
rejets = f"{DATA}/silver/_rejets"
if os.path.isdir(rejets):
    print("\n########## REJETS (lignes mises a l'ecart) ##########")
    for nom in sorted(os.listdir(rejets)):
        spark.read.parquet(f"{rejets}/{nom}").show(truncate=False)
spark.stop()
