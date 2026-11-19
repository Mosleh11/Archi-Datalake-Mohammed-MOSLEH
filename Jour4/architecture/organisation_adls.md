# J4-08 – Organisation ADLS Gen2

## Arborescence proposée

Un compte de stockage dédié, un conteneur `retail-intelligence` :

```
retail-intelligence/
|-- bronze/
|   |-- tpcxbb/<table>/ingest_date=AAAA-MM-JJ/      fichiers .dat tels que reçus
|   `-- complements/                                 données hors TPCx-BB (aucune ici)
|-- silver/<table>/                                  Parquet nettoyé et typé
|-- gold/
|   |-- indicateurs/<jeu>/                           KPI agrégés (Parquet)
|   `-- analyses/                                    tableaux CSV des analyses (kpi.csv, statistiques.csv)
|-- quality/<traitement>/                            rapports de contrôles (JSON)
`-- documentation/                                   dictionnaires de données et de KPI
```

Cette organisation est celle réellement matérialisée en local (arborescence dans `preuves/uc07/arborescence_lake_local.txt`) ; elle reprend les mêmes noms que les jeux produits au Jour 3.

## Rôle de chaque zone

| Zone | Fonction | Données déposées | Qui y accède | Nommage | Conservation et traçabilité |
|---|---|---|---|---|---|
| `bronze/` | conserver les sources telles que reçues | `.dat` du kit TPCx-BB | ingestion (écriture), data engineering (lecture) | `bronze/tpcxbb/<table>/ingest_date=AAAA-MM-JJ/` | jamais modifiée ; date d'ingestion dans le chemin ; somme de contrôle SHA-256 gardée (comme au Jour 2) |
| `silver/` | données nettoyées, typées, jointes | Parquet par table, avec colonnes `_source` et `_traite_le` | data engineering (écriture), analystes (lecture si besoin) | `silver/<table>/` en minuscules, snake_case | lignes rejetées conservées à part (`_rejets`), reproductible depuis bronze |
| `gold/` | données prêtes pour le métier | agrégats Parquet par KPI ; tableaux CSV d'analyse | data engineering (écriture contrôlée), analystes (lecture) | `gold/indicateurs/<kpi_ou_sujet>/` | version du script et date de calcul dans `quality/` |
| `quality/` | résultats des contrôles | JSON des 49 contrôles du Jour 3 | data engineering | `quality/<traitement>/` | gardés à chaque exécution |
| `documentation/` | explications des données | dictionnaires | tous (lecture) | nom explicite | versionnée avec le code |

## Hierarchical Namespace (HNS)

Le HNS est une option du compte de stockage, **à choisir à la création** du compte (le choix doit être vérifié avant de créer la ressource). Sans HNS, un compte Blob a un espace de noms « à plat » : les « dossiers » ne sont que des préfixes dans le nom des fichiers. Avec HNS, les répertoires existent réellement.

| Point | Avec HNS (ADLS Gen2) | Sans HNS (Blob à plat) |
|---|---|---|
| Organisation | arborescence réelle de répertoires et de fichiers | préfixes dans les noms |
| Renommer ou supprimer un répertoire | une seule opération sur le répertoire | une opération par fichier (copie puis suppression) |
| Permissions | ACL sur les répertoires et les fichiers | pas d'ACL par répertoire |
| Usages analytiques | adapté aux moteurs comme Spark (écriture de dossiers de fichiers, renommage à la validation) | possible, moins adapté |
| Accès | API et point d'accès « dfs » en plus de l'API Blob | API Blob |

Intérêt pour ce projet : renommer ou supprimer un jeu Silver ou Gold entier (un dossier de fichiers Parquet, comme ceux écrits par Spark) en une opération, et donner à l'équipe métier un droit de lecture sur `gold/` seulement. **HNS ne transforme pas Parquet en table transactionnelle** : cela reste de simples fichiers.

## Mise en œuvre locale réelle

`scripts/uc07_arborescence_locale.py` crée l'arborescence ci-dessus sur le disque, y dépose 10 fichiers du projet (échantillon de 200 lignes de `customer.dat` en bronze, deux tables Silver, les trois jeux Gold, les tableaux d'analyse, le rapport de qualité du Jour 3, le dictionnaire des KPI), puis relit chaque fichier à partir du manifeste (`preuves/uc07/manifeste_lake_local.json`) et compare taille et SHA-256 : **10 fichiers déposés, 10 vérifiés, 0 écart**. C'est l'équivalent local des étapes « déposer un fichier » et « vérifier qu'il est accessible » du TP ; ce n'est pas un dépôt Azure.
