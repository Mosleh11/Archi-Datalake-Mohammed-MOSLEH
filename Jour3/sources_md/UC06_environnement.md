# UC-06 – Fiche d'environnement technique

Relevé du 18/11/2026 avec `scripts/verification_env.py` (sortie complète : `preuves/environnement/verification_env.txt`).

| Élément | Valeur observée |
|---|---|
| Poste | Windows 11, Docker Desktop (moteur WSL2) |
| Environnement d'exécution | conteneur `j3-pyspark` construit par `docker/Dockerfile` (Python 3.12 slim) |
| Python | 3.12.14 |
| PySpark / Spark | 4.3.0 (installé avec `pip`, Spark embarqué) |
| Java | OpenJDK 21.0.13 |
| Mode d'exécution | **local** : `local[4]`, mémoire du driver 4 Go, 8 partitions de shuffle. Pas de cluster |
| Ressources vues par le conteneur | 20 CPU visibles, 7,5 Go de mémoire pour Docker |
| Notebook | `jupyter nbconvert` (exécution du notebook en ligne de commande) |
| Données brutes | `/data/raw` dans le conteneur = dossier du kit sur le poste, monté en **lecture seule** |
| Sorties | `/work/data/{silver,gold,parquet}` = `Jour3/data/` ; preuves : `/work/preuves` = `Jour3/preuves/` |

## Vérifications de l'étape 1

Session Spark initialisée ; lecture de `income_band.dat` (20 lignes), affichage du schéma, écriture d'un résultat de test en Parquet dans `data/_test/` (dossier distinct, supprimé ensuite) puis relecture : 20 lignes. Les données sources n'ont pas été modifiées.

## Choix et écarts avec le TP

- Le TP décrit une installation Ubuntu avec un environnement virtuel Python. J'ai utilisé une image Docker : même contenu (Python, PySpark, Java), mais reproductible avec une seule commande.
- **Cas 1 du TP (fichiers sur l'ordinateur)** : les 7 fichiers du kit sont lus depuis le disque du poste, pas depuis HDFS. Les données déposées dans HDFS au Jour 2 n'ont pas été conservées (conteneurs supprimés, pas de volume) et ne contenaient que 2 fichiers. La lecture depuis HDFS n'a pas été faite.
- Spark 4 refuse par défaut une conversion de texte vers nombre qui échoue (mode ANSI). J'ai mis `spark.sql.ansi.enabled=false` pour obtenir un `null` à la place, puis je **compte** ces échecs (0 observé).
- Je n'ai pas lancé de cluster ni de Spark UI : aucune capture de la Spark UI.
- Source : jeu synthétique TPCx-BB, 7 tables seulement (zip tronqué, voir Jour 1). Aucun score de benchmark n'est revendiqué.

