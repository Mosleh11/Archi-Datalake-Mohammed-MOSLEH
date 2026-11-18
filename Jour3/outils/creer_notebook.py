"""Genere notebooks/exploration.ipynb (non execute) ; l'execution se fait avec scripts/lancer_notebook.sh"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
    md("# Exploration des sources TPCx-BB avec PySpark\n\nTP Jour 3 – UC-06. Les fichiers `.dat` (séparateur `|`, sans en-tête) sont lus **en texte** avec les noms de colonnes du DDL de la spec TPCx-BB v1.7.0. "
       "Les fichiers sources ne sont jamais modifiés."),
    md("## 1. Environnement"),
    code("import sys, platform, subprocess\nsys.path.append('/work/scripts')\nfrom commun import *\n"
         "import pyspark\nprint('Python :', platform.python_version())\nprint('PySpark :', pyspark.__version__)\n"
         "print(subprocess.run(['java', '-version'], capture_output=True, text=True).stderr.splitlines()[0])\n"
         "spark = session('exploration')\nprint('Spark :', spark.version, '| mode :', spark.sparkContext.master)\nprint('RAW :', RAW, '| sorties :', DATA)"),
    md("## 2. Fonction d'exploration\n\nPour chaque source : schéma, échantillon, nombre de lignes, valeurs manquantes, doublons sur la clé candidate, min/max des colonnes numériques."),
    code("from pyspark.sql import functions as F\n\n"
         "def explorer(table, cle):\n"
         "    df = lire_raw(spark, table)\n"
         "    print('=====', table, '=====')\n"
         "    df.printSchema()\n"
         "    df.show(5, truncate=False)\n"
         "    n = df.count()\n"
         "    print('Lignes :', n, '| colonnes :', len(df.columns))\n"
         "    nulls = df.agg(*[F.sum(F.col(c).isNull().cast('int')).alias(c) for c in df.columns]).first().asDict()\n"
         "    print('Valeurs manquantes (colonne : nb, %) :')\n"
         "    for c, v in nulls.items():\n"
         "        if v: print(f'  {c} : {v} ({100 * v / n:.3f} %)')\n"
         "    if not any(nulls.values()): print('  aucune')\n"
         "    distincts = df.select(*cle).distinct().count()\n"
         "    print('Cle candidate', cle, ':', distincts, 'valeurs distinctes ->', 'doublons :', n - distincts)\n"
         "    num = [c for c, t in SCHEMA[table] if t in ('bigint', 'int')]\n"
         "    mm = df.agg(*[F.min(F.col(c).cast('long')).alias('min_' + c) for c in num] + [F.max(F.col(c).cast('long')).alias('max_' + c) for c in num]).first().asDict()\n"
         "    print('Min / max numeriques :')\n"
         "    for c in num: print(f'  {c} : {mm[\"min_\" + c]} -> {mm[\"max_\" + c]}')\n"
         "    return df"),
    md("## 3. Source 1 – customer (clients, une ligne par client)"),
    code("customer = explorer('customer', ['c_customer_sk'])"),
    md("## 4. Source 2 – customer_address (adresses, une ligne par adresse)"),
    code("adresse = explorer('customer_address', ['ca_address_sk'])\n"
         "adresse.groupBy('ca_state').count().orderBy(F.desc('count')).show(5)"),
    md("## 5. Source 3 – household_demographics (foyers)"),
    code("foyer = explorer('household_demographics', ['hd_demo_sk'])\n"
         "foyer.groupBy('hd_vehicle_count').count().orderBy('hd_vehicle_count').show()"),
    md("## 6. Source 4 – income_band (tranches de revenu)"),
    code("tranche = explorer('income_band', ['ib_income_band_sk'])"),
    md("## 7. Source 5 – date_dim (calendrier)"),
    code("dates = explorer('date_dim', ['d_date_sk'])\n"
         "dates.select(F.min('d_date'), F.max('d_date')).show()"),
    md("## 8. Source 6 – inventory (stocks, une ligne par date, article et entrepôt)\n\nLe fichier est tronqué : on s'attend à une dernière ligne incomplète."),
    code("inv = explorer('inventory', ['inv_date_sk', 'inv_item_sk', 'inv_warehouse_sk'])\n"
         "print('Lignes dont une cle est absente (ligne incomplete) :')\n"
         "inv.filter(F.col('inv_item_sk').isNull() | F.col('inv_warehouse_sk').isNull()).show(truncate=False)\n"
         "print('Lignes par date (5 dernieres dates) :')\n"
         "inv.groupBy('inv_date_sk').count().orderBy(F.desc('inv_date_sk')).show(5)"),
    md("## 9. Constats\n\n"
       "- Les 6 sources sont **structurées** (texte délimité par `|`, CRLF, sans en-tête) ; les types viennent du DDL de la spec, pas du fichier.\n"
       "- Clés candidates uniques sur les 6 sources ; aucun doublon sur la clé.\n"
       "- Valeurs manquantes : environ 0,02 à 0,05 % dans `customer` et `customer_address`, `inv_quantity_on_hand` à 0,026 %, rien dans `date_dim` ni `income_band`.\n"
       "- `hd_vehicle_count` contient la valeur **-1** (non conforme à un nombre de véhicules).\n"
       "- `inventory` : dernière ligne incomplète (fichier tronqué) et dernière date à 11 808 lignes au lieu de 90 000.\n"
       "- `date_dim` couvre 1900 à 2199 (109 573 jours).\n"
       "- Les décisions de nettoyage sont dans la partie « Règles de nettoyage » de `UC06_traitements_PySpark.pdf` et appliquées par `scripts/nettoyage.py`."),
    code("spark.stop()"),
]
nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
nbf.write(nb, "notebooks/exploration.ipynb")
print("notebook cree")
