"""Chemins, session Spark et lecture des fichiers bruts (partages par tous les scripts)"""
import json, os
from pyspark.sql import SparkSession, functions as F, types as T

RAW = os.environ.get("RAW_DIR", "/data/raw")
DATA = os.environ.get("DATA_DIR", "/work/data")
PREUVES = os.environ.get("PREUVES_DIR", "/work/preuves")
SCHEMA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_spec_tpcxbb.json")))
TYPES = {"bigint": "bigint", "int": "int", "string": "string", "decimal": "decimal(5,2)"}


def session(nom):
    spark = (SparkSession.builder.appName(nom).master("local[4]")
             .config("spark.driver.memory", "4g")
             .config("spark.sql.shuffle.partitions", "8")
             .config("spark.sql.ansi.enabled", "false")  # une valeur non convertible devient null au lieu de faire planter
             .config("spark.ui.showConsoleProgress", "false")
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def lire_raw(spark, table):
    """Lit un .dat TPCx-BB : separateur |, pas d'en-tete, tout en texte (le typage est fait au nettoyage)"""
    schema = T.StructType([T.StructField(c, T.StringType(), True) for c, _ in SCHEMA[table]])
    return spark.read.csv(f"{RAW}/{table}/{table}.dat", sep="|", header=False, schema=schema, quote="")


def lire_parquet(spark, zone, nom):
    return spark.read.parquet(f"{DATA}/{zone}/{nom}")


def ecrire_parquet(df, zone, nom):
    df.write.mode("overwrite").parquet(f"{DATA}/{zone}/{nom}")


def sauver_json(objet, chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    json.dump(objet, open(chemin, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
