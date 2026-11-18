#!/bin/bash
# ordre d'execution complet ; RAW_HOST = dossier contenant customer/, customer_address/, date_dim/, household_demographics/, income_band/, inventory/
cd "$(dirname "$0")" || exit 1
bash lancer.sh verification_env.py preuves/environnement/verification_env.txt
bash lancer.sh nettoyage.py preuves/transformations/nettoyage_log.txt
bash lancer.sh transformations.py preuves/transformations/transformations_log.txt
bash lancer.sh comparaison_formats.py preuves/parquet/comparaison_formats_log.txt
bash lancer.sh controles_qualite.py preuves/qualite/controles_qualite_log.txt
bash lancer.sh zones.py preuves/silver_gold/zones_silver_gold.txt
bash lancer_notebook.sh
