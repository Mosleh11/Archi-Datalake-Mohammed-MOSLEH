"""Etape 1 : versions, session Spark, lecture d'un fichier de test, schema, ecriture d'un resultat de test dans un dossier a part"""
import platform, subprocess, shutil, os
import pyspark
from commun import *

print("Python :", platform.python_version(), "|", platform.platform())
print("PySpark :", pyspark.__version__)
print(subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.splitlines()[0])
print("CPU visibles :", os.cpu_count())
spark = session("verification_env")
print("Spark :", spark.version, "| mode :", spark.sparkContext.master, "| memoire driver :", spark.conf.get("spark.driver.memory"))
print("Chemin des donnees brutes :", RAW, "| sorties :", DATA)
df = lire_raw(spark, "income_band")
df.printSchema()
df.show(5, truncate=False)
print("lignes lues :", df.count())
test = f"{DATA}/_test/income_band"
shutil.rmtree(f"{DATA}/_test", ignore_errors=True)
df.write.mode("overwrite").parquet(test)
print("ecriture de test OK, relu :", spark.read.parquet(test).count(), "lignes")
shutil.rmtree(f"{DATA}/_test", ignore_errors=True)
spark.stop()
