# UC-03 – Inventaire des fichiers TPCx-BB utilisés

Les fichiers viennent de `retail_project.zip`, qui est tronqué (voir Jour 1) : 7 tables sur la vingtaine attendue ont été récupérées. Je n'en ai déposé que 2 dans HDFS. Aucun fichier n'a été créé ni modifié.

| Fichier | Format | Taille (octets) | Lignes | Colonnes | Provenance | Observations |
|---|---|---|---|---|---|---|
| `household_demographics.dat` | texte, séparateur `\|`, sans en-tête | 155 100 | 7 200 | 5 | `retail_project.zip` du formateur (jeu TPCx-BB synthétique) | Utilisé pour UC-03 (`hdfs dfs -put`) et UC-04 (NiFi). Colonnes d'après le DDL de la spec : `hd_demo_sk`, `hd_income_band_sk`, `hd_buy_potential`, `hd_dep_count`, `hd_vehicle_count`. `hd_vehicle_count` vaut -1 pour 282 lignes (voir Jour 1) |
| `date_dim.dat` | texte, séparateur `\|`, sans en-tête | 15 395 800 | 109 573 | 28 | idem | Utilisé pour UC-03. Calendrier de 1900 à 2199 (d'après Jour 1), plus de lignes que les 73 049 écrites dans la spec |

Empreintes SHA-256 (identiques sur le disque du poste, dans le conteneur, et après relecture depuis HDFS) :

- `household_demographics.dat` : `915aa15ea23e2beee3fa13bee3a94ae8ed5b0d170ea97e25ff81f79417fdfaf7`
- `date_dim.dat` : `325c892265c040d6c85491d708e4e081d1bf8532f949b3a18b14ba6e73a456af`

Fichiers non déposés (non demandés pour le socle) : `customer`, `customer_address`, `customer_demographics`, `income_band` et `inventory` (tronqué). Les tables de ventes, retours, produits, magasins, etc. ne sont pas dans le zip.
Les types et valeurs vides de ces deux tables sont dans `Jour1/UC01_preuves/` (`resultats_analyse.json`, `inventaire_sources.xlsx`).
