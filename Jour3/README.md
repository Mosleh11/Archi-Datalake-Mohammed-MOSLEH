# TP Jour 3 – UC-06 : traitement et transformation avec Python / PySpark

Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh. Exécuté le 18/11/2026. Rapport : `UC06_traitements_PySpark.pdf`.

## Ce qui a été fait

Six sources du kit TPCx-BB (`customer`, `customer_address`, `household_demographics`, `income_band`, `date_dim`, `inventory`) sont explorées, nettoyées, jointes et agrégées avec PySpark, dans l'ordre Bronze (fichiers `.dat`) → Silver → Gold, avec des sorties Parquet et 49 contrôles qualité. Les KPI de ventes ne sont pas calculables (tables absentes du zip) : les trois Gold répondent à KPI-08 (stock), KPI-09 et KPI-10 (clients).

Non fait : partie complémentaire UC-05 (HBase / NoSQL), partie avancée (Lakehouse), lecture depuis HDFS (cas 2 du TP), Spark UI.

## Versions observées

Python 3.12.14, PySpark 4.3.0, Java OpenJDK 21.0.13, Spark en mode `local[4]` dans un conteneur Docker (voir `docker/Dockerfile`).

## Contenu

```
Jour3/
|-- README.md
|-- UC06_traitements_PySpark.pdf
|-- notebooks/exploration.ipynb        exploration exécutée (sorties incluses)
|-- scripts/
|   |-- commun.py                      chemins, session Spark, lecture des .dat
|   |-- nettoyage.py                   Bronze -> Silver
|   |-- transformations.py             jointures, Silver enrichi, Gold
|   |-- controles_qualite.py           contrôles qualité
|   |-- comparaison_formats.py         CSV / JSON / Parquet
|   |-- verification_env.py, zones.py  environnement, inventaire des zones
|   |-- lancer.sh, lancer_notebook.sh, lancer_tout.sh
|   |-- schema_spec_tpcxbb.json        noms et types des colonnes (DDL de la spec)
|-- data/silver, data/gold, data/parquet
|-- preuves/ environnement, exploration, transformations, silver_gold, parquet, qualite
|-- docker/Dockerfile, outils/, sources_md/
```

## Reproduire

Prérequis : Docker Desktop, et le dossier du kit (celui qui contient `customer/`, `customer_address/`, `date_dim/`, `household_demographics/`, `income_band/`, `inventory/`). Les données ne sont pas dans le dépôt.

```
cd docker && docker build -t j3-pyspark .          # image Python + Java + PySpark
cd ..
export RAW_HOST=<chemin du kit>                    # monté en lecture seule dans le conteneur
bash scripts/lancer_tout.sh                        # environ 8 minutes
```

Ordre d'exécution : `verification_env.py` → `nettoyage.py` → `transformations.py` → `comparaison_formats.py` → `controles_qualite.py` → `zones.py` → notebook. Chaque script écrit son journal dans `preuves/`. Le PDF se régénère avec `python outils/build_pdf.py` (Selenium et Edge).

Paramètres : `RAW_DIR` (défaut `/data/raw`), `DATA_DIR` (défaut `/work/data`), `PREUVES_DIR` (défaut `/work/preuves`).

## Sorties

`data/silver/<table>/` (Parquet), `data/silver/_rejets/` (lignes écartées), `data/gold/<jeu>/` (Parquet), `data/parquet/` (comparaison de formats). Non versionnés car volumineux et régénérables : `data/silver/inventory` (111 Mo) et les copies CSV et JSON de `data/parquet`.

## Limites connues

- Zip tronqué : 7 tables, `inventory` coupé en cours de fichier (dernière date exclue du Gold).
- Données synthétiques : répartitions quasi uniformes, pas d'interprétation métier.
- Un contrôle « OK » prouve la cohérence interne, pas l'exactitude métier.
