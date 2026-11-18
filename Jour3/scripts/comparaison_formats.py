"""Ecrit le meme jeu (silver/clients_enrichis) en CSV, JSON et Parquet, relit et compare taille, types et temps"""
import os, shutil, statistics, time
from pyspark.sql import functions as F
from commun import *

spark = session("formats")
df = lire_parquet(spark, "silver", "clients_enrichis")
n = df.count()
base = f"{DATA}/parquet"
shutil.rmtree(base, ignore_errors=True)

sorties = {"csv": lambda d, p: d.coalesce(1).write.option("header", True).csv(p),
           "json": lambda d, p: d.coalesce(1).write.json(p),
           "parquet": lambda d, p: d.coalesce(1).write.parquet(p)}
lecteurs = {"csv (sans inferSchema)": lambda p: spark.read.option("header", True).csv(p),
            "csv (inferSchema)": lambda p: spark.read.option("header", True).option("inferSchema", True).csv(p),
            "json": lambda p: spark.read.json(p),
            "parquet": lambda p: spark.read.parquet(p)}
dossier = {"csv (sans inferSchema)": "csv", "csv (inferSchema)": "csv", "json": "json", "parquet": "parquet"}


def taille(chemin):
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(chemin) for f in fs if not f.endswith(".crc") and f != "_SUCCESS")


for fmt, ecrire in sorties.items():
    ecrire(df, f"{base}/{fmt}")

resultats = []
for nom, lire in lecteurs.items():
    chemin = f"{base}/{dossier[nom]}"
    temps = []
    for _ in range(3):
        t = time.time()
        r = lire(chemin).groupBy("ca_state").count().collect()
        temps.append(time.time() - t)
    relu = lire(chemin)
    types_nuls = sum(1 for _, t in relu.dtypes if t == "string")
    resultats.append({"format": nom, "taille_octets": taille(chemin), "lignes_relues": relu.count(),
                      "colonnes": len(relu.columns), "colonnes_string": types_nuls,
                      "temps_agregation_s": round(statistics.median(temps), 2),
                      "types": dict(relu.dtypes)})
    print(nom, resultats[-1]["taille_octets"], "octets,", resultats[-1]["lignes_relues"], "lignes,",
          resultats[-1]["colonnes_string"], "colonnes string sur", resultats[-1]["colonnes"], ",", resultats[-1]["temps_agregation_s"], "s")

# relecture Parquet : schema et contenu identiques a la source
relu = spark.read.parquet(f"{base}/parquet")
meme_schema = relu.schema == df.schema
ecart = df.exceptAll(relu.select(df.columns)).count()
print("Parquet relu :", relu.count(), "lignes (source", n, ") ; meme schema :", meme_schema, "; lignes differentes :", ecart)
relu.printSchema()
relu.select("c_customer_sk", "ca_state", "tranche", "hd_vehicle_count").show(5, truncate=False)
# lecture de 2 colonnes seulement : Parquet ne lit que ces colonnes
t = time.time(); spark.read.parquet(f"{base}/parquet").select("c_customer_sk", "ca_state").count(); t2 = time.time() - t
sauver_json({"lignes_source": n, "formats": resultats, "parquet_meme_schema": meme_schema, "parquet_lignes_differentes": ecart,
             "parquet_2_colonnes_s": round(t2, 2)}, f"{PREUVES}/parquet/comparaison_formats.json")
spark.stop()
