# UC-08 – Analyse des données, KPI et visualisation

TP Jour 4 – Retail Intelligence Platform – Mastère Développement, Data & IA – IPSSI – Mohammed Mosleh. Exécuté le 19/11/2026. Notebook : `notebooks/analyses_kpi.ipynb`.

## Ce qui est exploitable et ce qui ne l'est pas

Le zip reçu au Jour 1 est tronqué : il ne contient que 7 tables (clients, adresses, foyers, tranches de revenu, calendrier, une partie de l'inventaire). **Aucune table de ventes, de retours, d'articles ni de magasins.** Les KPI de ventes (KPI-01 à KPI-07) ne sont donc pas calculables, et les graphiques d'exemple du TP (`ventes_par_magasin`, `evolution_ventes_mensuelles`) n'ont pas pu être produits. Les analyses portent sur les trois KPI calculables avec les jeux Silver et Gold du Jour 3 : KPI-08 (stock moyen), KPI-09 (nombre de clients) et KPI-10 (clients par tranche de revenu). Toutes les données sont synthétiques (TPCx-BB).

## Environnement de référence

| Élément | Version / choix |
|---|---|
| Python | 3.12.14 |
| PySpark | 4.3.0, mode `local[4]`, 4 Go de mémoire pour le driver |
| Java | OpenJDK 21.0.13 |
| pandas / Matplotlib | pandas < 3 (version relevée dans le notebook), Matplotlib (version relevée dans le notebook) |
| Exécution | conteneur Docker `j4-analytics` (image du Jour 3 + pandas + Matplotlib), notebook exécuté sans interface avec `jupyter nbconvert --execute` |
| Données lues | Parquet Silver et Gold du Jour 3 (`Jour3/data`, montés en lecture seule) |

L'environnement du TP3 (image `j3-pyspark`) est réutilisé : seuls pandas et Matplotlib sont ajoutés (`docker/Dockerfile`). JupyterLab n'a pas été ouvert dans un navigateur : le notebook est exécuté en ligne de commande, ses sorties sont enregistrées dans le fichier `.ipynb`. Les versions exactes sont affichées en tête du notebook exécuté.
