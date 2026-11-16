# TP J1 – Retail Intelligence Platform

Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh
Use cases traités : **UC-01** (besoin métier et exploration) et **UC-02** (architecture Data).

## Point important sur les données

Le fichier `retail_project.zip` donné par le formateur est **tronqué** (pas de fin d'archive). Je n'ai pu récupérer que 7 tables : `customer`, `customer_address`, `customer_demographics`, `date_dim`, `household_demographics`, `income_band` et `inventory` (ce dernier est coupé en cours de fichier). Les tables de ventes, de retours, `item`, `store`, la navigation web, etc. ne sont pas dans le zip.

Conséquence : l'inventaire et la qualification portent sur ces 7 tables (mesurés), et les KPI de ventes sont définis mais marqués **non calculables / non vérifié**. Les tables absentes sont listées dans `inventaire_sources.xlsx` (feuille « Absents du zip »). Rien n'a été inventé. Il faudrait redemander le zip complet au formateur.

Les noms de colonnes viennent du DDL de la spec TPCx-BB v1.7.0, car les `.dat` n'ont pas d'en-tête.

## Contenu

```
J1_Retail_Intelligence/
|-- README.md
|-- 01_UC01_besoin_exploration/
|   |-- cadrage_metier.pdf
|   |-- questions_decisionnelles.pdf
|   |-- dictionnaire_KPI.xlsx
|   |-- inventaire_sources.xlsx
|   |-- qualification_donnees.pdf
|   |-- limites_hypotheses.pdf
|   |-- preuves/        scripts, résultats, aperçus, arborescence
|-- 02_UC02_architecture/
|   |-- comparaison_architectures.pdf
|   |-- architecture_cible.pdf
|   |-- schema_flux.pdf
|   |-- positionnement_composants.pdf
|   |-- gouvernance.pdf
|   |-- local_vers_azure.pdf
|   |-- preuves/        schémas (SVG) et fiche de preuves
|-- sources_md/         textes d'origine des PDF (Markdown) et schémas
|-- outils/             scripts qui génèrent les PDF, Excel et schémas
```

Pas de dossiers `03_complementaire`, `04_avance` ni `05_contribution_individuelle` : travail individuel, activités facultatives non faites.

## Refaire les mesures

```
python 01_UC01_besoin_exploration/preuves/recuperation_zip.py <chemin>/retail_project.zip data_extraite
python 01_UC01_besoin_exploration/preuves/analyse_kit.py data_extraite/retail_project/data 01_UC01_besoin_exploration/preuves
python 01_UC01_besoin_exploration/preuves/controles_simples.py data_extraite/retail_project/data
```

Si on reçoit le kit complet, relancer `analyse_kit.py` (il lit le schéma dans `preuves/schema_spec_tpcxbb.json`), puis `python outils/build_xlsx.py` et `python outils/build_pdf.py` après avoir mis à jour les textes.

## Ce qui n'est pas fait

- Pas de déploiement (Hadoop, NiFi, Spark, Azure) : UC-02 est de la conception.
- KPI de ventes, retours et remises : définis, pas calculés.
- Projet fil rouge : non traité pour l'instant.
