# TP J1 – Retail Intelligence Platform

Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh
Use cases traités : **UC-01** (besoin métier et exploration) et **UC-02** (architecture Data).

## Point important sur les données

`retail_project.zip` est **tronqué**. Seules 7 tables sont récupérables : `customer`, `customer_address`, `customer_demographics`, `date_dim`, `household_demographics`, `income_band` et `inventory` (coupée en cours de fichier). Les ventes, retours, `item`, `store`, etc. sont absents.

Les KPI de ventes sont donc définis mais **non calculables**. Tables absentes : feuille « Absents du zip » de `UC01_preuves/inventaire_sources.xlsx`.

Les noms de colonnes viennent du DDL de la spec TPCx-BB v1.7.0, car les `.dat` n'ont pas d'en-tête.

## Contenu

```
Jour1/
|-- README.md
|-- UC01_besoin_donnees.pdf    besoin métier, KPI, sources, qualité, limites
|-- UC01_preuves/              scripts, résultats, xlsx (voir README.md du dossier)
|-- UC02_architecture.pdf      comparaison, architecture, flux, composants, gouvernance, Azure
|-- UC02_preuves/              schémas SVG (voir README.md du dossier)
|-- sources_md/                textes d'origine des PDF (Markdown) et schémas
|-- outils/                    scripts qui génèrent les PDF, Excel et schémas
```

Rendu au format « plusieurs fichiers » de la consigne. Pas de captures UC-02 : rien n'a été installé.

## Refaire les mesures

```
python UC01_preuves/recuperation_zip.py <chemin>/retail_project.zip data_extraite
python UC01_preuves/analyse_kit.py data_extraite/retail_project/data UC01_preuves
python UC01_preuves/controles_simples.py data_extraite/retail_project/data
```

Si on reçoit le kit complet, relancer `analyse_kit.py` (il lit le schéma dans `UC01_preuves/schema_spec_tpcxbb.json`), puis `python outils/build_xlsx.py` et `python outils/build_pdf.py` après avoir mis à jour les textes.

## Ce qui n'est pas fait

- Pas de déploiement (Hadoop, NiFi, Spark, Azure) : UC-02 est de la conception.
- KPI de ventes, retours et remises : définis, pas calculés.
- Projet fil rouge : non traité pour l'instant.
