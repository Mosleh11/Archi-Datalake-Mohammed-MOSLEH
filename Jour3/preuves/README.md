# Preuves Jour 3

Toutes les sorties viennent de l'exécution réelle du 18/11/2026 (`scripts/lancer_tout.sh`). Pas de captures d'écran : les preuves sont les sorties des scripts et le notebook exécuté.

| Dossier / fichier | Ce qu'il démontre |
|---|---|
| `environnement/verification_env.txt` | Versions Python 3.12.14, PySpark 4.3.0, Java 21, mode `local[4]`, lecture d'un fichier de test, schéma, écriture et relecture d'un résultat de test |
| `exploration/exploration.html` | Notebook d'exploration exécuté (version lisible) : schémas, échantillons, volumes, valeurs manquantes, doublons, min/max des 6 sources |
| `transformations/nettoyage_log.txt`, `nettoyage_stats.json` | Application des règles de nettoyage : lignes brutes, Silver, rejetées, échecs de conversion, compteurs par règle |
| `transformations/transformations_log.txt`, `jointures.json` | Jointures vérifiées (unicité de la clé, lignes avant et après, orphelins) et résultats des agrégations Gold |
| `silver_gold/zones_silver_gold.txt` | Jeux Silver et Gold réellement produits : fichiers Parquet, taille, lignes, schéma, échantillon, lignes rejetées |
| `silver_gold/gold_*.csv` | Les trois jeux Gold en CSV pour les lire directement (agrégation métier) |
| `parquet/comparaison_formats_log.txt`, `comparaison_formats.json` | Écriture et relecture Parquet (schéma identique, 0 ligne différente) et comparaison CSV / JSON / Parquet |
| `qualite/controles_qualite_log.txt`, `controles_qualite.json` | Résultat des 49 contrôles qualité et de l'anomalie restante |
