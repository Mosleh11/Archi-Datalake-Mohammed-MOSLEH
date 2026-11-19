# TP Jour 4 – UC-08 (analyse et visualisation) et UC-07 (transposition Azure)

Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh. Exécuté le 19/11/2026. Rapports : `UC08_analyses_visualisations.pdf` et `UC07_architecture_azure.pdf`.

## Ce qui a été fait

- **UC-08** : notebook PySpark + pandas + Matplotlib sur les jeux Silver et Gold du Jour 3. Trois KPI calculés (KPI-08 stock moyen, KPI-09 nombre de clients, KPI-10 clients par tranche de revenu), statistiques descriptives, trois analyses métier, quatre graphiques, constats et recommandations. Les KPI de ventes (KPI-01 à KPI-07) ne sont pas calculables : le zip reçu ne contient aucune table de ventes, de retours, d'articles ni de magasins.
- **UC-07** : **parcours B (local / open source)**. Aucune ressource Azure n'a été créée. L'architecture Azure (ADLS Gen2, HNS, Entra ID, RBAC, ACL, ADF, Synapse), l'organisation des zones et la matrice des droits sont une étude ; les commandes Azure sont écrites mais non exécutées. La seule réalisation concrète est l'arborescence `retail-intelligence/` créée en local avec 10 fichiers du projet vérifiés par SHA-256.

Non fait : Power BI, partie complémentaire (CO-01 à CO-05) et avancée (AV-01 à AV-04), déploiement MinIO / Iceberg / Trino / Airflow.

## Versions observées

Python 3.12.14, PySpark 4.3.0, Java OpenJDK 21.0.13, pandas 2.3.3, Matplotlib 3.11.2, Spark en mode `local[4]` dans un conteneur Docker (`docker/Dockerfile`, basé sur l'image du Jour 3). Relevé dans `preuves/environnement/versions.txt`.

## Livrables (organisation de Livrables_Jour_4, option 1)

| Livrable | Où |
|---|---|
| Rapport UC-08 : jeux utilisés, KPI, statistiques, analyses, visualisations, constats | `UC08_analyses_visualisations.pdf` |
| Rapport UC-07 : parcours, Azure, ADLS Gen2, HNS, sécurité, ADF / Synapse, comparaison Azure / open source | `UC07_architecture_azure.pdf` |
| Notebook et script d'analyse | `notebooks/analyses_kpi.ipynb`, `scripts/analyses.py` |
| Visualisations | `visualisations/*.png` (4 graphiques, noms descriptifs) |
| Schéma d'architecture | `architecture/schema_architecture.png` (Azure) et `parcours_b_local.png` (ce qui a tourné) |
| Organisation ADLS Gen2 | `architecture/organisation_adls.md` |
| Matrice des rôles et permissions | `architecture/matrice_permissions.pdf` |
| Preuves UC-08 | `preuves/uc08/` |
| Preuves UC-07 (locales et simulation, **aucune capture Azure**) | `preuves/uc07/` |

## Contenu

```
Jour4/
|-- README.md, UC08_analyses_visualisations.pdf, UC07_architecture_azure.pdf
|-- notebooks/analyses_kpi.ipynb                notebook exécuté (sorties incluses)
|-- scripts/ analyses.py, lancer_notebook.sh, lancer_analyses.sh, uc07_arborescence_locale.py
|-- visualisations/                             4 graphiques PNG
|-- architecture/                               schémas (.dot .png .svg), organisation_adls.md, matrice_permissions.pdf
|-- preuves/uc08/                               environnement, notebook HTML, resultats (CSV)
|-- preuves/uc07/                               lake_local, manifeste SHA-256, journal, simulation_commandes
|-- docker/Dockerfile, outils/ (creer_notebook.py, build_pdf.py), sources_md/
```

## Reproduire

Prérequis : Docker Desktop, et les données du Jour 3 déjà produites dans `Jour3/data` (`bash Jour3/scripts/lancer_tout.sh`, environ 8 minutes, voir `Jour3/README.md`). `Jour3/data/silver/inventory` n'est pas dans le dépôt et doit être régénéré.

```
cd Jour4/docker && docker build -t j3-pyspark ../../Jour3/docker   # si l'image du Jour 3 n'existe pas
docker build -t j4-analytics .
cd .. && bash scripts/lancer_notebook.sh        # exécute le notebook, écrit preuves/uc08/resultats/ et visualisations/
python scripts/uc07_arborescence_locale.py <dossier du kit contenant customer/customer.dat>
(cd outils && python creer_notebook.py)         # régénère le notebook (vide) et scripts/analyses.py
python outils/build_pdf.py                      # PDF (Selenium et Edge)
```

Les schémas de `architecture/` se régénèrent avec Graphviz : `dot -Tpng schema_architecture.dot -o schema_architecture.png`.

## Limites connues

- Zip tronqué : 7 KPI sur 10 non calculables ; `inventory` coupé en cours de fichier (dernière date exclue).
- Données synthétiques : répartitions quasi uniformes, aucune conclusion métier réelle ; pas de test statistique.
- Notebook exécuté sans interface JupyterLab (`nbconvert --execute`).
- Azure : étude et simulation uniquement, rien n'a été déployé.
