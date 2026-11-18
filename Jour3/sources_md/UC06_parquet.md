# UC-06 – Format Parquet : écriture, relecture, comparaison

`scripts/comparaison_formats.py` (log : `preuves/parquet/comparaison_formats_log.txt`, mesures : `comparaison_formats.json`). Le jeu `silver/clients_enrichis` (99 000 lignes, 25 colonnes) est écrit en CSV, JSON et Parquet dans des dossiers séparés (`data/parquet/`), puis relu.

## Écriture et relecture Parquet

- Écriture : `df.write.mode("overwrite").parquet(...)` sur un dossier réservé au TP (jamais sur les sources).
- Relecture : `spark.read.parquet(...)` → {{PARQUET_RELECTURE}}

## Comparaison des formats

{{TABLE_FORMATS}}

| Critère | CSV | JSON | Parquet |
|---|---|---|---|
| Organisation | lignes de texte, colonnes séparées | un objet par ligne, nom des champs répété | colonnes stockées ensemble, métadonnées et schéma dans le fichier |
| Lisibilité | lisible par un humain et par tout éditeur | lisible, très verbeux | binaire : pas lisible sans outil |
| Gestion des types | aucun : tout est du texte, sauf `inferSchema` qui **devine** (et peut se tromper) | types simples (nombres, chaînes) mais pas de date ni de décimal précis | types explicites conservés (entiers, décimaux, dates, horodatages) |
| Volume observé | voir tableau | le plus volumineux (noms de champs répétés) | le plus petit (compression par colonne) |
| Usages adaptés | échange simple, petits fichiers, import | échanges entre applications, données imbriquées | analyse, agrégations, lecture de quelques colonnes |
| Avantages | universel, simple | souple, semi-structuré | compact, rapide à agréger, schéma fiable |
| Limites | pas de types, lent et gros | gros, lent | pas lisible directement, pas fait pour modifier une ligne |

Point d'attention : **Parquet seul n'est pas une table transactionnelle**. Il ne fournit ni transactions ACID, ni mises à jour ligne par ligne, ni historique des versions : ce sont les formats de table Lakehouse (Delta Lake, Iceberg, Hudi) qui les ajoutent. Les jeux Silver et Gold produits ici sont de simples fichiers Parquet. Les temps sont mesurés en mode local sur un petit jeu (99 000 lignes) : l'écart de temps est indicatif, pas un résultat de performance.
